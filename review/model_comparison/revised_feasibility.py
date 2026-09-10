"""Outcome-blind budget and input gate; no fitter, scorer, or historical writes."""
import hashlib
import json
from pathlib import Path
import numpy as np


def fit_plan(control_sensitivities=True):
    plan = []
    for orientation in range(3):
        for half in range(2):
            for model, starts in [('F', 1), ('R', 1), ('D', 2), ('I', 2), ('C', 2)]:
                for penalty in ([1] if model == 'F' else [1, .25, 4]):
                    for start in range(starts):
                        plan.append(('A', orientation, half, model, penalty, start))
        for held in range(12):
            for assignment in range(4):
                penalties = [1, .25, 4] if assignment == 0 or control_sensitivities else [1]
                for penalty in penalties:
                    for model, starts in [('G', 1), ('H', 2)]:
                        for start in range(starts):
                            plan.append(('B', orientation, held, assignment, model, penalty, start))
    return plan


def schedule_gate(rows):
    keys = [(r['item_id'], r['condition'], r['rollout_index']) for r in rows]
    if len(keys) != 17760 or len(set(keys)) != len(keys):
        raise ValueError('schedule coverage')
    if len({r['seed'] for r in rows}) != len(rows):
        raise ValueError('seed coupling requires supervisor redesign')
    families = {r['item_id'] for r in rows}
    conditions = {r['condition'] for r in rows}
    expected = {(f, c, r) for f in families for c in conditions for r in range(8)}
    if len(families) != 60 or len(conditions) != 37 or set(keys) != expected:
        raise ValueError('panel dimensions')
    return {'rows': len(rows), 'unique_seeds': len(rows), 'seed_overlap_any_disjoint_split': 0,
            'half_split_compatible': True, 'held_controller_split_compatible': True}


def inspect(directory, audit):
    directory = Path(directory)
    pinned = audit['input_hashes']
    names = ['PRIVATE_SCORES.json', 'vectors.npz', 'PREPARED.json', 'QUALIFICATION.json',
             'SELECTION_SEAL.json', 'DEPLOYMENT.json', 'EVALUATION_SCHEDULE.json',
             'EVALUATION_SEAL.json', 'evaluation.jsonl']
    hashes = {}
    for name in names:
        h = hashlib.sha256()
        with (directory / name).open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(block)
        hashes[name] = h.hexdigest()
        if hashes[name] != pinned[name]:
            raise ValueError('audited digest mismatch: ' + name)
    read = lambda name: json.loads((directory / name).read_text())
    prepared, selection, seal = [read(n) for n in ['PREPARED.json', 'SELECTION_SEAL.json', 'EVALUATION_SEAL.json']]
    assert prepared['vectors_sha256'] == hashes['vectors.npz']
    assert seal['journal_sha256'] == hashes['evaluation.jsonl']
    assert seal['protocol_sha256'] == pinned['precheck']
    assert selection['schedule_sha256'] == seal['schedule_sha256'] == hashes['EVALUATION_SCHEDULE.json']
    assert selection['deployment_sha256'] == seal['deployment_sha256'] == hashes['DEPLOYMENT.json']
    assert selection['qualification_sha256'] == hashes['QUALIFICATION.json']
    schedule = schedule_gate(read('EVALUATION_SCHEDULE.json'))
    keep = read('QUALIFICATION.json')['common_safe_indices']
    assert len(keep) == len(set(keep)) == 12
    with np.load(directory / 'vectors.npz', allow_pickle=False) as archive:
        c = archive['coefficients'][keep]
    assert c.shape == (12, 8) and np.isfinite(c).all()
    assert np.allclose(np.linalg.norm(c, axis=1), 1, atol=1e-10)
    ranks = [int(np.linalg.matrix_rank(np.delete(c, k, 0) - np.delete(c, k, 0).mean(0))) for k in range(12)]
    return {'passed': True, 'audited_input_hashes_verified': hashes, 'schedule': schedule,
            'coefficient_shape': list(c.shape), 'training_centered_ranks': ranks,
            'outcomes_parsed': False, 'historical_files_written': False}

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('directory')
    p.add_argument('audit')
    args = p.parse_args()
    print(json.dumps(inspect(args.directory, json.loads(Path(args.audit).read_text())), indent=2))
