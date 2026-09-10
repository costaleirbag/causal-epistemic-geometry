# Supervisor disposition adopted before fitting — 2026-09-10

The supervisor accepts the 780-attempt reduction proposed in
MODEL_COMPARISON_REVISION.md: Stage A 132 unchanged; Stage B 648, all actual
assignment penalties and all three permutation controls at lambda 1 only.
Both G/H are retained throughout. No outcomes have been fitted by this stage.
This supersedes the feasibility stop and its awaiting-implementation language;
the original design, revision and partial precheck remain history. Execution
requires a new tested EXECUTABLE precheck. No ceiling is increased. No commit
or push occurs before independent review.

The rank-one definitions and penalties in the revision are retained. Numerical
representation uses orthonormal sum-zero contrasts for b,h,u,v and a normalized
nonzero vector for the right factor (v in contrast space or w in coordinates).
Its redundant radial coordinate is computational only; dimensions remain
60/71/130/140/137/68/134. Gradients through normalization are tested, and the
convergence criterion includes the intrinsic tangent gradient, so increasing
the redundant radius cannot fake convergence. Sign is canonicalized only on
output (first nonzero right-factor coordinate positive). At zero u the right
factor is unidentified. Penalty on h is on centered log discrimination, on b
and u their Euclidean norms, and on beta its coordinate norm; right unit factors
are unpenalized. Family intercept penalty is .01. No coordinate standardization.

Use deterministic full inverse BFGS in float64 with analytic derivatives of the
summed binomial objective. Initial inverse Hessian is identity; descent fallback
is negative gradient if the proposed direction is not descending. Armijo 1e-4,
steps 1,1/2,... (40 trials), update only for s'y > 1e-12 ||s|| ||y||;
otherwise reset to identity. Max 3000 iterations. Require both computational
and intrinsic maximum absolute gradient / training trials <= 1e-9. No relaxed
criterion on loss stagnation. Nonfinite objective, line-search exhaustion or
iteration cap is failure. Initial intercepts and free effects are zero except
D uses a deterministic centered .1-normal skill, and interactions use .1-normal
centered u; right factor is unit normal. Start seeds 20260910 and 20260911,
shared across fits; no outcome-based initialization. Convex models have one
start, nonconvex two. Select converged start by smallest training penalized
objective, ties by start index; both starts must converge for complete status.
No claim of global optimality for D/I/C/H. No changes after real losses.

The resource gate precedes every objective evaluation. Whole-fit checkpoints
are exclusive-created and attempts are journaled before starting. Interrupted
attempts count; resume may only use completed checkpoints and may not silently
retry interrupted starts. Resource accounting includes prior recorded CPU and
wall time; interrupted attempt means incomplete pending independent disposition.
A new private output directory is separate from all historical artifacts.
Prediction clipping [1e-6,1-1e-6] and family-first paired aggregation follow the
original design. Reversal diagnostic and predictive simulations are deferred.
