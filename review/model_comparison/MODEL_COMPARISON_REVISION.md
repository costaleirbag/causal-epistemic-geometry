# Additive revision, 2026-09-10: feasibility stop before fitting

This document supersedes the model list, split definitions, identity fallback,
permutation count and fit-budget sections of MODEL_COMPARISON_DESIGN.md for the
new assigned stage only. The original document and all historical scientific
artifacts remain unchanged. The latest user assignment authorizes implementation
and execution; the old awaiting-review language is not an authorization barrier.
The substantive modeling critique was read from the bounded, truncated PR reply;
its unavailable ending is not represented as reviewed.

The assigned comparison is retrospective and explanatory, with internal data
separation. Unrestricted eight slopes per family are replaced by rank one, with
no rank search. A positive-discrimination model protects against interpreting
monotonic sensitivity as crossed specialization. Held-controller identity-zero
fallback is removed from the evidence for coordinate information.

For family i and controller k, use Bernoulli logistic likelihood. The revised
candidates are:

| Stage | Model | Logit |
|---|---|---|
| A | F | a_i |
| A | R | a_i + b_k |
| A | D | a_i + exp(h_i) b_k |
| A | I | a_i + b_k + u_i v_k |
| A | C | a_i + b_k + u_i w^T x_k |
| B | G | a_i + beta^T x_k |
| B | H | a_i + beta^T x_k + u_i w^T x_k |

Coordinates x are centered using training controllers only. Stage A trains on
rollouts 0..3 and tests 4..7; reversal is sensitivity. Stage B leaves one of 12
controller indices out, using all eight rollouts of all remaining controllers,
with no held-controller labels for fitting, calibration or tuning. Each
orientation uses only its 60 x 12 x 8 panel. Three fixed outcome-independent
assignment permutations are shared by orientations. Explicit permutations are
recorded in MODEL_COMPARISON_PRECHECK.json; no selection or redraw.

Proposed identification for later implementation: b, h and u each sum to zero
on their applicable training index sets. Identity v sums to zero and has unit
norm; coordinate w has unit norm. Choose the sign with first nonzero right-factor
entry positive, simultaneously flipping u. At zero interaction the right factor
is unidentified and must be reported as such. exp(h) gives strictly positive
sensitivity, with geometric mean one. Under full centered coordinate rank eight,
generic parameter dimensions for F/R/D/I/C/G/H are 60/71/130/140/137/68/134.
These are generic manifold dimensions, not effective degrees of freedom; equal
counts would not imply equal capacity. Rank deficiency requires explicit handling
before implementation, not arbitrary coefficient identification from test data.

Retain summed negative log likelihood plus 0.5 times [0.01 ||a||² + lambda times
the sum of squared free-effect norms], with primary lambda 1 and fixed .25/4
sensitivities. Unit right factors are constraints, not additionally shrinkable
scales; interaction shrinkage acts on u. This is a proposed constrained
parameterization, not a tested solver specification. Optimizer, initialization,
tolerances, gradient checks, synthetic signal tests and resume journal have NOT
been implemented or frozen. No real fit is authorized by this partial precheck.

Primary loss remains held-out log loss; Brier is secondary. Pair losses on the
same observations, aggregate within each of 60 families before averaging, and
report controller gains descriptively. Stage A comparisons include R-F, D-R,
I-D and C-D (report gains with positive meaning the latter improves); Stage B
compares H with G for each assignment and real-assignment gains with each control.
Report both orientations of half splitting separately. No p-values or bootstrap
over folds/pairs. Threshold .005 nats is an exploratory decision aid fixed before
fit, not significance. No reversal diagnostic or predictive simulation campaign
is added. Absence of improvement would not prove the simpler model true.

## Concrete budget failure and proposed reduction

For conservative complete reporting, the feasibility calculation crosses all
three penalties with the actual assignment and all three control assignments.
This full crossing is an explicit interpretation of sensitivity/control coverage,
not a claim that the user separately required every such cross-product. Each
nonconvex fit has two predetermined starts total (initial plus one restart);
convex models have one. Every start counts as an attempt. F is cached across
penalties because it has no lambda-dependent terms, but never across splits.

Stage A: 3 orientations x 2 halves x [1 F + 3 penalties x (1 R + 2 D + 2 I +
2 C)] = 132 attempts. Stage B: 3 orientations x 12 held indices x 4 assignments
x 3 penalties x (1 G + 2 H) = 1296 attempts. Total **1428 > 1000**. The counts
are enumerated and tested in revised_feasibility.py. No runtime estimate can
repair this deterministic attempt-ceiling failure.

The user explicitly instructed: if infeasible before fitting, document a minimal
reduction preserving the core comparison and mark incomplete for supervisor.
Accordingly this stage stops before real fitting. This is not an irreducible
scientific or access block, and is not a request for routine user permission.

Proposed reduction: retain Stage A unchanged; retain all three penalties for
actual-coordinate Stage B; retain all three permutation controls for both G/H
at primary lambda 1 only. This removes one ancillary analysis dimension, the
control-by-sensitivity crossing, symmetrically across permutations and
orientations. Stage B becomes 3 x 12 x [(3 x 3) + (3 x 1 x 3)] = 648 attempts;
total **780**. This preserves the core models, rank, restarts, all folds,
actual-coordinate sensitivities and every primary information control. It is
minimal in analysis dimensions removed, not a numerically optimized selection
of individual fits. No outcome-driven subset or budget increase is proposed.

The reduced plan was not executed. Its finite optimizer still needs
implementation and synthetic validation within the separate 30 CPU-minute
ceiling. Real execution remains bounded by 2 CPU-hours, 2 wall-hours, one worker,
BLAS1, 2 GiB, no GPU, with append-only attempted-fit journal and checkpoints.

## Integrity and limits

REVISED_INPUT_GATE.json verifies original-audit digests for scores, raw journal,
selection, prepared/deployment metadata, coefficient archive and schedule. Scores
were hashed as bytes, never parsed into an outcome array. All 17,760 schedule
seeds are unique, so no repeated seed crosses either planned split. This does
not establish independence from family/prompt or operational dependencies.
Coefficient norms, shape and training-centered ranks were checked in place;
individual scores, vectors and item identifiers were not exported. No semantic
scoring or historical numerical/forensic audit was repeated.

Frozen specificity remains inconclusive. There are no new model-loss results.
Learned coordinate-map success would not identify A0, semantic axes, a Jacobian,
new-family generalization or deployment usefulness. Local optimization would
remain a limitation even after convergence. Independent audit is required before
any substantive conclusion or publication. No commit or push was performed.
