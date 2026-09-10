# Revised comparison: incomplete before fitting

No scientific model comparison was executed. The historical specificity
conclusion remains inconclusive; this stage supplies no evidence favoring any
explanatory model.

The fully crossed proposed design needs 1,428 attempts, exceeding the hard ceiling
of 1,000 even with only two starts for each nonconvex fit and cached family-only
fits. The assignment's pre-fit infeasibility rule was applied. A 780-attempt
reduction preserving the core comparison is specified in
MODEL_COMPARISON_REVISION.md for supervisor disposition. It omits only permutation
controls crossed with the two sensitivity penalties; all primary controls remain.
This is a design feasibility stop, not failed connectivity or failed convergence.

Four new synthetic metadata/budget tests passed (pytest: 0.13 seconds). They verify
explicit attempt enumeration, preservation of core coverage, rejection of coupled
seeds, and rejection of malformed schedule coverage. These are NOT model gradient,
optimization, invariance, monotonic-signal, rank-one-signal or aggregation tests;
those requested acceptance checks remain unimplemented.

The outcome-blind input gate passed in place. Nine current input hashes agree with
the original audit, including the score digest and sealed raw journal. The schedule
contains 17,760 distinct seeds with complete 60 x 37 x 8 coverage. The coefficient
panel is 12 x 8 and training-centered rank is eight in all 12 exclusions. No raw
outcome array or coefficient array was exported. Digest verification is not a new
semantic audit or independent verification of generation.

Actual model fit attempts: **0**. Real-fit CPU and wall time: **0**. GPU usage and
new inference: **0**. Losses, convergence results and sensitivity/control outcomes
are unavailable, not zero and not successful. Gate/test CPU and peak memory were
not instrumented; command elapsed times are not represented as CPU measurements.
The precheck explicitly records ready_for_real_fitting=false, and must not be
used as an execution freeze. Optimizer, fitting code, journal/checkpoint/resume,
full synthetic validation, real results and independent review remain outstanding.

No historical scientific files, paper workspace, controller state or receipts
were changed. No commit or push. The next decision belongs to the supervisor.
