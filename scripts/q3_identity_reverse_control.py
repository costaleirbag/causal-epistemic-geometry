#!/usr/bin/env python3
"""One bounded engineering control; reuses the frozen backend, parser and journal."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'scripts')]
REVIEW = ROOT / 'review/q3_identity_reverse_control'
KEYS = ('family_id', 'condition', 'rollout_index')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def prepare():
    texts = ['maple', 'b7K2', 'cobalt', 'raven9', 'tulip4', 'q3Z8m']
    assert len(set(texts + [x[::-1] for x in texts])) == 12
    fixtures, references, schedule = [], {}, []
    for i, text in enumerate(texts):
        data = {'n': 7, 'values': [2, 5, 8], 'text': text}
        for condition, expression in [('IDENTITY', 'data["text"]'), ('REVERSE', 'data["text"][::-1]')]:
            fixture_id = f'ENGINEERING-IR-{i:02d}-{condition}'
            source = f'def solve(data):\n    return {expression}\n'
            scope = {}
            exec(source, {'__builtins__': {}}, scope)  # fixed synthetic code only
            reference = text if condition == 'IDENTITY' else ''.join(reversed(text))
            assert scope['solve'](data) == reference
            prompt = ('Predict the exact output of this deterministic Python function.\n\n'
                      f'```python\n{source}```\n\nInput: {repr(data)}\n\n'
                      'Return exactly one final line in this form:\n'
                      'FINAL: <the exact Python output>\nDo not add any text after FINAL.')
            fixtures.append({'fixture_id': fixture_id, 'pair_id': i, 'condition': condition,
                             'input': data, 'source': source, 'prompt': prompt,
                             'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest()})
            references[fixture_id] = repr(reference)
        for rollout in (0, 1):
            seed = int.from_bytes(hashlib.sha256(f'Q3-ENGINEERING-IR-20260909:{i}:{rollout}'.encode()).digest()[:4], 'big') % (2**31 - 1)
            # Same seed across conditions within each pair; distinct across input/rollout.
            for condition in (('IDENTITY', 'REVERSE') if (i + rollout) % 2 == 0 else ('REVERSE', 'IDENTITY')):
                schedule.append({'family_id': f'ENGINEERING-IR-{i:02d}-{condition}',
                                 'condition': condition, 'rollout_index': rollout, 'pair_id': i, 'seed': seed})
    assert len(schedule) == 24 and len({r['seed'] for r in schedule}) == 12
    previous = json.loads((ROOT / 'review/q3_fresh_unsteered_diagnostic/Q3_FRESH_UNSTEERED_DIAGNOSTIC_PRECHECK.json').read_text())
    dependencies = ['scripts/q3_identity_reverse_control.py', 'scripts/execute_q3_fresh_qualification.py',
                    'scripts/analyze_q3_fresh_unsteered_diagnostic.py', 'scripts/run_q2_oos_v2_semantic.py',
                    'src/epistemic_geometry/research/durable_journal.py',
                    'src/epistemic_geometry/benchmarks/external/semantic_v3.py',
                    'src/epistemic_geometry/benchmarks/prompts.py',
                    'src/epistemic_geometry/backends/huggingface.py']
    write(REVIEW / 'REFERENCES.json', references)
    write(REVIEW / 'MANIFEST.json', {
        'status': 'FROZEN_ENGINEERING_CONTROL_BEFORE_INFERENCE', 'fixtures': fixtures,
        'schedule': schedule, 'model': previous['model'], 'generation': previous['generation'],
        'source_hashes': {p: sha(ROOT / p) for p in dependencies},
        'references_sha256': sha(REVIEW / 'REFERENCES.json'),
        'permanently_excluded_from_all_scientific_evaluation': True,
        'primary': 'both conditions exactly correct per input and rollout; denominator 12 pairs',
        'interpretation': {'all_12_pairs_correct': 'elementary control passes on these six inputs only',
                           'otherwise': 'limited/mixed result; inspect only these fixtures, no tuning or additional generation'},
        'stop': '24 planned generations once; no automatic retry, no further panels; Q3 remains NOT_RUN',
        'scope': 'unsteered; no qualification/confirmation/reserve data; no router or steering hooks',
        'reference_isolation': 'collection reads prompts only; reference file is not loaded or passed to backend',
    })
    print('Prepared 12 synthetic fixtures and 24 scheduled generations; no model access.')


def verified_manifest():
    m = json.loads((REVIEW / 'MANIFEST.json').read_text())
    for p, digest in m['source_hashes'].items():
        assert sha(ROOT / p) == digest, p
    assert len(m['schedule']) == 24
    assert len({tuple(r[k] for k in KEYS) for r in m['schedule']}) == 24
    return m


def collect(directory, model_path):
    import execute_q3_fresh_qualification as frozen
    from run_q2_oos_v2_semantic import EXTREME_REPETITION_NAME, extreme_mechanical_repetition_v1, frozen_terminal_metadata
    from epistemic_geometry.research.durable_journal import SingleWriterJournal
    m = verified_manifest()
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).strip()
    assert not (directory / 'PREOPEN.json').exists(), 'No automatic restart or repeated panel'
    environment = frozen.verify_environment(model_path)
    identity = {'experiment': 'ENGINEERING_IDENTITY_REVERSE_ONLY',
                'manifest_sha256': sha(REVIEW / 'MANIFEST.json'),
                'code_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'environment': environment, 'steering': 'NONE'}
    write(directory / 'PREOPEN.json', identity)
    fixtures = {f['fixture_id']: f for f in m['fixtures']}
    with SingleWriterJournal(directory / 'journal.jsonl', identity=identity, key_fields=KEYS) as journal:
        assert not journal.rows
        backend = frozen.build_backend(model_path)
        for index, row in enumerate(m['schedule']):
            f = fixtures[row['family_id']]
            item = frozen.model_item(row['family_id'], f['prompt'])
            started = time.perf_counter()
            output = backend.generate_reasoning(item, sampling_seed=row['seed'], max_new_tokens=4096,
                                                token_stop_predicate=extreme_mechanical_repetition_v1,
                                                token_stop_name=EXTREME_REPETITION_NAME)
            elapsed = time.perf_counter() - started
            journal.append({**row, 'schedule_index': index, 'raw_output': output.raw_output,
                            'generated_token_ids': output.metadata['generated_token_ids'],
                            'rendered_prompt_hash': output.metadata['rendered_prompt_hash'],
                            **frozen_terminal_metadata(output), 'elapsed_seconds': elapsed,
                            'runtime_error': None})
            print(json.dumps({'completed': index + 1, 'expected': 24}), flush=True)
        journal.seal(directory / 'COLLECTION_COMPLETE_SEAL.json', m['schedule'], lambda rows: {
            'status': 'COLLECTION_COMPLETE_RAW_UNSCORED', 'correctness_inspected': False,
            'semantic_scoring': 'NOT_RUN', 'manifest_sha256': sha(REVIEW / 'MANIFEST.json'),
            'confirmation_qwen_access': 0, 'reserve_qwen_access': 0})


def score(directory):
    from analyze_q3_fresh_unsteered_diagnostic import classify, summary
    from epistemic_geometry.research.durable_journal import decode, snapshot
    m = verified_manifest()
    seal = json.loads((directory / 'COLLECTION_COMPLETE_SEAL.json').read_text())
    assert seal['status'] == 'COLLECTION_COMPLETE_RAW_UNSCORED' and seal['completed'] == seal['expected'] == 24
    assert seal['correctness_inspected'] is False and seal['semantic_scoring'] == 'NOT_RUN'
    assert seal['manifest_sha256'] == sha(REVIEW / 'MANIFEST.json')
    raw = snapshot(directory / 'journal.jsonl')
    assert hashlib.sha256(raw).hexdigest() == seal['journal_sha256'] and len(raw) == seal['journal_bytes']
    identity = json.loads((directory / 'PREOPEN.json').read_text())
    view = decode(raw, identity, KEYS)
    assert set(view.rows) == {tuple(r[k] for k in KEYS) for r in m['schedule']}
    assert sha(REVIEW / 'REFERENCES.json') == m['references_sha256']
    refs = json.loads((REVIEW / 'REFERENCES.json').read_text())
    rows = []
    for i, planned in enumerate(m['schedule']):
        r = view.rows[tuple(planned[k] for k in KEYS)]
        assert r['schedule_index'] == i and all(r[k] == v for k, v in planned.items())
        rows.append({**classify(r, refs[r['family_id']]), 'pair_id': planned['pair_id']})
    write(directory / 'SCORES.json', rows)
    pairs = []
    for i in range(6):
        for rollout in (0, 1):
            selected = [r for r in rows if r['pair_id'] == i and r['rollout_index'] == rollout]
            assert len(selected) == 2
            pairs.append({'pair_id': i, 'rollout_index': rollout, 'both_correct': all(r['correct'] for r in selected)})
    copied = 0
    for r in rows:
        if r['condition'] == 'REVERSE' and r['canonical_value'] is not None:
            f = next(f for f in m['fixtures'] if f['fixture_id'] == r['family_id'])
            copied += json.loads(r['canonical_value']) == ['str', f['input']['text']]
    passed = sum(p['both_correct'] for p in pairs)
    result = {'status': 'ELEMENTARY_CONTROL_PASS' if passed == 12 else 'ELEMENTARY_CONTROL_MIXED_OR_FAILED',
              'evidence': 'ENGINEERING_CONTROL_ONLY', 'conditions': {c: summary([r for r in rows if r['condition'] == c]) for c in ('IDENTITY', 'REVERSE')},
              'pairs_both_correct': passed, 'pairs_total': 12, 'inputs_total': 6,
              'inputs_all_four_correct': sum(all(p['both_correct'] for p in pairs if p['pair_id'] == i) for i in range(6)),
              'pairs_correct_by_rollout': {str(j): sum(p['both_correct'] for p in pairs if p['rollout_index'] == j) for j in (0, 1)},
              'reverse_returned_original_input': copied, 'planned_generations': 24,
              'terminal_counts': {t: sum(r['terminal_reason'] == t for r in rows) for t in sorted({r['terminal_reason'] for r in rows})},
              'raw_journal_sha256': seal['journal_sha256'], 'manifest_sha256': sha(REVIEW / 'MANIFEST.json'),
              'scores_sha256': sha(directory / 'SCORES.json'), 'collection_seal_sha256': sha(directory / 'COLLECTION_COMPLETE_SEAL.json'),
              'historical_status': 'Q3_FRESH_INSTRUMENT_NOT_QUALIFIED', 'q3_confirmatory': 'NOT_RUN',
              'confirmation_access': 0, 'reserve_access': 0, 'additional_panel_authorized': False}
    write(directory / 'RESULT.json', result)
    print(json.dumps(result))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['prepare', 'collect', 'score'])
    p.add_argument('--execution-dir', type=Path)
    p.add_argument('--model-path')
    a = p.parse_args()
    if a.mode == 'prepare':
        prepare()
    elif a.mode == 'collect':
        assert a.execution_dir and a.model_path
        collect(a.execution_dir, a.model_path)
    else:
        assert a.execution_dir
        score(a.execution_dir)
