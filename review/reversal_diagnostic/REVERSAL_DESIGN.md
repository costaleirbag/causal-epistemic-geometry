# Single retrospective paired-policy reversal diagnostic

Design only, 2026-09-10. No empirical selection, fitting, inference, private input access, remote execution or publication has occurred. This document fixes one exploratory diagnostic for supervisor disposition. Existing outcomes and aggregate comparisons have been exposed; computational separation cannot make this confirmatory.

## Scientific target and fixed model

Ask whether **one training-selected pair of existing ORIGINAL policies exchanges its accuracy ordering between two fixed groups of known families on rollouts 4..7**. This distinguishes broad crossed specialization from heterogeneous magnitudes under a globally monotonic skill/difficulty ordering. It does not test semantic mechanism, subspace specificity, new-family generalization or deployable routing.

Use model C, Stage A, orientation index 0 (ORIGINAL), primary split 0, actual coordinates, rank one, penalty 1, trained on rollouts 0..3. C has known-policy intercepts plus a coordinate-linked family-varying rank-one term: the scientific target is reversal among these same known policies on new repetitions. Stage B H instead targets held-controller prediction; its fits use all eight rollouts of other controllers, so one policy's purported validation outcomes enter the fit predicting another. Combining its outputs for selection creates mutual outcome leakage. Stage B, F_B, random orientations, other penalties, D/I and reverse-half fits cannot select this pair. C is fixed by the target, not by validation performance.

Read closeouts: `../family_baseline_extension/FAMILY_BASELINE_CLOSEOUT.md`, `../model_comparison/MODEL_COMPARISON_CLOSEOUT.md`, `../geometry_specificity/PILOT_CLOSEOUT.md`. The independent F_B arithmetic audit passed; ORIGINAL H beats F_B on both metrics at all three penalties (primary F−H log loss 0.01489009; Brier 0.00457787). Both random primary H fits lose to F_B. These comparisons do not establish a reversal. Model comparison passed its numerical audit but failed its full robust-benefit rule. Specificity remains inconclusive with the historical pilot numerical failure disclosed. None of these conclusions is changed here.

## Reconstruction feasibility from public code

Static inspection confirms **schema-level reconstructibility**, not current private checkpoint availability or integrity. `../model_comparison/run_finite_comparison.py` writes each `fit_%04d.json` with `attempt`, `spec`, and `fit` including parameters, convergence status and training objective. It selects the lowest saved objective, breaking ties by start number; it does not save a separate training probability array. `revised_feasibility.py:fit_plan(False)` identifies the two specs `(A,0,0,C,1,start)` for starts 0 and 1. Derive filenames from that frozen plan rather than guessing indexes. Do not select starts using any loss or held metric.

`finite_models.py:split_panel` uses the first four rollouts for Stage A split 0 and centers all 12 known coefficient rows by their mean. `Model.logits` reconstructs the same 60×12 logits for training and held repetitions because C has no rollout covariate. With the original ordered families and retained policies, set Xc=X−mean(X), and reconstruct

    eta[f,k] = a[f] + (Kcontrast @ b)[k]
               + (Fcontrast @ u)[f] * (Xc @ (q / norm(q)))[k]
    p = exp(-logaddexp(0, -eta))

Use the frozen contrast convention and parameter slices (60 a, 11 b, 59 u, 8 q), finite nonzero q, and un-clipped sigmoid probabilities. No optimization, outcomes or `PRIVATE_METRICS.json` are required. A future additive adapter must read only the two exact checkpoint records and sealed identity/coordinate metadata before selection; never invoke the historical executor or its full-panel loader. Verify precheck/source/input/checkpoint hashes against the completed audit and preserve its objective/start choice. Resolve frozen row identities before canonical sorting. Check complete 60-family, 12-policy coverage, original qualification and split provenance. Missing/inconsistent checkpoints, nonconvergence, nonfinite parameters, zero q or mismatched hashes are a no-go, with no refit or fallback. This stage did not test these conditions on private files.

## One deterministic selection rule

Use all 60 frozen evaluation families and all 12 retained ORIGINAL policies, excluding BASELINE. Identities are their exact frozen strings; compare by Unicode code-point order, without renaming or numeric reinterpretation. For each of the 66 unordered pairs, orient (a,b) in increasing policy-identity order. Compute d_f = p_C(f,a) − p_C(f,b) using **only the reconstructed train-fit predictions**.

Sort families by (d_f, frozen family identity). The bottom 30 form L and the top 30 form U: disjoint, exhaustive, equal weight, minimum size 30 each. Ties are retained and split by frozen identity. Let m_L and m_U be their mean d. A pair is eligible only if m_L ≤ −0.05 AND m_U ≥ +0.05. Select the eligible pair maximizing min(−m_L,m_U), then break exact score ties by the ordered pair identities. No tolerance-based near-tie rule or rounding. Stable summation and sorting make array reordering irrelevant; pin the implementation/runtime for later reproduction. The algorithm searches 66 candidates but exports exactly one selection, not 66 held comparisons.

Five percentage points is an explicit practical convention: at least five expected additional correct responses per hundred within **each** group, equivalent to six per group's 120 held trials. It is not a powered threshold, a learned optimum or a definition of scientific confirmation. Balanced halves avoid choosing sample sizes after seeing effects and demand broad specialization across this panel. They can dilute narrow true crossing regions, especially with many unresponsive families. A no-go therefore rejects this broad diagnostic opportunity, not every possible specialization. Do not shrink groups, tune the margin, select extreme families or expand models after failure. Constants are fixed here before any new selection, despite previously exposed outcomes.

If no pair qualifies (including monotonic predictions, all ties, or insufficient margin), record `NO_GO_NO_TRAIN_REVERSAL`, stop without opening held outcomes, and return the decision to the supervisor. Invalid/missing input is a separate integrity no-go. There is no second search.

## Held evaluation and dependence

Before opening held outcomes, write a private immutable selection record: design/code/runtime hashes, checkpoint and metadata digests, selected start, train-prediction digest, exact pair, L/U identities, train means and criterion. Verify this seal immediately before evaluation. The pure library validates shapes and provenance declarations; it cannot authenticate a caller's data labels or enforce a filesystem seal. Those checks belong to the separately authorized adapter. Do not publish private identities, predictions or family outcomes.

Read only sealed correctness for ORIGINAL rollouts 4..7 under the original invalid-as-incorrect convention; require complete unique keys and binary scores. For each family compute D_f = mean_r(Y_far − Y_fbr), retaining paired policies and all four repetitions. Report Δ_L=mean_L D_f and Δ_U=mean_U D_f, group sizes, per-rollout group differences and descriptive family ranges. Same-sign heterogeneous effects fail: the required direction is Δ_L<0 **and** Δ_U>0. A practical observed crossing additionally requires Δ_L≤−0.05 and Δ_U≥+0.05. Zero is not an opposite sign. Opposite signs below the margin are a small observed crossing; any other result fails the held reversal criterion. These are descriptive outcomes, never `confirmed` or a specificity PASS. No evaluation reselection, relabeling L/U, sign flipping, refit or additional metric-based decision.

Report no p-value, standard error, confidence interval or bootstrap probability in this diagnostic. Policies share families, fits share training labels, and repetitions within families are clustered; 240 selected-policy trajectories per group are not independent evidence units. Family-first paired means retain that dependence in aggregation. Per-rollout differences/ranges are dispersion descriptions, not uncertainty intervals or independent replications. Without justified sampling assumptions and coverage validation, suppressing numerical inferential uncertainty is preferable to an IID trial/pair bootstrap. Generalization beyond these selected families/policies remains unquantified. Selection optimism, prior exposure, sparse changing families and recovery missingness limit even held interpretation.

The reversed training split overlaps the original data and is not independent replication. It is excluded from this budget and cannot trigger a second search. A future sensitivity would need a separate prospectively fixed label and contract; none is authorized by this design.

## Implementation, validation and exact handoff

`reversal.py` is a pure in-memory selection/evaluation library with no data loaders, model refits or execution entry point. Its strict production dimensions also apply to generated synthetic panels. `test_reversal.py` covers true crossing, same-sign heterogeneous effects failing in training and evaluation, small effects, ties, order invariance, empty/overlapping/duplicate groups, nonfinite input and rollout/model/orientation/Stage B leakage boundaries. It deliberately does not claim that provenance strings prove source isolation.

Run locally with the supplied NumPy/pytest Python:

    python -m pytest -q -p no:cacheprovider review/reversal_diagnostic/test_reversal.py

Supervisor's exact next action: review this fixed contract and synthetic validation, then dispatch one separate bounded **private reconstruction-and-seal adapter stage**, with no empirical refits, using only the two existing C checkpoints and frozen metadata. That stage must verify train-only reconstruction and seal either the single selection or a no-go before any held read. Only a subsequent supervisor-authorized evaluation may consume the sealed pair once. No further PR consultation is required. Do not run selection/evaluation from this design task, publish this bundle, or change frozen sources, paper/Q3 workspaces or program/controller state.
