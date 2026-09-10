"""Render all public model losses and contrasts; does not fit or access private data."""
import hashlib
import json
from pathlib import Path
from revised_feasibility import fit_plan

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'MODEL_COMPARISON_RESULTS.json').read_text())
p=json.loads((ROOT/'MODEL_COMPARISON_PRECHECK.json').read_text())
assert r['status']=='complete' and r['attempts_started']==r['attempts_completed']==780
assert [tuple(x['spec']) for x in r['convergence']]==fit_plan(False)
assert all(x['status']=='converged' and x['gradient_per_trial']<=1e-9 for x in r['convergence'])
assert len(r['losses'])==114 and len(r['paired_comparisons'])==90 and len(r['assignment_controls'])==18
assert r['cpu_seconds']<7200 and r['wall_seconds']<7200 and r['peak_rss_kib']*1024<2*1024**3
assert r['historical_inputs_unchanged']
assert r['precheck_sha256']==hashlib.sha256((ROOT/'MODEL_COMPARISON_PRECHECK.json').read_bytes()).hexdigest()
assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in p['code_hashes'].items())
assert hashlib.sha256((ROOT/'MODEL_COMPARISON_RESULTS.json').read_bytes()).hexdigest()=='d43080ed1d6ba17ded3e4153bf588c72d7410134f837fe4fc4c391e88c53f15a'
for row in r['losses']:
    assert row['folds_completed']==(1 if row['key'][0]=='A' else 12)
    assert not any(k.startswith('family_') for k in row)
    for metric in ['log_loss','brier']:
        assert abs(sum(row['controller_'+metric])/12-row[metric])<1e-12

groups={}
for row in r['convergence']: groups.setdefault(tuple(row['spec'][:-1]),[]).append(row)
start_differences=[abs(rows[0]['objective']-rows[1]['objective']) for rows in groups.values() if len(rows)==2]
names=['Original','Random 1','Random 2']
lines=['# Retrospective finite model comparison — independent audit pending','',
'Operational status: all 780 planned attempts converged under the frozen criterion. This is executor validation, not an independent scientific audit. No commit or push was performed. The original design/revision and partial precheck/results/report are preserved as explicitly named history. The accepted 780-attempt disposition was recorded before any real fitting.','',
'The original orientation shows a positive held-controller rank-one incremental gain: G−H = 0.012271 nats at lambda 1. Its gains remain positive at .25 (0.004479) and 4 (0.008920), although .25 falls below the preselected .005 discussion threshold. The primary Random 1 gain is 0.002236 and Random 2 is −0.001665; their sensitivity signs vary. Actual-coordinate H outperforms each of the three primary permutation H controls in the original by 0.023836–0.043948 nats. This supports conditional predictive information in the original coordinates in this exposed panel, subject to audit. It does not establish population subspace specificity.','',
'For known cells at lambda 1, original C improves D by 0.005845 nats in the primary half and 0.006963 in the reverse half. The monotonic D baseline itself improves R by 0.013051 and 0.009471. Identity interaction I does not uniformly improve D: its original primary gain is −0.000088 and reverse gain 0.003576. Hence repeated probability heterogeneity cannot simply be equated with crossed specialization. The reversal diagnostic was deferred.','',
'All fits used the same 60×12×8 panel per orientation, with baseline observations excluded. Stage A trains 0..3 and tests 4..7; A reverse exchanges these halves. Stage B holds out each controller entirely, uses all rollouts from the other eleven, and centers coordinates on those eleven only. Penalties and starts are fixed; no held-out loss selects models, starts or permutations. G/H are compared under every retained assignment.','',
'F=family; R=Rasch; D=positive family discrimination; I=identity rank one; C=coordinate rank one with known-policy intercepts; G=coordinate-global skill; H=G plus family-varying rank one. The normalized right-factor parameterization has a computational radial redundancy. Its intrinsic tangent gradient is explicitly checked; parameter counts are manifold dimensions, not equal-capacity claims. Nonconvex convergence establishes a stationary point under the numerical criterion, never a global optimum.','',
'## Validation and resources','',
f"33 synthetic tests passed locally and in the designated remote CPU environment. Checks cover the actual objective gradient, sum constraints, monotonic ordering, rank-one signal, all models and sensitivity penalties, rotation invariance, training-only centering, held-label exclusion, score schema/coverage, family aggregation, exclusive checkpoints and exact budget enumeration. Real execution: {r['cpu_seconds']:.6f} CPU seconds, {r['wall_seconds']:.6f} wall seconds, peak RSS {r['peak_rss_kib']} KiB, one worker and BLAS1; all below the 2-hour/2-GiB limits. Test-run timing is recorded separately in EXECUTABLE_VALIDATION.json; editor/tool overhead was not separately metered.",'',
f"The maximum gradient per training trial was {max(x['gradient_per_trial'] for x in r['convergence']):.12g}, below 1e-9 without changing tolerances. Every attempt has its convergence/iteration/objective/resource record in MODEL_COMPARISON_RESULTS.json. All nine pinned input hashes matched before and after execution. The original-audit score digest and sealed schedule/input chain were verified without semantic rescoring. The schedule has 17,760 unique seeds, compatible with the frozen grouping; this does not imply family/prompt independence.",'',
'Journal verification found exactly 1,560 records (one begin and end for each of 780 attempts). An idempotent invocation returned the existing result and added zero attempts. Private checkpoints contain fitted parameters; per-family losses remain private. Public output contains model/fold aggregates, anonymized controller diagnostics, paired-family summaries, and coordinate rank/conditioning metadata. No raw outcomes, vectors, prompts or infrastructure details are included.','',
f"Of {len(start_differences)} nonconvex fit groups, {sum(d>1e-6 for d in start_differences)} had starting-point objective differences above 1e-6; the maximum difference was {max(start_differences):.6f} in summed penalized loss. This is direct evidence of optimization sensitivity. The lower training objective selected the start under the frozen rule; held-out outcomes never did. Objective/gradient rotation invariance was tested, not equality of local solutions reached from coordinate-dependent random initializations. Prediction clipping affected {sum(row['clipped_cells'] for row in r['losses'])} evaluated cells across reported model configurations; per-model counts are below.",'',
'## All model losses','',
'A split 0=primary, 1=reverse. B assignment 0=actual, 1..3=frozen permutations. B rows aggregate all 12 completed held-controller folds. All loss rows and paired-family summaries are in the JSON at full precision.','',
'| Stage | Orientation | Split/assignment | Model | Lambda | Log loss | Brier | Clipped cells |','|---|---|---:|---|---:|---:|---:|---:|']
for row in r['losses']:
    stage,o,s,model,lam=row['key']
    lines.append(f"| {stage} | {names[o]} | {s} | {model} | {lam} | {row['log_loss']:.9f} | {row['brier']:.9f} | {row['clipped_cells']} |")
lines+=['','## All incremental gains','','Positive favors the model after the minus sign: baseline loss − candidate loss. B controls are primary lambda only by the accepted disposition.','','| Stage | Orientation | Split/assignment | Contrast | Lambda | Log-loss gain | Brier gain |','|---|---|---:|---|---:|---:|---:|']
for row in r['paired_comparisons']:
    stage,o,s,model,lam=row['key']; q=row['paired']
    lines.append(f"| {stage} | {names[o]} | {s} | {row['baseline']}−{model} | {lam} | {q['log_loss']['mean']:.9f} | {q['brier']['mean']:.9f} |")
lines+=['','## Every assignment control','','Positive favors actual coordinates; these are descriptive controls, not a permutation test.','','| Orientation | Permutation | Model | Control−actual log loss | Control−actual Brier |','|---|---:|---|---:|---:|']
for row in r['assignment_controls']:
    q=row['paired']; lines.append(f"| {names[row['orientation']]} | {row['assignment']} | {row['model']} | {q['log_loss']['mean']:.9f} | {q['brier']['mean']:.9f} |")
lines+=['','## Orientation contrasts of actual-coordinate gains','','Original incremental gain minus each random incremental gain; all lambda values shown. These contrasts are descriptive and do not correct unequal response scale or signal-to-noise.','','| Stage | Split | Contrast | Lambda | Original−Random 1 | Original−Random 2 |','|---|---:|---|---:|---:|---:|']
lookup={tuple(row['key']):row for row in r['paired_comparisons']}
for key,row in lookup.items():
    stage,o,s,model,lam=key
    if o!=0 or (stage=='B' and s!=0): continue
    values=[row['paired']['log_loss']['mean']-lookup[(stage,j,s,model,lam)]['paired']['log_loss']['mean'] for j in [1,2]]
    lines.append(f"| {stage} | {s} | {row['baseline']}−{model} | {lam} | {values[0]:.9f} | {values[1]:.9f} |")
lines+=['','## Limits and next review','',
'The comparison is retrospective: outcomes were already exposed to the research program. Internal separation prevents the specified computational leakage, not researcher adaptation. Only known families and a qualification-conditioned twelve-controller panel are evaluated. The two random orientations do not identify a population specificity effect. .005 nats is an exploratory decision aid, not significance; no fold/pair bootstrap or p-values are used. Positive coordinate prediction does not identify A0, semantic axes, a Jacobian, new-family generalization or deployment usefulness. Failure to improve does not prove a simpler model true. Penalty sensitivity and local optima limit interpretation; no expansion or post-loss optimizer changes were made.','',
'The historical specificity conclusion remains inconclusive. Historical numerical audit/reconciliation and raw recovery remain untouched; the lost-record root cause is not established and unknown-attempt markers are not observations. Independent review should reproduce the new losses and scrutinize the normalized-factor optimizer, training-only selection, aggregation, input chain, and finite-scope limitations before publication. Continuing-program decisions remain with the supervisor.']
(ROOT/'MODEL_COMPARISON_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
verification=dict(passed=True,expected_attempts=780,completed_attempts=780,converged_attempts=780,loss_rows=114,paired_contrasts=90,assignment_controls=18,frozen_code_hashes_verified=True,remote_local_result_digest_matches=True,idempotent_result_verified=True,journal_records=1560,independent_audit=False,publication='not committed or pushed')
(ROOT/'MODEL_COMPARISON_VERIFICATION.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps(verification))
