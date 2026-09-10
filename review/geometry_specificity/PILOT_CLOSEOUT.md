# Geometry-specificity pilot: bounded scientific closeout

Decision: close collection as **INCONCLUSIVE_SPECIFICITY_CONTRAST** and consolidate one manuscript. The original has higher observed angular alignment than either sampled control, but this bounded pilot does not separate subspace specificity from generic response structure and unequal measurement attenuation. No further collection follows automatically.

Operational disposition: **closeout completed with disclosed numerical audit failure; approved for publication with the evidence bundle**. The original independent audit remains `passed=false`, specifically `numerical_agreement_1e-10=false`. The later [supervisor disposition](PILOT_SUPERVISOR_DISPOSITION.json), reviewed 2026-09-10T03:30:49.582933+00:00, explicitly authorizes `PUBLISH_INCONCLUSIVE_CLOSEOUT_WITH_DISCLOSED_AUDIT_FAILURE`. It does not convert this into an audit pass. Historical audit and reconciliation reports correctly record their then-current block pending review; they remain unchanged. This report uses the later disposition rather than silently rewriting that history.

## Frozen comparison and primary estimates

The [protocol](PILOT_PROTOCOL.md) compared the original rank-eight basis with two frozen random orientations at the same intervention layer, preserving the shared coefficient Gram matrix and the MEDIUM target amplitude 0.25. Evaluation comprised 60 previously exposed families, 12 commonly qualified coefficients per orientation and eight rollouts, with contemporaneous baseline. This is a finite, conditional comparison, not new-task confirmation or an estimate over a population of subspaces.

A0 is one minus coefficient cosine. Response distance is the family-centered distinct-rollout product estimator on binary correctness, retaining negative estimates and scoring invalid responses zero. Spearman associations use shared controller pairs; the pairs are not independent observations. Primary estimates below come unchanged from [PILOT_RESULTS.json](PILOT_RESULTS.json). Display values are rounded; JSON retains precision.

| Orientation | Angular rho | Accuracy | Validity = evaluability | Mean pair displacement | Stable product S | Observed energy E | S/E |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original | 0.418140069 | 41.718750% | 98.750000% | 0.042282498 | 0.019379478 | 0.035132861 | 0.551605467 |
| Random 1 | 0.017889573 | 40.190972% | 99.392361% | 0.021801497 | 0.009992353 | 0.023294512 | 0.428957381 |
| Random 2 | 0.247886442 | 40.243056% | 99.531250% | 0.025095298 | 0.011502012 | 0.025736883 | 0.446907724 |

The primary original-minus-mean-control contrast is **0.285252061**; the descriptive original-minus-random-1 and original-minus-random-2 contrasts are **0.400250496** and **0.170253627**, respectively. The frozen paired-family bootstrap uses 2,000 valid draws and gives percentile endpoints **[0.091805359, 0.357333264]**. Its lower endpoint does not exceed the frozen +0.15 margin, and the comparable-alignment rule is not satisfied. Preserve the frozen inconclusive label. The interval and classifier are exploratory: neither coverage nor classification error rates have been calibrated. A positive lower percentile endpoint must not be promoted to a confirmatory specificity finding. Comparison against the mean of two controls does not prove all-three equivalence or equivalence to either individual control.

Baseline accuracy is 39.583333%. The evaluation channel guard passed. Channel validity is high but not identical; it neither proves equal competence nor eliminates uneven channel failures as a contributor to response distances. Original response scale and S/E exceed both controls, while random 1 has especially weak angular alignment. Equal implemented amplitude and token activity do not equal signal-to-noise ratio (SNR), equal semantic effect, or equal angular/radial state change. The observed rho ordering therefore does not isolate latent specificity.

Primary first-/second-half rollout associations are original 0.353846154 / 0.426990920, random 1 0.017806260 / 0.007389702, and random 2 0.165915164 / 0.276735205. These are descriptive stability diagnostics, not independent replications. S/E measures normalized doubly centered probability-scale response energy under rollout independence, not the fraction of questions solvable or variance causally explained by geometry.

## Qualification and conditioning

The independently audited qualification metadata, summarized in [PILOT_CLOSEOUT_AGGREGATES.json](PILOT_CLOSEOUT_AGGREGATES.json), show 20/24 original candidates passing, 23/24 random-1 candidates passing and 23/24 random-2 candidates passing. Thus attrition was 4, 1 and 1 respectively. All calibration conditions had validity/evaluability 1.0 and zero terminal failures; rejected conditions failed the weak token-change activity screen. Baseline calibration validity/evaluability was 1.0. Implemented-amplitude qualification passed the original audit.

Nineteen of 24 coefficient indices qualified in common: five were excluded by the intersection. The first 12 in frozen draw order were retained, leaving seven commonly qualified candidates unused under the cap. The retained coefficient rank passed the rank-eight requirement. Qualification used 12 disjoint calibration families and two rollouts, without correctness selection or redraw. The target population is explicitly coefficients conditioned on common qualification in all three orientations. This noisy intersection can remove regions where orientations differ; it does not represent all candidate directions.

## Numerical failure, reconciliation and later disposition

The [original audit](PILOT_INDEPENDENT_AUDIT.json) passed all nonnumerical checks, including frozen sources, coverage, qualification, seeds, score verification and recovery prefixes, but failed numerical agreement. Its bootstrap endpoints were [0.090905438, 0.357374736], and the largest original half-rollout rho disagreement was 0.00430026720200577. Primary full-panel associations and contrast agreed at floating precision. Classification agreement alone did not waive the failed gate.

The additive [reconciliation report](PILOT_NUMERICAL_RECONCILIATION.md) and [JSON](PILOT_NUMERICAL_RECONCILIATION.json) explain the disagreements fully: floating arithmetic split exact mathematical distance ties, changing ranks; residual correlation arithmetic differed at machine precision. Two independently organized integer identities agreed entry-for-entry across 18,009 tested matrices (full and half panels and the same paired resamples). There were no distinct-distance order reversals or false ties. Maximum distance error was about 1.624e-15. Both saved floating result sets were reproduced exactly for originally reported correlations, contrast and interval endpoints. **No unexplained numerical discrepancies remain in the tested samples.** This is finite numerical evidence, not a universal guarantee.

| Full-panel quantity | Frozen primary | Original independent audit | Additive exact-tie sensitivity |
|---|---:|---:|---:|
| Original rho | 0.418140069 | 0.418140069 | 0.418140069 |
| Random 1 rho | 0.017889573 | 0.017889573 | 0.017889573 |
| Random 2 rho | 0.247886442 | 0.247886442 | 0.247886442 |
| Original minus mean | 0.285252061 | 0.285252061 | 0.285252061 |
| Bootstrap lower endpoint | 0.091805359 | 0.090905438 | 0.090910469 |
| Bootstrap upper endpoint | 0.357333264 | 0.357374736 | 0.357376038 |

All three full-panel classifications remain INCONCLUSIVE_SPECIFICITY_CONTRAST. Exact ties are additive only; neither estimator, ranking convention, threshold nor primary result has been replaced. Stable endpoints do not mean each resample is insensitive: maximum full-bootstrap rho deviations from exact ranks were 0.012349683 for primary and 0.016959312 for independent arithmetic. Independent first-half and second-half resamples reached 0.095025629 and 0.051346776, with maximum rank displacement 22 positions. Those deviations also occurred only within exact tie groups. All nine full/half diagnostic classifications stayed inconclusive; half-bootstrap classifications are post hoc descriptive sensitivities, not additional gates.

The supervisor disposition records successful rerunning of all 14 audit/reconciliation tests. The original audit shares the frozen semantic parser and NumPy RNG/quantiles; it does not independently adjudicate semantic truth or actual model execution. Numerical reconciliation does not validate bootstrap coverage, which remains unvalidated.

## Exact recorded costs and persistence incidents

The following are sealed totals for persisted scientific rows, verified against manifest hashes pinned by the original audit. Elapsed seconds are sums of row timings, not measured total accelerator occupancy or end-to-end execution time.

| Phase | Persisted trajectories | Generated tokens | Sum of row elapsed seconds |
|---|---:|---:|---:|
| Calibration | 1,752 | 24,009 | 2102.8701811619103 |
| Evaluation | 17,760 | 234,063 | 20383.728703581844 |
| Total | 19,512 | 258,072 | 22486.598884743755 |

Recorded row time totals about 6.246277468 hours. Twelve baseline denominator prefills were separately specified in the protocol and are outside semantic-trajectory counts. Loading, calibration-prefill overhead, interruptions and unknown-attempt token/time consumption are not fully quantified by these seals; an exact total compute or monetary cost cannot be inferred. No paid service or new inference was used for this closeout.

The conservative operational ledger contains **19,543** unique contiguous attempt entries, below the 20,000 ceiling by 457. This differs from 19,512 persisted scientific trajectories; neither count should be silently substituted for the other. The 72-hour ceiling is an operational cap, not measured GPU usage.

Collection had nonzero exits and lost persisted records. Calibration recovery appended two missing predeclared keys after preserving 1,750 rows; evaluation recovery appended 29 after preserving 17,731 rows. Original byte prefixes were verified. Thirty unknown-attempt markers filled two calibration and 28 evaluation index gaps, conservatively consuming budget. They are **not scientific observations**, and their outcomes are unknown. Reconciliation corrected a length-versus-index collision in operational accounting without changing frozen scientific code. That accounting issue is not an established explanation for lost scientific records: **the root cause of record loss was not established**. Recovery does not prove that missingness was outcome-independent.

The audit pins RECOVERY_1.json, ATTEMPT_COUNTER_RECONCILIATION.json, EVALUATION_RECOVERY_1.json and the calibration, evaluation and selection seals; their safe hashes and counts are in the companion aggregates. Full raw data were sealed before scoring. Scientific source commit ed16ed6 and additive exact-frozen-panel loader repair 28acd6d are preserved. Precheck SHA256 is `2c7c4a25cacf61aca660274eca2e4562c276148bb54365db206aaa628d109511`; evaluation raw SHA256 is `248c1bd198ef4c85b9964aed1f97f6469357d49d84b0dde8d572644ac3f0219d`. Private observations and vectors remain private.

## Relation to completed work and scientific decision

[Stage A](REPEATABILITY_REPORT.md) used the closed 300-family × 47-policy × two-rollout Q2 panel, with no new model forwards. Signed projected reproducibility was 0.562267. It supports a repeatable probability-scale interaction component, not subspace specificity. Its cross-rollout selector used correctness from the same family and therefore privileged information. Probability-scale repeatability does not exclude a nonlinear global-skill/family-difficulty explanation such as p = sigmoid(family difficulty + policy skill), which can yield centered interaction without crossed specialization or reversals in policy ordering.

The completed, numerically audited [budget replay](../geometry_budget_replay/CLOSEOUT.md) was retrospective on previously exposed, qualified controllers. At acquisition budget eight, A0-minus-uniform bank opportunity was +0.578 percentage points, but fixed-policy accuracy only +0.089 points; fixed-policy differences were −0.768 at budget 16 and +0.445 at 32. Opportunity uses a retrospective outcome maximum, not deployable selection. The replay had zero new model forwards, omitted complete construction/qualification and test costs from acquisition budgets, and established no end-to-end savings. Its weak, inconsistent practical benefit does not motivate an automatic larger campaign.

Four claims must remain distinct. **Causal control** concerns effects of the applied activation intervention under the frozen experimental regime; it is not evidence of a semantic mechanism or knowledge representation. **Relational alignment** is the measured association between coefficient geometry and response-profile distances. **Semantic specificity** would require discriminating a privileged semantic organization from generic local response, scale, anisotropy and noise explanations; this pilot is inconclusive on that question. **Practical utility** requires usable selection information and benefits with all relevant costs, neither of which follows from rho or repeatability.

The evidence-based decision is to end this bounded collection and consolidate one manuscript integrating control, relational structure, repeatability, this inconclusive specificity comparison and the limited utility replay. A generic local-response explanation remains viable; it was not proved sufficient here. A future analysis or collection would require its own discriminating question and authorization, not an automatic extension to obtain a favorable label. No guarantee of novelty, journal acceptance or publication follows from this closeout. No paper workspace, Q3 data, router, bank, champion, confirmation or reserve was modified. The report-preparation stage performed no push; publication is handled by the subsequent release stage.

## Evidence verification

The supervisor disposition's three pinned evidence hashes were recomputed and matched before writing. The safe qualification/cost/recovery manifest hashes also matched the original audit. Frozen evidence is preserved; the release bundle includes this report, safe companion aggregates, the original audit, additive reconciliation code/tests and the supervisor disposition. The structured stage receipt identifies this report, companion aggregates, disposition, original audit, reconciliation and primary results by absolute path and SHA256.
