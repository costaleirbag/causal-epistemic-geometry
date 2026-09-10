# Additive numerical reconciliation — supervisor disposition required

Numerical reconciliation complete; supervisor disposition required. Operational status: **BLOCKED**. The original failed audit, frozen sources, primary result, thresholds and release gate remain unchanged. No commit or publication was made.

All observed association, half-rollout and bootstrap disagreements are explained by floating arithmetic splitting exact mathematical distance ties, plus rank-correlation arithmetic at machine precision. Both saved implementations were reproduced exactly for every originally reported association, contrast, interval endpoint and half-rollout correlation. No unexplained numerical discrepancy remains in the tested finite panel and draws. This is an additive sensitivity diagnostic, not a replacement primary analysis or an audit waiver.

For binary observations, let x_ir = Y_ikr − Y_ilr for a controller pair, n be the number of sampled families (including bootstrap multiplicity), and R the rollout count. Family centering gives:

```text
D_kl = N_kl / [n² R(R−1)]
N_kl = Σ_(r≠s) [n Σ_i x_ir x_is − (Σ_i x_ir)(Σ_i x_is)]
```

The first implementation builds integer controller cross-Grams, using summed rollouts minus same-rollout products. The second builds pair differences directly and uses sum-of-squares identities: n Σ_i[(Σ_r x_ir)²−Σ_r x_ir²] − [(Σ_r Σ_i x_ir)²−Σ_r(Σ_i x_ir)²]. These independently organized integer calculations have a common positive denominator, so integer equality and ordering are exact. Binary validation and a conservative int64 bound guard the arithmetic. The denominators are 201600 for eight rollouts and 43200 for four rollouts; a one-unit numerator gap is far larger than the observed floating error.

Eight local tests passed, including an independent fractions.Fraction oracle with explicit centered distinct-rollout products, duplicate controllers, complements, negative distances, constant outcomes, repeated families, and nonbinary rejection. On the private data, both integer identities agreed entry-for-entry on 18,009 matrices: three orientations × (original sample + 2,000 draws) × three scopes. Each scope used the same paired family draws, NumPy default_rng seed 2026090937; all 2,000 draws were valid in every implementation and scope. The draw-index digest is recorded in JSON.

The primary distance and association functions were invoked only as isolated comparisons. The independent first-audit distance and association functions were also preserved and invoked without running its structural audit. Neither is imported into the independent integer estimators. Geometry, RNG and percentile primitives are shared. Applying the diagnostic rank-correlation calculation to the native floating distances reproduces native associations within 1.67e-16.

Counts below include the original sample and all bootstrap samples, across all orientations. Rank entries and pair comparisons are repeated diagnostic counts, not independent scientific observations. A false tie means distinct exact distances collapsed to equal floating values.

| Scope | Floating implementation | Max absolute distance error | Changed rank entries | Split exact-tie pairs | Distinct-order reversals | False ties |
|---|---|---:|---:|---:|---:|---:|
| full | primary | 5e-16 | 6827 | 3901 | 0 | 0 |
| full | independent | 1.62e-15 | 8267 | 5283 | 0 | 0 |
| first_half | primary | 3.61e-16 | 46633 | 33954 | 0 | 0 |
| first_half | independent | 1.03e-15 | 52721 | 49003 | 0 | 0 |
| second_half | primary | 4.44e-16 | 39680 | 27768 | 0 | 0 |
| second_half | independent | 9.37e-16 | 46063 | 41260 | 0 | 0 |

There are zero distinct-distance reversals and zero false ties in every case: floating ranks differ only within exact mathematical tie groups. The maximum distance error is 1.624e-15. The 1e-14 checks in diagnostic bookkeeping identify reproduction at floating precision; they do not alter the original 1e-10 audit gate, and rank order comparisons use exact equality with no tolerance.

| Scope | Implementation | rho original | rho random 1 | rho random 2 | Contrast | Paired percentile interval |
|---|---|---:|---:|---:|---:|---|
| full | exact | 0.418140069 | 0.017889573 | 0.247886442 | 0.285252061 | [0.090910469, 0.357376038] |
| full | primary | 0.418140069 | 0.017889573 | 0.247886442 | 0.285252061 | [0.091805359, 0.357333264] |
| full | independent | 0.418140069 | 0.017889573 | 0.247886442 | 0.285252061 | [0.090905438, 0.357374736] |
| first_half | exact | 0.353394289 | 0.020210245 | 0.166985064 | 0.259796634 | [0.070786813, 0.348415087] |
| first_half | primary | 0.353846154 | 0.017806260 | 0.165915164 | 0.261985442 | [0.070121375, 0.348420584] |
| first_half | independent | 0.353846154 | 0.019559545 | 0.170215431 | 0.258958666 | [0.070599849, 0.349170289] |
| second_half | exact | 0.427405382 | 0.008267655 | 0.275684986 | 0.285429062 | [0.093760716, 0.363413620] |
| second_half | primary | 0.426990920 | 0.007389702 | 0.276735205 | 0.284928466 | [0.092803621, 0.363850934] |
| second_half | independent | 0.427058001 | 0.006450401 | 0.276108966 | 0.285778318 | [0.093802857, 0.363435346] |

All nine displayed classifications are INCONCLUSIVE_SPECIFICITY_CONTRAST. Half-sample bootstrap intervals/classifications are additional descriptive sensitivities, not prospectively specified new decision gates. The evaluation channel guard passed in the preserved first audit; it was not re-audited here.

For full data with exact ties, original-minus-random-1 is 0.400250496 and original-minus-random-2 is 0.170253627. Their paired percentile sensitivity intervals are [0.117694534, 0.472523426] and [0.021166615, 0.286590395]. Individual rho intervals and all other descriptive contrasts are in JSON. These are exploratory, unadjusted intervals, not new confirmatory tests.

Endpoint stability does not imply negligible sensitivity in each resample: maximum absolute rho deviations from exact ranks across the full bootstrap are 0.01235 (primary) and 0.01696 (independent). In first-half resamples the independent deviation reaches 0.09503, and in second-half resamples 0.05135. These larger deviations still arise only within exact ties; the largest rank displacement is 22 positions. No estimator substitution is justified by classification agreement alone.

The interpretation remains conditional on these coefficients, families, rollout regime and two sampled random orientations. Bootstrap coverage has not been validated; rank sensitivity reconciliation does not validate coverage, establish population subspace specificity, crossed specialization, or deployable utility. Unequal response noise can affect observed alignment. No cause of lost records or outcomes of unknown attempts was established.

Input digests matched the preserved first audit and remained unchanged after computation. Only private scores, coefficients and previously prepared metadata were read in place; no collection, model loading, raw journal review or full structural audit was repeated. Repository artifacts contain only code, tests and safe aggregates. The source digests and NumPy version are recorded in JSON. Frozen source hashes in the checkout also match the original precheck.

Reproduction interface (paths supplied by the authorized operator; private inputs remain at execution site):

```text
python scripts/reconcile_geometry_specificity_numerics.py --run PRIVATE_RUN --primary FROZEN_PRIMARY_MODULE --audit FIRST_AUDIT_MODULE --audit-result FIRST_AUDIT_JSON
python -m pytest -q tests/test_geometry_specificity_numerical_reconciliation.py
```

Supervisor disposition is still required. The first audit continues to record passed=false; this finite diagnostic does not authorize release or further experiments.
