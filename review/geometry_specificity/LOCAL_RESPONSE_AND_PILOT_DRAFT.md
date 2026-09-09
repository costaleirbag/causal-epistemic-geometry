# Local-response alternative and small matched-orientation pilot

DRAFT: no new vectors, semantic families or model outcomes generated for this pilot yet. Stage-A retrospective results have been inspected. This is a separately declared exploratory specificity pilot, not an amendment of Q2 or Q3.

## Simple competing explanation

Let p_i(c) denote the probability of error on family i under coefficient vector c in a fixed orthonormal intervention basis. Assume a local approximation p_i(c)≈a_i+b_i^T c. Center policy contrasts over families. Then the expected blind-spot shape displacement between c and d is approximately

    Dshape(c,d) ≈ (c−d)^T Cov_i(b_i) (c−d).

If this response covariance is approximately λI and coefficients have unit norm,

    Dshape(c,d) ≈ 2λ[1−cos(c,d)].

Thus positive A0 alignment can arise from approximately isotropic local response without a privileged semantic subspace. This is a model-based alternative, not a theorem about finite-dose generative outputs: nonlinearities, dose calibration, discrete parser/termination rules and anisotropic sensitivity can break the approximation. The empirical question is what explanatory precision and specificity remain beyond it.

Preserving coefficient Gram matrices across ambient orientations holds A0 fixed while allowing response covariance to change. A similar rho alone does not show equal effect magnitude or equal useful complementarity: report stable interaction energy, displacement scale, accuracy, validity and runtime alongside association.

## Proposed finite pilot

- Same frozen Qwen revision, L27 interface and canonical prompt/parser configuration. One MEDIUM implemented-radius target initially; do not silently alter old scientific code.
- Original native rank8 basis plus two independent isotropic ambient rank8 bases, generated once with numerical orthonormalization, no outcome-based redraw. Prefer new shared coefficient draws over selecting12 favorable old controllers:12 normalized Gaussian coefficient vectors shared by all three orientations, preserving the full Gram matrix exactly in float64. Numerical degeneracy rules fixed first.
- Fresh contemporaneous baseline and original-space controls. Historical original rows are context, not the primary paired comparator for new random-space collection.
- Candidate size:100 families selected by fixed hash from the old closed panel,4 independent evaluation rollouts,36 steered policies plus baseline:14,800 evaluation trajectories. The families are exposed historical data, so this tests new interventions on this population, not new-task generalization. No Q3 reserved access.
- Separate12-family label-free calibration,2 rollouts,37conditions:888 nominal qualification trajectories. Dose calibration may need additional forwards; count and budget them separately. Total nominal semantic trajectories15,688 before any exceptional allowance, within20,000 ceiling. Counts remain provisional pending cost and precision review.
- Qualification must compare active, valid perturbations under a common prospectively frozen procedure. Specify exact implemented-norm target, admissible error, validity/termination bounds, activity statistic and no-redraw policy from the established calibration instrument. Report all attrition. If comparable active controls cannot be obtained, classify comparison unqualified rather than crediting specificity.
- Primary contrast: original versus mean of the two random-space A0/Dshape associations with paired family uncertainty, controller bank fixed. Each space is one orientation, not12 independent subspaces. Report each null separately and do not claim universal specialness from only two null draws. Also report displacement scale and stable interaction energy so inactive controls cannot look like negative geometry evidence.
- Four rollouts allow two independent two-rollout profile estimates and exploratory reproducibility checks. Define exact unbiased Dshape estimator and split before inference; preserve negative unbiased pair estimates, do not clip.
- Freeze a precision/sensitivity simulation over effect/noise scenarios, not a post-hoc promise of significance. Decide before pilot outcomes whether the finite design can discriminate an effect large enough to matter. No opportunistic sample expansion.
- Qualification/scoring/private-data boundaries, crash-safe persistence, exact source hashes and runtime preflight remain to be implemented/reviewed before any pilot model call. No need for another routine user permission: campaign adoption already covers this bounded execution after scientific review.

## Immediate engineering work

Locate the original native rank8 basis and calibration prompt manifest by scientific provenance; use the existing Spark1 skill/alias for access. Inspect existing Q2 calibration and semantic runners before creating a thin pilot adapter. Validate hashes, generation stopping semantics and prompt formatting. Estimate runtime from actual existing near-support execution, not Q3.4 collapse timings. Write synthetic geometry/estimator/schedule/recovery tests, finalize the qualification gates and prospective lock, then execute the single planned pilot.
