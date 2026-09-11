# Retrospective family-only extension F_B

2026-09-10. Design and synthetic implementation only. No real-data fit or scoring.
This is an additive extension of the completed Stage B comparison, not a revision
of its precheck, fitted H/G predictions, or historical specificity classification.
Previously exposed outcomes make this exploratory even though this stage inspected
only public code, metadata and aggregate results. Supervisor owns the next stage.

## Estimand and exact masks

For each ORIGINAL, RANDOM_1, RANDOM_2 orientation separately, predict binary
correctness for a held controller in each of 60 **known** families. Use the same
ordered 12 retained controllers and eight rollouts as `split_panel(...,'B',held)`
in `../model_comparison/finite_models.py`. For held position k=0,...,11, train on
all rolls 0,...,7 of every controller position except k. Thus each family has
11 × 8 = 88 training responses, exactly the information available to H/G for
that family, and eight test responses. H/G additionally pool information across
families and use coordinates; F_B deliberately imposes no controller response.
Equal available labels does not imply equal capacity or identical pooling.

Family order must be PREPARED evaluation_items order; controller order must be
QUALIFICATION common_safe_indices order, not a new numeric sort; orientation order
is the three names above. Inherit the sealed binary correctness convention,
including invalid/unevaluable outputs as failures. Exclude the separate BASELINE
condition and calibration observations. No Q3 or additional family is used.
No held labels influence fitting, penalty, stopping, clipping, initialization or
selection. Coordinate-assignment permutations change only x, never masks or y.
No probabilities are pooled across orientations. There are no new-family claims.

## One estimator, fixed before new calculation

For each family i and fold k let s be the sum of its 88 training successes.
Set p_ik = sigmoid(a_ik), where a is the unique minimizer of

    L(a) = 88 log(1 + exp(a)) - s a + 0.005 a².

This is precisely the existing summed binomial negative log likelihood plus
half the fixed 0.01 intercept penalty in Model.objective. Setting all G/H
non-intercept effects to zero gives this objective. It also corresponds to Stage
A's F model evaluated under B masks; Stage A's already fitted F is not reusable.
There is no division by trial count in the penalized training objective. Lambda
1/.25/4 penalizes other effects only, so F_B has no lambda sweep. No added prior,
Laplace pseudo-count, empirical Bayes pooling, empirical frequency, or clipping
as a substitute for fitting is introduced. The existing penalty is unambiguous;
there are no competing baseline definitions requiring outcome-based selection.

The first derivative is 88 sigmoid(a) - s + .01 a; second derivative is
88 p(1-p) + .01 > 0. Even s=0 or 88 has a unique finite optimum. A fixed
[-32,32] bracket has opposite derivative signs for every s in [0,88]. Use 64
bisections in float64 and require absolute derivative residual <= 1e-11.
Bisection, bracket, iteration count and stricter residual check are numerical
choices not specified by the old BFGS solver; they target the identical unique
optimum and cannot select among baseline definitions. No retry or relaxed
convergence gate is proposed. Synthetic tests exhaust all 89 possible counts.

| Successes / 88 | F_B probability | F_B logit |
|---|---:|---:|
| 0 | 0.000808970341434 | -7.11893900461734 |
| 22 | 0.250124766701922 | -1.09794697691165 |
| 44 | 0.5 | 0 |
| 66 | 0.749875233298078 | 1.09794697691165 |
| 88 | 0.999191029658566 | 7.11893900461727 |

These are deterministic synthetic counts, not empirical probabilities or a claim
of consistency without shrinkage. The balanced prediction has log loss log(2)
= 0.6931471805599453 nats/trial and Brier 0.25 on any binary outcome.

## Calculation count and metrics

Compute 3 orientations × 12 folds = **36 vector baseline calculations**, each
solving 60 scalar roots: **2160 scalar intercept estimates**. One deterministic
solution each, no starts or tuning. Predict 3 × 60 × 12 × 8 = 17,280 held binary
observations, with 2160 probabilities repeated over eight rollouts. Folds have
5280 training trials and 480 test trials. Do not reuse fits across folds or
orientations. Cache F_B across coordinate assignments and non-intercept lambdas.

Use frozen evaluation clipping [1e-6,1-1e-6] for both metrics (inactive for all
admissible F_B counts). Primary negative Bernoulli log loss uses natural logs,
in nats per binary trial, not bits, total likelihood, or penalized objective.
Secondary Brier is (y-p)² per binary trial, no factor two or percentage scaling.
Average eight rollouts per family and held controller, then the 12 controllers
per family, then equally over 60 families. Do not pool orientations. For each
metric and model M, report paired family differences L(F_B)-L(M), positive
favoring M, and the mean, median, minimum, maximum and fraction positive;
controller-wise gains are descriptive. Negative difference favors F_B.

Compare frozen G and H at actual assignment for lambda 1,.25,4, in all three
orientations: 18 model comparisons. Reuse the same F_B for frozen three assignment
controls at lambda 1 for both models: 18 more comparisons, with no baseline
refits. Total 36 baseline-vs-model aggregate comparisons, each with both metrics.
This is bookkeeping against already fitted predictions, not an added study.
Keep every original G-H gain exactly as published.

## Independent audit contract for subsequent authorized execution

Public aggregate results cannot reconstruct exact predictions or family-paired
comparisons. A subsequent private adapter must first verify the original input
hash chain, score identity, prepared family order, qualification order, selection
and evaluation seals, unique schedule coverage and original model precheck. Use
the already sealed scores; never rescore semantic outputs. No private inputs are
included in this extension. Freeze this extension's hashes before loading them.

Consume the completed model-comparison private checkpoint set read-only and its
saved PRIVATE_METRICS records, with keys
[B, orientation_index, held_index, assignment_index, model, penalty]. Check all
12 held indices exactly once for each of 36 model groups (432 selected fold
predictions). Retain selected_start from the frozen records; do not reselect
starts or rerun G/H fits. Verify checkpoint/input hashes against the audited
manifest, reconstruct logits from those exact parameters using the frozen
training-centered x for the recorded permutation, and compare resulting per-family
losses with the saved private metrics. Audit the independent arithmetic layout
in `../model_comparison/independent_audit.py`, including right-factor normalization.
Do not infer row alignment from array dimensions alone.

For F_B an independent checker can use scalar Newton or a separately implemented
root bracket and the explicit objective above. Check count/mask equality and
stationarity; compare probabilities within 1e-10 and per-family/aggregate losses
within 1e-10 absolute. These are arithmetic acceptance tolerances, not scientific
thresholds. For G/H reuse the established audit tolerance and disclose any
mismatch without overwriting historical values. Write new private fold logits,
training counts, losses and paired differences into a new exclusive directory;
never append to historical fit journals. Export only reviewed aggregate metrics,
counts, numerical diagnostics and hashes. Family identifiers, counts, predictions
and individual outcomes remain private. Verify source/checkpoint hashes afterward.
No H/G refit, optimizer change, penalty choice or loss rounding before differences.

## Interpretation and stopping

H or G beating F_B means predictive benefit beyond a regularized known-family
constant under these masks. It does not by itself show incremental geometric
interaction: that is the distinct, unchanged G-H comparison. Conversely F_B
beating H/G means the constant predicts better here, not that geometry is absent.
H-G improvement can coexist with both models losing to F_B. Superior original
relative to two random orientations is not population subspace specificity,
semantic-axis identification, a Jacobian, crossed specialization or deployment
utility. Common qualification, exposed outcomes, shared training folds, only two
random orientations, unequal SNR and many invariant families remain limitations.

No new significance threshold, p-value, bootstrap, confidence interval or pass/fail
scientific classification is introduced. Do not apply the historical .005-nat
discussion aid as a new F_B significance claim. Report all orientations, both
metrics and all already frozen comparison settings regardless of sign. Operational
success means masks, numerical verification and provenance pass; it does not mean
any model wins. A discrepancy stops the extension for supervisor disposition.
