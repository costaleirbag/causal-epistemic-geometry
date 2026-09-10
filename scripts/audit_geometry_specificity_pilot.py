"""Independent CPU audit. Private inputs stay at execution site; stdout is aggregate only.

No primary estimator, rank, qualification, or summary functions are imported.
The frozen semantic parser is shared solely to verify persisted scores. NumPy RNG
and quantile are shared numerical primitives, with the frozen seed and 2000 draws.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

SPACES = ('ORIGINAL', 'RANDOM_1', 'RANDOM_2')
SEED = 2026090937


def ranks(x):
    x = np.asarray(x)
    order = np.argsort(x, kind='stable')
    out = np.empty(len(x), float)
    start = 0
    while start < len(x):
        end = start + 1
        while end < len(x) and x[order[end]] == x[order[start]]:
            end += 1
        out[order[start:end]] = (start + end - 1) / 2
        start = end
    return out


def distances(y):
    """Center each controller over families; sum explicit distinct-rollout Grams."""
    y = np.asarray(y, float)
    if y.ndim != 3 or y.shape[2] < 2:
        raise ValueError('need two rollouts')
    z = y - y.mean(axis=0, keepdims=True)
    gram = np.zeros((y.shape[1], y.shape[1]))
    for r in range(y.shape[2]):
        for s in range(y.shape[2]):
            if r != s:
                gram += z[:, :, r].T @ z[:, :, s]
    gram /= y.shape[0] * y.shape[2] * (y.shape[2] - 1)
    return np.diag(gram)[:, None] + np.diag(gram)[None, :] - gram - gram.T


def correlation(y, c):
    ix = np.triu_indices(len(c), 1)
    a, b = (1 - c @ c.T)[ix], distances(y)[ix]
    if np.std(a) < 1e-15 or np.std(b) < 1e-15:
        return None
    a, b = ranks(a), ranks(b)
    a -= a.mean()
    b -= b.mean()
    return float(a @ b / np.sqrt((a @ a) * (b @ b)))


def exact_correlation(y, c):
    """Diagnostic for binary Y: exact centered cross-product integer numerators."""
    a = np.asarray(y, dtype=np.int64)
    n, k, r = a.shape
    gram = np.zeros((k,k), dtype=np.int64)
    for u in range(r):
        for v in range(r):
            if u != v:
                gram += n * (a[:,:,u].T @ a[:,:,v]) - np.outer(a[:,:,u].sum(axis=0), a[:,:,v].sum(axis=0))
    d = np.diag(gram)[:,None] + np.diag(gram)[None,:] - gram - gram.T
    ix = np.triu_indices(k,1)
    x, z = ranks((1-c@c.T)[ix]), ranks(d[ix])
    x -= x.mean()
    z -= z.mean()
    return float(x@z / np.sqrt((x@x)*(z@z))) if z@z else None


def classify(rho, interval):
    if interval[0] > .15:
        return 'OBSERVABLE_ALIGNMENT_HIGHER_FOR_ORIGINAL'
    if interval[0] > -.15 and interval[1] < .15 and min(rho) > .30:
        return 'COMPARABLE_RELATIONAL_ALIGNMENT_IN_TESTED_ORIENTATIONS'
    return 'INCONCLUSIVE_SPECIFICITY_CONTRAST'


def calculate(y, c, draws=2000):
    rho = [correlation(a, c) for a in y]
    result = dict(associations=rho, accuracy=y.mean(axis=(1, 2, 3)).tolist(),
                  mean_pair_displacement=[float(distances(a)[np.triu_indices(len(c), 1)].mean()) for a in y])
    if None in rho:
        return dict(result, contrast=None, classification='INCONCLUSIVE_DEGENERATE_RESPONSE')
    result['contrast'] = rho[0] - .5 * (rho[1] + rho[2])
    rng = np.random.default_rng(SEED)
    boot = []
    for _ in range(draws):
        sample = rng.integers(0, y.shape[1], y.shape[1])
        r = [correlation(a[sample], c) for a in y]
        if None not in r:
            boot.append(r[0] - .5 * (r[1] + r[2]))
    if len(boot) < .95 * draws:
        return dict(result, classification='INCONCLUSIVE_BOOTSTRAP_DEGENERACY')
    ci = np.quantile(boot, [.025, .975]).tolist()
    result.update(paired_family_bootstrap_q025_q975=ci, bootstrap_valid_draws=len(boot),
                  classification=classify(rho, ci), margin=.15)
    rep = []
    for a in y:
        z = a - a.mean(axis=0, keepdims=True)
        z -= z.mean(axis=1, keepdims=True)
        products = [float(np.mean(z[:, :, r] * z[:, :, s]))
                    for r in range(a.shape[2]) for s in range(a.shape[2]) if r != s]
        stable, energy = float(np.mean(products)), float(np.mean(z*z))
        rep.append(dict(stable_product=stable, observed_energy=energy, ratio=stable/energy if energy else None))
    result['response_reproducibility'] = rep
    result['rollout_half_associations'] = [[correlation(a[:, :, :4], c), correlation(a[:, :, 4:], c)] for a in y]
    return result


def qualify(rows, deployment, c):
    baseline = {(r['item_id'], r['rollout_index']): r for r in rows if r['condition'] == 'BASELINE'}
    bv = sum(r['commitment_valid'] for r in baseline.values()) / len(baseline)
    be = sum(r['semantic_evaluable'] for r in baseline.values()) / len(baseline)
    report = {}
    for space in SPACES:
        for k in range(24):
            name = f'{space}_{k:02}'
            group = [r for r in rows if r['condition'] == name]
            assert len(group) == 24
            v = sum(r['commitment_valid'] for r in group)/24
            e = sum(r['semantic_evaluable'] for r in group)/24
            t = sum(r['truncated'] for r in group)/24
            m = sum(r['generated_token_ids'] != baseline[r['item_id'], r['rollout_index']]['generated_token_ids'] for r in group)/24
            report[name] = dict(validity=v, evaluability=e, terminal_failure_rate=t, movement=m,
                                passed=v >= max(.9, bv-.05) and e >= max(.9, be-.05) and t <= .05 and m >= .1 and deployment[name]['relative_target_error'] <= .005)
    keep = [k for k in range(24) if all(report[f'{s}_{k:02}']['passed'] for s in SPACES)]
    return dict(qualified=bool(bv >= .9 and be >= .9 and len(keep) >= 8 and np.linalg.matrix_rank(c[keep[:12]]) == 8), common_safe_indices=keep[:12], all_common_safe_indices=keep, baseline_validity=bv, baseline_evaluability=be, conditions=report)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(r):
    return r['item_id'], r['condition'], r['rollout_index']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--code', type=Path, required=True)
    ap.add_argument('--official', type=Path, required=True)
    args = ap.parse_args()
    run, code = args.run, args.code
    read = lambda name: json.loads((run/name).read_text())
    checks, hashes, counts = {}, {}, {}
    pre = code/'review/geometry_specificity/PILOT_PRECHECK.json'
    lock = json.loads(pre.read_text())
    hashes['precheck'] = sha(pre)
    checks['precheck'] = hashes['precheck'] == '2c7c4a25cacf61aca660274eca2e4562c276148bb54365db206aaa628d109511'
    mismatches = [name for name, expected in lock['sources'].items() if not (code/name).exists() or sha(code/name) != expected]
    # The loader repair is additive; every originally frozen source must match.
    checks['frozen_sources'] = not mismatches
    counts['frozen_source_mismatches'] = len(mismatches)
    hashes['official'] = sha(args.official)
    checks['official'] = hashes['official'] == lock['official_source_sha256']
    prepared, selection = read('PREPARED.json'), read('SELECTION_SEAL.json')
    for name in ['vectors.npz', 'PRIVATE_SCORES.json', 'RESULTS.json', 'PREPARED.json', 'QUALIFICATION.json', 'SELECTION_SEAL.json', 'DEPLOYMENT.json', 'attempts.jsonl']:
        hashes[name] = sha(run/name)
    checks['prepared'] = prepared['protocol_sha256'] == hashes['precheck'] and prepared['vectors_sha256'] == hashes['vectors.npz']
    checks['selection'] = all(selection[k] == hashes[n] for k, n in [('deployment_sha256','DEPLOYMENT.json'), ('qualification_sha256','QUALIFICATION.json')])
    raw = {}
    for phase, expected_count in [('calibration',1752), ('evaluation',17760)]:
        seal = read(phase.upper()+'_SEAL.json')
        schedule = read(phase.upper()+'_SCHEDULE.json')
        raw[phase] = [json.loads(line)['row'] for line in (run/(phase+'.jsonl')).read_text().splitlines()]
        hashes[phase+'.jsonl'] = sha(run/(phase+'.jsonl'))
        hashes[phase.upper()+'_SEAL.json'] = sha(run/(phase.upper()+'_SEAL.json'))
        hashes[phase.upper()+'_SCHEDULE.json'] = sha(run/(phase.upper()+'_SCHEDULE.json'))
        checks[phase+'_seal'] = seal['journal_sha256'] == hashes[phase+'.jsonl'] and seal['protocol_sha256'] == hashes['precheck'] and seal['deployment_sha256'] == hashes['DEPLOYMENT.json'] and seal['schedule_sha256'] == hashes[phase.upper()+'_SCHEDULE.json'] and seal['rows'] == expected_count
        actual = [key(r) for r in raw[phase]]
        checks[phase+'_coverage'] = len(actual) == len(set(actual)) == expected_count and set(actual) == {key(r) for r in schedule}
        seeds = {key(r):r['seed'] for r in schedule}
        checks[phase+'_seeds'] = all(r['seed'] == seeds[key(r)] for r in raw[phase])
        counts[phase] = len(actual)
    checks['selection_schedule'] = selection['schedule_sha256'] == hashes['EVALUATION_SCHEDULE.json']
    checks['prepared_schedule'] = prepared['calibration_schedule_sha256'] == hashes['CALIBRATION_SCHEDULE.json']
    for manifest, target, sizekey, hashkey in [('RECOVERY_1.json','calibration.jsonl','prefix_bytes','prefix_sha256'), ('EVALUATION_RECOVERY_1.json','evaluation.jsonl','prefix_bytes','prefix_sha256'), ('EVALUATION_RECOVERY_1.json','attempts.jsonl','attempt_prefix_bytes','attempt_prefix_sha256'), ('ATTEMPT_COUNTER_RECONCILIATION.json','attempts.jsonl','before_bytes','before_sha256')]:
        m = read(manifest)
        hashes[manifest] = sha(run/manifest)
        prefix = (run/target).read_bytes()[:m[sizekey]]
        checks[manifest+'_'+target+'_prefix'] = hashlib.sha256(prefix).hexdigest() == m[hashkey]
        if target != 'attempts.jsonl':
            prior = [json.loads(line)['row'] for line in prefix.splitlines()]
            missing = {key(r) for r in raw[target.split('.')[0]]} - {key(r) for r in prior}
            checks[manifest+'_missing_only'] = len(prior) == m['preserved_rows'] and missing == {key(r) for r in m['missing_schedule_rows']}
    counts['attempt_ledger_entries'] = len((run/'attempts.jsonl').read_text().splitlines())
    checks['attempt_count'] = counts['attempt_ledger_entries'] == 19543
    attempts = [json.loads(line)['row'] for line in (run/'attempts.jsonl').read_text().splitlines()]
    indices = [r['attempt_index'] for r in attempts]
    counts['unknown_attempt_markers'] = sum('record_type' in r for r in attempts)
    checks['attempt_indices_unique_contiguous'] = len(set(indices)) == len(indices) and max(indices)-min(indices)+1 == len(indices)
    checks['unknown_markers_not_observations'] = counts['unknown_attempt_markers'] == 30 and all('record_type' not in r for rows in raw.values() for r in rows)
    arrays = np.load(run/'vectors.npz', allow_pickle=False)
    c = arrays['coefficients']
    q = qualify(raw['calibration'], read('DEPLOYMENT.json')['controllers'], c)
    checks['qualification'] = q == read('QUALIFICATION.json')
    keep, ids = q['common_safe_indices'], prepared['evaluation_items']
    counts['retained'] = len(keep)
    checks['disjoint_panels'] = not set(ids).intersection(prepared['calibration_items'])
    scored = read('PRIVATE_SCORES.json')
    checks['score_coverage'] = len(scored) == len({key(r) for r in scored}) == 17760 and {key(r) for r in scored} == {key(r) for r in raw['evaluation']}
    sys.path.insert(0, str(code/'src'))
    from epistemic_geometry.benchmarks.external.semantic_v3 import evaluate_external_answer_v3
    references = {r['id']:str(r['output']) for r in map(json.loads, args.official.read_text().splitlines()) if r['id'] in ids}
    panel_path = code/'review/q2_v4_1_prediction_lock/SEMANTIC_PANEL_MANIFEST.json'
    panel = json.loads(panel_path.read_text())
    references.update({r['item_id']:r['reference_answer'] for r in panel['items'] if r['item_id'] in ids})
    checks['reference_coverage'] = set(references) == set(ids)
    amendment = json.loads((code/'review/geometry_specificity/LOADER_AMENDMENT_1.json').read_text())
    hashes['loader_adapter'] = sha(code/'scripts/geometry_specificity_loader_amendment.py')
    checks['loader_adapter'] = hashes['loader_adapter'] == amendment['adapter_sha256']
    hashes['frozen_panel'] = sha(panel_path)
    scoremap = {key(r):r for r in scored}
    errors = 0
    for row in raw['evaluation']:
        failed = bool(row['terminal_answer_channel_failure'])
        s = evaluate_external_answer_v3(row['raw_output'], references[row['item_id']], truncated=failed, runtime_error=False)
        expected = [bool(s.correct) and not failed, bool(s.commitment_valid) and not failed, bool(s.semantic_evaluable) and not failed]
        errors += expected != [scoremap[key(row)][f] for f in ('correct','valid','evaluable')]
    counts['scorer_mismatches'] = errors
    checks['shared_parser_score_verification'] = errors == 0
    y = np.full((3,len(ids),len(keep),8), np.nan)
    baseline = []
    for row in scored:
        if row['condition'] == 'BASELINE':
            baseline.append(row)
        else:
            space, k = row['condition'].rsplit('_',1)
            y[SPACES.index(space),ids.index(row['item_id']),keep.index(int(k)),row['rollout_index']] = row['correct']
    checks['tensor_complete'] = bool(np.isfinite(y).all())
    result = calculate(y,c[keep])
    result.update(baseline_accuracy=float(np.mean([r['correct'] for r in baseline])), dimensions=list(y.shape), eval_rows=len(scored), new_semantic_trajectories=len(scored)+len(raw['calibration']))
    for field, column in [('validity','valid'),('evaluability','evaluable')]:
        result[field] = {s:float(np.mean([r[column] for r in scored if r['condition'].startswith(s+'_')])) for s in SPACES}
    bv, be = [float(np.mean([r[f] for r in baseline])) for f in ('valid','evaluable')]
    guard = bv >= .9 and be >= .9 and min(result['validity'].values()) >= max(.9,bv-.05) and min(result['evaluability'].values()) >= max(.9,be-.05)
    result['evaluation_channel_qualified'] = guard
    if not guard:
        result['association_classification_before_channel_guard'] = result['classification']
        result['classification'] = 'INCONCLUSIVE_EVALUATION_CHANNEL_CONFOUND'
    primary = read('RESULTS.json')
    # Integer numerator identifies mathematical ties without floating centering.
    exact_half = [[exact_correlation(a[:, :, :4], c[keep]), exact_correlation(a[:, :, 4:], c[keep])] for a in y]
    exact_full = [exact_correlation(a,c[keep]) for a in y]
    differences = {}
    def compare(a,b,path):
        if isinstance(a,dict):
            for k,v in a.items(): compare(v,b[k],path+'.'+k)
        elif isinstance(a,list):
            for i,v in enumerate(a): compare(v,b[i],path+'.'+str(i))
        elif isinstance(a,(float,int)) and not isinstance(a,bool):
            differences[path] = float(a-b)
        else:
            checks[path] = a == b
    compare(result,primary,'results')
    checks['numerical_agreement_1e-10'] = all(abs(d) <= 1e-10 for d in differences.values())
    print(json.dumps(dict(passed=all(checks.values()), checks=checks, numeric_differences=differences, counts=counts, input_hashes=hashes, independently_computed=result, exact_integer_tie_diagnostic=dict(associations=exact_full, rollout_half_associations=exact_half, explanation='Integer cross-product numerators preserve mathematical ties. Floating implementations can split them differently; primary sources remain unchanged.'), release_blocked=not all(checks.values()), independence_limits=['Shared frozen semantic parser for score verification only; no independent semantic ground truth.', 'Shared NumPy RNG and quantile; seed 2026090937 and 2000 paired family draws.', 'Independent centered cross-rollout Gram identity and sorting-based tied ranks; no primary numerical or qualification calls.', 'Recovery prefix preservation cannot establish cause of lost records or outcomes of unknown attempts.', 'Exploratory frozen bootstrap classification; coverage not validated.']),indent=2))


if __name__ == '__main__':
    main()
