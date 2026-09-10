# Independent pilot audit: release blocked

The independent audit did **not** pass. No original source, precheck, score, or primary result was changed. Six synthetic tests passed.

The independent implementation uses family-centered controller matrices and explicitly sums distinct-rollout cross-Gram products. It implements tied ranks by sorting and grouping exact equal values, and computes centered rank dot-product correlations. It reconstructs the tensor from private scores, uses the original NumPy bootstrap generator, seed 2026090937, and all 2,000 paired family draws. It never calls the primary distance, association, summary, or qualification functions.

Primary full-rollout associations and contrast agree within floating precision. However, the independent bootstrap interval is [0.09090543784573636, 0.3573747355275291], versus primary [0.09180535874110858, 0.3573332637511742]. The largest half-rollout correlation difference is 0.00430026720200577. Both classify the comparison as INCONCLUSIVE_SPECIFICITY_CONTRAST and pass the evaluation channel guard. Agreement of classification does not waive the numerical discrepancy.

An additional diagnostic computes exact integer numerators for centered cross-rollout distances of binary observations. Its half-rollout correlations differ from both floating implementations, demonstrating sensitivity to mathematical ties being split by floating arithmetic. This diagnostic does not replace the frozen analysis or justify silently changing its ranking convention. The bootstrap discrepancy requires scientific review before release; no tolerance relaxation was applied.

All originally frozen source hashes match. Raw seals, dependency hashes, exact schedule coverage and recorded seeds, all 17,760 persisted score verifications, independently rederived qualification, and recovery byte prefixes pass. There are 1,752 calibration observations, 17,760 evaluation observations, 12 retained coefficients, and 19,543 unique contiguous conservative attempt indices. Thirty unknown-attempt markers are operational entries, not scientific observations. Recovery appended only the declared missing scientific keys. Prefix preservation does not establish why records were lost or what happened in unknown attempts.

Shared components and limits: the frozen semantic parser verifies scores against references read directly from the hash-pinned full panel (the documented additive loader repair); semantic correctness is not independently adjudicated. NumPy RNG and quantiles are shared primitives. This audit does not independently verify actual model execution or establish bootstrap interval coverage. The frozen classification remains exploratory and conditional on the tested coefficients and two random orientations.

Operational outcome: audit execution finished, release acceptance failed. No commit or push was made. A scientific review of numerical ties is needed before downstream release.
