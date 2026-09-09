# Geometry-guided portfolio discovery under an equal acquisition budget

The retrospective replay found small average improvements in empirical bank opportunity from A0 acquisition, but no consistent improvement in the accuracy of the selected fixed policy. It does not justify reopening the failed Q3 population or launching a larger routing confirmation.

Status: **COMPLETED_AND_NUMERICALLY_AUDITED — EXPLORATORY, NOT CONFIRMATORY**.

## Question and fixed design

Does A0-guided acquisition find a useful eight-policy portfolio with fewer training labels than uniform random acquisition? The candidate pool was the existing 47 MEDIUM controllers (31 historical and 16 fresh controllers), conditional on their prior qualification. A0 is **one minus cosine similarity of normalized controller coefficients**, checked against the archived distance blocks. This is a test of angular diversity; it cannot establish that a richer learned or causal geometry adds value.

The precheck was frozen before this replay's curves were inspected. It specified five historical family folds (240 training, 60 test families; both rollouts together), 64 algorithm seeds, and acquisition budgets of 8, 16, 32 and 47 policies. Each seed shares its first policy between maximin and random acquisition. Prefixes are nested. A factorial comparison holds acquisition and final selection apart: A0 maximin versus uniform acquisition, followed by either top training competence or greedy training opportunity. Selectors receive only acquired training correctness. Ties use policy identity.

All **5,120 bank records** were saved and hash-sealed before any test-fold evaluation. Full source validation covered 37,800 historical and 19,200 fresh score rows, including the unused STRONG and baseline conditions. Only MEDIUM enters this comparison. At budget 47, both acquisition orders and every seed converge to the same bank and champion for each fold and selector.

The fixed-policy endpoint chooses the best acquired training policy within the bank and evaluates that one policy on the test fold. Both selectors necessarily include the training champion: top competence directly, and greedy opportunity at its first step. Their fixed-policy results therefore coincide; these are not two independent confirmations.

## Results

Differences below are A0 minus uniform, in **percentage points**, averaged over five folds and then 64 seeds.

| Acquired policies | Training labels per fold | Bank opportunity: top competence | Bank opportunity: greedy | Fixed-policy accuracy |
|---:|---:|---:|---:|---:|
| 8 | 3,840 | +0.578 | +0.578 | +0.089 |
| 16 | 7,680 | +0.456 | +0.180 | −0.768 |
| 32 | 15,360 | +0.076 | +0.562 | +0.445 |
| 47 | 22,560 | 0.000 | 0.000 | 0.000 |

At budget 8, no label-based bank reduction is possible: the eight acquired policies are the bank. A0 bank opportunity averaged 57.198%, versus 56.620% for uniform. The paired opportunity difference was positive in 47/64 seeds and in the mean of all five folds. Its empirical 2.5–97.5% seed range was **−1.00 to +1.83 points**. This range describes random-start/permutation variation on reused data; it is not a confidence interval for a new population.

At the same budget, fixed-policy accuracy averaged 47.685% versus 47.596%. The paired fixed-policy difference ranged from −2.33 to +3.74 points at those seed quantiles. Across budgets, the fixed-policy contrast changes sign. The observed evidence for practical single-policy benefit is consequently weak and inconsistent, despite the small positive average opportunity contrasts.

More acquired policies did not yield monotonically better test-bank opportunity. For example, A0 with greedy selection averaged 57.198%, 56.813%, 56.753% and 55.333% across the four budgets. Bank size stays eight and its membership changes after training-based selection, so test monotonicity is not guaranteed. This pattern is compatible with selection instability or overfitting, but this replay does not isolate its cause. It must not be turned into a post-hoc claim that eight is an optimal universal budget.

The full paired seed distributions, fold contrasts, selection effects, descriptive interactions, and token ledgers are in [AGGREGATES.json](AGGREGATES.json). No policy, family or answer-level results are released here.

## Costs and limits

- One acquired policy costs 240 training families × two rollouts = 480 revealed correctness labels. This is a **replayed acquisition ledger**, not newly incurred inference expenditure. The primary replay used about 4.67 seconds of CPU wall time and zero model forwards.
- Equal labels are not equal tokens. At budget 8 the acquired-token averages were approximately 168,062 for A0 and 164,902 for uniform; at budget 32 they were 692,417 and 663,874. Historical collection timings are not directly comparable.
- Atlas construction, controller safety qualification and historical selection overhead are not known completely and are not charged here. They are not free. Test-evaluation cost is also outside the acquisition budget. This study establishes no end-to-end compute saving.
- Empirical bank opportunity averages the two correctness rollouts **before** taking a retrospective maximum across the bank for each family. It uses test outcomes to identify that maximum. It is an optimistic opportunity diagnostic, not a deployable router or a guarantee on expected achievable utility.
- These families, folds, controllers and outcomes were previously exposed during research. New software isolation does not erase researcher-level adaptation. The 320 fold/seed combinations share data; no confirmatory p-values or independent-sample interpretation is warranted.
- The historical fold hash `407f563…` hashed a descriptor string, not the family assignment. The original artifact is preserved. The new precheck records an explicitly serialized assignment hash and tests that reconstruction matches the historical function.

## Verification and provenance

Thirteen tests passed, including geometry-axis permutation/corruption, independent coordinate reconstruction, full-source coverage, hidden-label scrambling, fold-specific evaluation, sealed-bank requirements, exact plan coverage, paired aggregation, and full-budget convergence. Formatting/static checks passed.

A post-run arithmetic audit checked all 5,120 records, acquisition token/label counts and champions. It does not call the primary evaluator or aggregator, but shares the validated numeric loader. Maximum metric difference was **0.0** and aggregate mean difference was **2.22e−16**. This is a numerical implementation audit, not an independent scientific replication. See [AUDIT.json](AUDIT.json).

- Precheck SHA-256: `2bad076a99c24518081f904c582021a7bf0bb699382e7d1ca9be0852088ec7ae`.
- Private bank manifest: `09b7942684d9b87aaed15a97ded6bab6a4cf3aec4362b784f09de29bd9b630d0`.
- Private evaluation: `59fa917922c59c8b6f09223c87abc5ca3f1e7ba2e0d590c58f7897b815ca7dd4`.

## Research decision

Close this bounded campaign with the result above. The economical next contribution is to incorporate this negative/limited utility result into the project's evidence assessment, together with the existing geometry findings. Do not start another router search or select a favorable budget retrospectively to advertise a large benefit.

If a later prospective campaign is justified, its narrow question should be whether a fixed descriptor-only diversity rule beats a fixed random-bank comparator on genuinely new, independently qualified near-support tasks. Base-model competence and useful policy diversity must be established before committing to a large utility trial. Such a design would test transfer of the small opportunity signal, not rescue Q3.4 or confirm routed accuracy. The present replay is insufficient to justify large additional compute by itself.

Q3.4 remains NOT_QUALIFIED; its confirmation remains NOT_RUN. No new model forwards, reserved-data access, router/bank/champion changes or paper edits occurred in this campaign.
