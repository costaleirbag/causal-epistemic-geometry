# Retrospective repeatability diagnostic — frozen before new calculations

This analysis uses the already exposed closed Q2 panel, not Q3 confirmation/reserve. It is exploratory and conditional on the existing 47 MEDIUM controllers. No new model generations. Source identities and numeric loading are those verified in geometry_budget_replay/PRECHECK.json. Reuse the loader, not the conclusions or bank-selection outcome.

For correctness arrays Y[i,p,r], separately double-center each rollout:
Z_r = Y_r - family mean_r - policy mean_r + grand mean_r.
This removes additive family difficulty and marginal policy competence on the finite panel. It does not remove all heterogeneity or establish a causal mechanism.

Primary descriptive quantities:
- cross-rollout interaction product S = mean(Z_0 * Z_1), estimating squared centered probability interaction under conditionally independent rollout draws;
- observed centered energy E = (mean(Z_0^2) + mean(Z_1^2))/2;
- disagreement energy N = mean((Z_0-Z_1)^2)/2, with identity E=S+N;
- signed normalized reproducibility S/E when E>0; no clipping of negative S or ratio;
- repeatability of marginal policy accuracy reported separately, not conflated with interaction.

Uncertainty: paired family bootstrap (recompute centering within each draw), controllers fixed, 2000 draws with seed2026090917. This does not support controller-population or new-task inference. With only two rollouts, label the uncertainty as exploratory; document assumptions and possible dependence of the sampling seeds.

Descriptive broken-alignment checks: permute policy columns of Z_1 or family rows of Z_1, independently, 999 permutations using seed2026090918; compare S to these distributions without exchangeability p-values. Explain that heterogeneous variances can invalidate a formal permutation test. These controls are not substitutes for matched random intervention subspaces.

Secondary oracle diagnostic: compare the existing empirical mean-before-max opportunity with cross-rollout selection, choosing a policy using only one rollout's correctness for that family and evaluating the other, then reversing. Predefine ties with 64 policy permutations seeded2026090920..2026090983 shared between directions. Report mean and seed spread. This has privileged access to a labeled repetition of the SAME family and is not a deployable router or held-out-family performance. Report the accuracy of a uniform policy and the marginal competence context; no claim of gain beyond a fixed champion without a separately valid train/test construction.

Implementation reviewed before execution. Four tests passed using synthetic fixtures: no interaction in deterministic additive cases, stable complementary profiles, independent noise in expectation, centering/projection identity, family-policy axis alignment, and cross-rollout winner independence from evaluation labels. Numerical audit must recompute primary quantities by separate arithmetic. Do not tune metrics to observed signs.

Follow-on pilot must still be designed/reviewed: CPU results inform interpretation and pre-pilot precision planning, not selection of favorable old families or random orientations. The campaign does not end with this diagnostic.
