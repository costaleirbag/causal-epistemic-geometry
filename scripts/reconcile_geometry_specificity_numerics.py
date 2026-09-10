"""Additive CPU sensitivity diagnostic; private tensors never leave execution site.

For x_ir=Y_ikr-Y_ilr, D=sum_{r!=s}[n sum_i x_ir x_is
- (sum_i x_ir)(sum_i x_is)]/[n^2 R(R-1)]. Integer numerator
A uses controller Grams collapsed over rollouts. Independent numerator B uses
pair differences and the sum-square identity, with no controller Grams.
Neither changes the frozen estimator or its exact floating equality ranks.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

SEED = 2026090937
SPACES = ('ORIGINAL', 'RANDOM_1', 'RANDOM_2')


def binary(y):
    a = np.asarray(y)
    if a.ndim != 3 or a.shape[2] < 2 or not np.isin(a, [0, 1]).all():
        raise ValueError('binary tensor with at least two rollouts required')
    n, k, r = a.shape
    if 4*n*n*r*r >= np.iinfo(np.int64).max:
        raise ValueError('integer bound exceeded')
    return a.astype(np.int64)


def numerator_gram(y):
    a = binary(y)
    n, k, r = a.shape
    total = a.sum(axis=2)
    sums = a.sum(axis=0)
    g = n*(total.T@total - np.einsum('ikr,ilr->kl', a, a))
    g -= np.outer(sums.sum(axis=1), sums.sum(axis=1)) - sums@sums.T
    return np.diag(g)[:, None] + np.diag(g)[None, :] - g - g.T


def numerator_pairs(y):
    a = binary(y)
    n, k, r = a.shape
    x = a[:, :, None, :] - a[:, None, :, :]
    t = x.sum(axis=0)
    return n*((x.sum(axis=3)**2 - (x*x).sum(axis=3)).sum(axis=0)) - (t.sum(axis=2)**2 - (t*t).sum(axis=2))


def ranks(x):
    _, ix, count = np.unique(x, return_inverse=True, return_counts=True)
    return (np.cumsum(count)-(count+1)/2)[ix]


def corr(a, b):
    a, b = ranks(a), ranks(b)
    a, b = a-a.mean(), b-b.mean()
    den = np.sqrt((a@a)*(b@b))
    return float(a@b/den) if den else None


def classify(rho, ci):
    if ci[0] > .15:
        return 'OBSERVABLE_ALIGNMENT_HIGHER_FOR_ORIGINAL'
    if ci[0] > -.15 and ci[1] < .15 and min(rho) > .30:
        return 'COMPARABLE_RELATIONAL_ALIGNMENT_IN_TESTED_ORIENTATIONS'
    return 'INCONCLUSIVE_SPECIFICITY_CONTRAST'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--primary', type=Path, required=True)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--audit-result', type=Path, required=True)
    args = ap.parse_args()
    p, audit = load(args.primary, 'frozen_primary'), load(args.audit, 'first_audit')
    read = lambda name: json.loads((args.run/name).read_text())
    names = ['PRIVATE_SCORES.json', 'vectors.npz', 'PREPARED.json', 'QUALIFICATION.json', 'RESULTS.json']
    hashes = {name: sha(args.run/name) for name in names}
    old = json.loads(args.audit_result.read_text())
    assert all(hashes[name] == old['input_hashes'][name] for name in names)
    ids = read('PREPARED.json')['evaluation_items']
    keep = read('QUALIFICATION.json')['common_safe_indices']
    y = np.full((3, len(ids), len(keep), 8), np.nan)
    for row in read('PRIVATE_SCORES.json'):
        if row['condition'] != 'BASELINE':
            s, k = row['condition'].rsplit('_', 1)
            y[SPACES.index(s), ids.index(row['item_id']), keep.index(int(k)), row['rollout_index']] = row['correct']
    c = np.load(args.run/'vectors.npz', allow_pickle=False)['coefficients'][keep]
    ix = np.triu_indices(len(c), 1)
    geom = (1-c@c.T)[ix]
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, len(ids), (2000, len(ids)))
    methods = ['exact', 'primary', 'independent']
    report = {}
    for scope, tensor in [('full', y), ('first_half', y[:, :, :, :4]), ('second_half', y[:, :, :, 4:])]:
        stats = {m: dict(max_distance_error=0., rank_entries_different_from_exact=0, matrices_with_rank_difference=0, distinct_distance_order_reversals=0, distinct_distance_false_ties=0, exact_tie_pairs_split=0, max_rank_difference=0.) for m in methods[1:]}
        values = {m: [] for m in methods}
        max_function_error = 0.
        exact_mismatches = 0
        for sample in [None, *draws]:
            z = tensor if sample is None else tensor[:, sample]
            rs = {m: [] for m in methods}
            for a in z:
                num = numerator_gram(a)
                other = numerator_pairs(a)
                exact_mismatches += int(np.count_nonzero(num != other))
                d = num[ix]
                den = a.shape[0]**2*a.shape[2]*(a.shape[2]-1)
                rs['exact'].append(corr(geom, d))
                for m, f, association in [('primary', p.dshape, p.association), ('independent', audit.distances, audit.correlation)]:
                    v = f(a)[ix]
                    rs[m].append(association(a, c))
                    re = corr(geom, v)
                    if re is not None and rs[m][-1] is not None:
                        max_function_error = max(max_function_error, abs(re-rs[m][-1]))
                    st = stats[m]
                    st['max_distance_error'] = max(st['max_distance_error'], float(np.max(np.abs(v-d/den))))
                    diff = np.abs(ranks(v)-ranks(d))
                    st['rank_entries_different_from_exact'] += int(np.count_nonzero(diff))
                    st['matrices_with_rank_difference'] += int(np.any(diff))
                    st['max_rank_difference'] = max(st['max_rank_difference'], float(diff.max()))
                    j, k = np.triu_indices(len(d), 1)
                    exact_sign = np.sign(d[j]-d[k])
                    float_sign = np.sign(v[j]-v[k])
                    st['distinct_distance_order_reversals'] += int(np.sum(exact_sign*float_sign < 0))
                    st['distinct_distance_false_ties'] += int(np.sum((exact_sign != 0)&(float_sign == 0)))
                    st['exact_tie_pairs_split'] += int(np.sum((exact_sign == 0)&(float_sign != 0)))
            for m in methods:
                values[m].append(rs[m])
        summaries = {}
        for m in methods:
            v = np.array(values[m], dtype=float)
            delta = v[:, 0]-.5*(v[:, 1]+v[:, 2])
            valid = np.isfinite(v[1:]).all(axis=1)
            ci = np.quantile(delta[1:][valid], [.025, .975]).tolist()
            summaries[m] = dict(associations=v[0].tolist(), contrast=float(delta[0]), individual_contrasts=(v[0, 0]-v[0, 1:]).tolist(), paired_family_bootstrap_q025_q975=ci, individual_correlation_intervals=np.quantile(v[1:][valid], [.025, .975], axis=0).T.tolist(), individual_contrast_intervals=np.quantile(v[1:, :1][valid]-v[1:, 1:][valid], [.025, .975], axis=0).T.tolist(), valid_draws=int(valid.sum()), classification=classify(v[0], ci), max_correlation_difference_from_exact=float(np.nanmax(np.abs(v-np.array(values['exact'], float)))))
        report[scope] = dict(matrices_per_implementation=6003, integer_implementation_mismatches=exact_mismatches, floating_diagnostics=stats, max_native_vs_diagnostic_correlation_error=max_function_error, results=summaries)
    original = read('RESULTS.json')
    reproduction = {}
    for m, saved in [('primary', original), ('independent', old['independently_computed'])]:
        cur = report['full']['results'][m]
        reproduction[m] = {field: float(np.max(np.abs(np.array(cur[field])-np.array(saved[field])))) for field in ['associations', 'contrast', 'paired_family_bootstrap_q025_q975']}
        halves = np.array([report['first_half']['results'][m]['associations'], report['second_half']['results'][m]['associations']]).T
        reproduction[m]['rollout_half_associations'] = float(np.max(np.abs(halves-np.array(saved['rollout_half_associations']))))
    explained = all(s['integer_implementation_mismatches'] == 0 and s['max_native_vs_diagnostic_correlation_error'] < 1e-14 and all(d['distinct_distance_order_reversals'] == d['distinct_distance_false_ties'] == 0 and d['max_distance_error'] < 1e-14 for d in s['floating_diagnostics'].values()) for s in report.values()) and all(v < 1e-14 for r in reproduction.values() for v in r.values())
    unchanged = all(sha(args.run/name) == value for name, value in hashes.items())
    print(json.dumps(dict(status='BLOCKED', summary='Numerical reconciliation complete; supervisor disposition required', additive_sensitivity_only=True, release_gate_unchanged=True, fully_explained_by_exact_tie_splitting=explained, classification_robust_full= len({v['classification'] for v in report['full']['results'].values()}) == 1, original_inputs_unchanged=unchanged, input_hashes=hashes, source_hashes={'primary':sha(args.primary),'first_audit':sha(args.audit),'first_audit_result':sha(args.audit_result),'diagnostic':sha(__file__)}, numpy_version=np.__version__, seed=SEED, paired_draws=2000, draws_sha256=hashlib.sha256(draws.astype('<i8').tobytes()).hexdigest(), dimensions=list(y.shape), saved_result_reproduction_max_errors=reproduction, scopes=report, uncertainties=['Exploratory bootstrap coverage remains unvalidated.', 'Finite coefficients and two random orientations; no population specificity or utility claim.', 'No diagnosis of lost-record root cause or unknown attempt outcomes.', 'Exact-tie sensitivity is additive and cannot waive the original failed audit.']), indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
