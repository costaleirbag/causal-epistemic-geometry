# Family baseline closeout

Operational audit: **passed**. Independent arithmetic verified all 2,160 family-fold roots, 17,280 held outcomes, 432 saved G/H folds and 36 comparison groups on log loss and Brier. Exact 17,760-row schedule/score coverage includes the 480 excluded BASELINE rows. All frozen input/source hashes and private checkpoint/output hashes remained unchanged. No inference, rescoring, H/G refitting or push.

The checker imports no fitting/extension modules. It constructs masks from ordered sealed keys, solves scalar roots using a separate bracket, and reconstructs frozen G/H predictions from recorded starts, training-centered coordinates and normalized right factors. All saved per-family metrics and paired summaries agree within 1e-10. Maximum per-family loss discrepancy: 1.1973e-12; root residual: 1.9325e-14. All 18 G/H setting pairs satisfy F−H=(F−G)+(G−H), maximum cell discrepancy 4.4409e-16. Historical G−H rows are exactly preserved.

Positive differences below favor the named model over F_B. Log loss is nats/trial; Brier is unscaled. Primary setting is actual coordinates, penalty 1; .25 and 4 are the frozen sensitivities.

| Orientation | Penalty | F−G log loss | F−H log loss | F−G Brier | F−H Brier |
|---|---:|---:|---:|---:|---:|
| ORIGINAL | 1 | +0.00261933 | +0.01489009 | -0.00003617 | +0.00457787 |
| ORIGINAL | 0.25 | -0.00025857 | +0.00422012 | -0.00103749 | +0.00307077 |
| ORIGINAL | 4 | +0.00477786 | +0.01369742 | +0.00072238 | +0.00383787 |
| RANDOM_1 | 1 | -0.01241304 | -0.01017676 | -0.00258937 | -0.00205426 |
| RANDOM_1 | 0.25 | -0.02034756 | -0.02093635 | -0.00422995 | -0.00420164 |
| RANDOM_1 | 4 | -0.00586776 | -0.00477214 | -0.00116899 | -0.00084337 |
| RANDOM_2 | 1 | -0.00245876 | -0.00412391 | -0.00022978 | -0.00071560 |
| RANDOM_2 | 0.25 | -0.00678915 | -0.01204111 | -0.00139837 | -0.00227096 |
| RANDOM_2 | 4 | +0.00009043 | +0.00031062 | +0.00039316 | +0.00033336 |

Assignment-control sensitivity (penalty 1): all three frozen permutations are retained below; these are descriptive controls, not additional independent replicates.

| Orientation | Assignment | F−G log loss | F−H log loss | F−G Brier | F−H Brier |
|---|---:|---:|---:|---:|---:|
| ORIGINAL | 1 | -0.01880330 | -0.02905819 | -0.00494551 | -0.00667458 |
| ORIGINAL | 2 | -0.02462727 | -0.02527562 | -0.00654120 | -0.00596620 |
| ORIGINAL | 3 | -0.00158684 | -0.00894622 | -0.00117943 | -0.00252561 |
| RANDOM_1 | 1 | -0.01212565 | -0.01422885 | -0.00319636 | -0.00378596 |
| RANDOM_1 | 2 | +0.00188968 | -0.00197563 | +0.00012102 | -0.00092301 |
| RANDOM_1 | 3 | -0.00040528 | -0.00245779 | -0.00041343 | -0.00129412 |
| RANDOM_2 | 1 | -0.00593941 | -0.00537346 | -0.00184740 | -0.00181883 |
| RANDOM_2 | 2 | -0.00855392 | -0.00609350 | -0.00215016 | -0.00178246 |
| RANDOM_2 | 3 | -0.00817867 | -0.00689315 | -0.00231746 | -0.00235995 |

At the primary setting, H improves over the family constant in ORIGINAL on both metrics, whereas H loses to it in both random orientations. ORIGINAL H retains that advantage at all three penalties; RANDOM_1 H loses at all three, and RANDOM_2 H changes sign at penalty 4. ORIGINAL G has a small primary log-loss advantage but a slightly worse Brier score. Thus the two metrics do not support an undifferentiated claim that any coordinate-based model helps.

A family-only explanation is less sufficient for ORIGINAL held-controller prediction under these known-family masks; additional controller-dependent structure is more plausible there. Family constants remain a competitive explanation in the random orientations. The separate G−H comparison measures incremental modeled interaction; neither that gain nor beating F_B establishes reversals in controller ordering. Penalized pooling, capacity, common qualification, exposed outcomes, unequal signal/noise, shared folds and only two random orientations limit interpretation. These results do not establish population subspace specificity, semantic mechanisms, new-family generalization or deployment utility.

No significance tests, confidence intervals or new scientific thresholds were added. This numerical audit does not erase the historical specificity audit failure or change its inconclusive conclusion. The next scientific decision belongs to the supervisor, including whether a bounded reversal diagnostic is informative; no GPU collection follows automatically.

Artifacts: FAMILY_BASELINE_AUDIT.json, audit_extension_independent.py and the unchanged FAMILY_BASELINE_RESULTS.json. Private counts, identifiers, predictions and per-family differences were not exported.
