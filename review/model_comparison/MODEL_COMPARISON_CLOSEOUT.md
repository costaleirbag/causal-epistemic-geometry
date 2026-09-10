# Final explanatory model-comparison closeout

Conditional original-coordinate predictive gain exists in this exposed, selected panel. **Independent numerical audit: PASS. Full robust-benefit rule: NOT PASSED.** These are separate conclusions. The .005-nat threshold is an exploratory discussion aid, not a significance test; no new classifier or decision rule is introduced.

G models coordinate-linked global skill plus family difficulty; H adds a family-varying rank-one term. D allows positive family discrimination of global skill; C adds coordinate-linked rank-one structure with known-controller intercepts. Gains below are baseline loss minus candidate loss (G−H or D−C), so positive means improved prediction. This resolves the possible “C−D improvement” naming ambiguity. Values are read from the aggregate JSON, then rounded.

| Stage / orientation / split | Lambda | Log-loss gain (nats) | Brier gain |
|---|---:|---:|---:|
| B / Original | 1 | 0.012270759 | 0.004614043 |
| B / Original | 0.25 | 0.004478689 | 0.004108253 |
| B / Original | 4 | 0.008919564 | 0.003115492 |
| B / Random 1 | 1 | 0.002236281 | 0.000535112 |
| B / Random 1 | 0.25 | -0.000588789 | 0.000028308 |
| B / Random 1 | 4 | 0.001095622 | 0.000325622 |
| B / Random 2 | 1 | -0.001665155 | -0.000485821 |
| B / Random 2 | 0.25 | -0.005251953 | -0.000872588 |
| B / Random 2 | 4 | 0.000220196 | -0.000059796 |
| A / Original / primary | 1 | 0.005844786 | 0.001737454 |
| A / Original / primary | 0.25 | 0.010820541 | 0.002512006 |
| A / Original / primary | 4 | 0.000114953 | 0.000321490 |
| A / Original / reverse | 1 | 0.006963224 | 0.000528853 |
| A / Original / reverse | 0.25 | 0.013685284 | 0.001839966 |
| A / Original / reverse | 4 | -0.000403524 | -0.000418461 |

Original Stage B is positive at all three penalties, but lambda .25 falls below .005. Original Stage A reverses sign at lambda 4 in the reverse half. Brier corroborates the primary original gains, but does not remove this sensitivity or rescue the full rule. Random controls show mixed sensitivity signs.

Compare incremental G−H against each assignment permutation, since permutations change G as well as H. The three controls are descriptive, not a permutation significance test. Each row uses lambda 1.

| Orientation | Permutation | Permuted G−H | Actual minus permuted G−H | Brier gain difference |
|---|---:|---:|---:|---:|
| Original | 1 | -0.010254882 | 0.022525640 | 0.006343118 |
| Original | 2 | -0.000648351 | 0.012919110 | 0.004039050 |
| Original | 3 | -0.007359380 | 0.019630138 | 0.005960221 |
| Random 1 | 1 | -0.002103197 | 0.004339478 | 0.001124707 |
| Random 1 | 2 | -0.003865312 | 0.006101593 | 0.001579146 |
| Random 1 | 3 | -0.002052506 | 0.004288786 | 0.001415808 |
| Random 2 | 1 | 0.000565951 | -0.002231105 | -0.000514397 |
| Random 2 | 2 | 0.002460420 | -0.004125574 | -0.000853525 |
| Random 2 | 3 | 0.001285528 | -0.002950683 | -0.000443327 |

All orientations use equal panel dimensions and the same selected families, controller indices and rollout partitions: 60 × 12 × 8 observations per orientation, excluding baseline. Outcomes differ across orientations. Stage A separates rollout halves; Stage B excludes every label of each held controller, centers on the other eleven controllers, and predicts held controllers for **known families**. Penalties and starts were fixed; saved training objectives select starts. This is internal separation within already exposed outcomes, not prospective confirmation or new-family validation.

In Original, Random 1 and Random 2 respectively, 42/60, 42/60 and 43/60 families have identical binary outcomes across conditions and repetitions. Low per-trial losses therefore do not represent thousands of independent informative observations. Aggregation is paired and family-first; folds share training data and controller pairs share controllers. No calibrated confidence intervals, p-values or population-specificity estimates are claimed. Qualification by common selection, only two random orientations, unequal response scale/SNR and greater latent flexibility constrain interpretation.

The generic skill/difficulty alternative remains substantive: original D improves R by 0.013051443 nats in the primary half and 0.009470726 in reverse. A nonlinear monotonic skill/difficulty model can create probability-scale interaction without crossed specialization. Conditional coordinate gain does not identify semantic axes, specificity, a Jacobian, A0 correctness, routing benefit or deployment usefulness. Specialization reversals are not inferred: their diagnostic was deferred. Failure of the robust rule does not prove the simpler explanation true.

The prior geometry-specificity pilot remains inconclusive, with its historical numerical audit failure disclosed and unchanged. This later audit PASS applies to the model comparison only. Historical raw recovery preserved byte prefixes; unknown-attempt ledger markers are not scientific observations. The length/index accounting collision did not establish the cause of lost records. Sources, private outcomes, frozen pilot/data/prechecks and historical conclusions remain unchanged.

All 780 attempts converged; the independent audit checked 510 selected groups, 114 loss rows, 90 paired summaries, 18 assignment controls and 1560 journal entries. Nonconvex stationary points are not global optima: 18/270 groups disagree between initializations above 1e-6, with maximum summed objective gap 11.147836472. The unchanged gradient tolerance is 1e-9 per training trial; independent maximum is 9.97873772891e-10. A numerical near tie became an exact tie in independent arithmetic; original selection by saved training objective was preserved.

Historical fitting used 8.771457488 CPU seconds and 19.705271517 wall seconds (about 8.77/19.71); final audit used 8.333013344 CPU seconds (about 8.33). Measured fitting was below 30 minutes, while its frozen enforced cap was two hours. The independent audit cap was 30 minutes. Historical reports record 33 implementation tests plus 9 independent tests. This preparation reran those and 4 earlier synthetic-design tests: 46 passed in 0.84 seconds. No real-data refitting, inference or remote execution occurred in this preparation.

Chronology is supported by declared freeze and filesystem metadata preceding the first checkpoint, not cryptographic proof: the journal has no wall-clock timestamps. The audit inherits the pinned semantic scores and parameter layout; arithmetic reconstruction is independent, semantic scoring is not repeated. Private-input and checkpoint preservation is evidence from the completed audit, not a new remote verification in this stage.

## Reading the preserved progression

1. `MODEL_COMPARISON_DESIGN.md`, `DESIGN_INPUT_HASHES.json`, `synthetic_validation.py`, its test and `SYNTHETIC_RESULTS.json`: superseded initial design and feasibility illustration, not the executed fit contract.
2. `MODEL_COMPARISON_REVISION.md`, `revised_feasibility.py`, its test, `REVISED_INPUT_GATE.json`, `MODEL_COMPARISON_RESUME_INSPECTION.json` and all `*_PARTIAL_HISTORY.*`: superseded feasibility stop; draft/partial prechecks did not authorize fits. Old filenames inside resume inspection refer to the subsequently archived partial versions.
3. `MODEL_COMPARISON_DISPOSITION.md` adopted the finite reduction; `MODEL_COMPARISON_PRECHECK.json` is the EXECUTABLE 780-attempt contract, pinning implementation and tests. `EXECUTABLE_VALIDATION.json` records implementation validation.
4. `finite_models.py`, `run_finite_comparison.py`, `test_finite_models.py`, `summarize_finite_comparison.py`, `MODEL_COMPARISON_RESULTS.json`, `MODEL_COMPARISON_VERIFICATION.json` and `MODEL_COMPARISON_ANALYSIS.md`: unchanged executor outputs. Their “independent audit pending” language is superseded by the audit and this closeout; their bytes are preserved for hash verification.
5. `independent_audit.py`, `test_independent_audit.py`, `MODEL_COMPARISON_AUDIT.json` and `.md`: independent numerical audit. This closeout supplies the final interpretation.

Reviewers can rerun `python -m pytest -q -p no:cacheprovider review/model_comparison/test_*.py` with NumPy and pytest. The public bundle supports aggregate comparison and synthetic validation. Reconstructing every fit loss requires authorized access to sealed private inputs/checkpoints; these are deliberately excluded from release. Historical published context is pinned by `DESIGN_INPUT_HASHES.json` at commit 580bf4d. No draft precheck, synthetic test or release inventory authorizes a new fit.

## Operational disposition

Local preparation complete; publication remains blocked pending supervisor evidence review. No staging, commit, push or external write was performed. `RELEASE_PAYLOAD_REVIEW.json` enumerates the exact proposed scientific payload and destination for independent review; it is not publication approval. The automatic review previously rejected publication launch because destination and payload had not been independently verified; no alternative publication route was attempted.

The default next step is evidence synthesis and manuscript argument, not more fitting or a new GPU campaign. This finite closeout does not stop the continuing research program. Subsequent decisions belong to the supervisor; this stage makes no manuscript, controller, automation, Q3 or infrastructure changes.
