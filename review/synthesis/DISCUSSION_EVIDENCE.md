# Discussion evidence index

This local discussion draft uses the published source snapshot `6780ee36276241d2447cb81d67a53f023ba64a70`. Existing manuscript drafts, scientific code, source results and figures are preserved. No fitting or inference was performed. The revision response contains SHA256 identities and source-commit equality checks; those checks establish provenance, not independent scientific validation.

| Question | Exact verification |
|---|---|
| Q2 directions | `finalize_source`: paired positive-minus-negative mean activation differences, four instruction families × two capture boundaries; `retained_subspace`: normalized columns, SVD, retained orthonormal basis. |
| Q2 intervention and dose | Output forward hook at layer 27; final prompt/current decode token; BF16-rounded perturbation norm relative to baseline reference RMS; MEDIUM 0.25 and STRONG 0.50. |
| Generation regimes | Q2 normative lock plus OOS terminal rule; Q1 identity lock separately records Qwen D75 and Ministral D25 and their differing temperatures/top-k. No common router regime inferred. |
| Q1 uncertainty | `models.Qwen.estimands.MEANINGFUL_FIXED.C`, `models.Qwen.delta_C_nullmean`, and `models.Qwen.intervals` in CONFIRMATORY_RESULTS.json; REPORT.md gives rounded endpoints. PROTOCOL_LOCK.md specifies 50,000 item-percentile bootstrap resamples and joint criteria. No new coverage validation. |
| Q2 central figure | Existing main PNG/PDF/SVG hashes match SOURCE_MANIFEST.json. Visual inspection confirms all 16 positions, correlated shell lists and their average, descriptive global panel and secondary ±1 SE panel. The CSV average and positive count were checked directly. |
| Print | Existing three-page PDF and three raster pages retained byte-for-byte; PRINT_PLACEMENT.md specifies 7 × 9 inches and archived 9-pt minimum. No redraw, printer proof or venue certification. Use the shorter Figure 2 caption in the discussion manuscript. |
| Q3 transfer | Postmortem section 4: median 57 versus 5 source lines, 600 versus 39 AST nodes. Qualification failed; confirmation was not run. |
| Recovery | Missing prespecified keys completed by documented reexecution; original persisted byte prefixes preserved. No claim of recovering absent original bytes, no inferred root cause. |

## Primary code and protocol pointers

- source_construction: [scripts/run_q2_v4_presemantic.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/scripts/run_q2_v4_presemantic.py).
- source_boundaries_and_amplitude: [scripts/run_q2_v3.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/scripts/run_q2_v3.py).
- subspace_SVD: [src/epistemic_geometry/experiments/q2_v4_presemantic.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/src/epistemic_geometry/experiments/q2_v4_presemantic.py).
- coefficient_draw: [src/epistemic_geometry/experiments/q2_oos_fresh_controller.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/src/epistemic_geometry/experiments/q2_oos_fresh_controller.py).
- output_hook: [src/epistemic_geometry/backends/huggingface.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/src/epistemic_geometry/backends/huggingface.py).
- Q2_generation: [review/q2_v4_1_prediction_lock/Q2_V4_1_NORMATIVE_EXECUTION_AND_ANALYSIS_LOCK.md](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q2_v4_1_prediction_lock/Q2_V4_1_NORMATIVE_EXECUTION_AND_ANALYSIS_LOCK.md).
- OOS_final_protocol: [review/q2_oos_fresh_controller_design/v2_final_presemantic/V2_FINAL_PROTOCOL_LOCK.json](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q2_oos_fresh_controller_design/v2_final_presemantic/V2_FINAL_PROTOCOL_LOCK.json).
- OOS_terminal_rule: [scripts/run_q2_oos_v2_semantic.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/scripts/run_q2_oos_v2_semantic.py).
- Q1_identity: [review/q1_confirmatory_fixed_controllers/CONTROLLER_IDENTITY_LOCK.json](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q1_confirmatory_fixed_controllers/CONTROLLER_IDENTITY_LOCK.json).
- Q1_intervals: [review/q1_confirmatory_fixed_controllers/CONFIRMATORY_RESULTS.json](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q1_confirmatory_fixed_controllers/CONFIRMATORY_RESULTS.json).
- Q1_interval_procedure: [review/q1_confirmatory_fixed_controllers/PROTOCOL_LOCK.md](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q1_confirmatory_fixed_controllers/PROTOCOL_LOCK.md).
- Q1_report: [review/q1_confirmatory_fixed_controllers/REPORT.md](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q1_confirmatory_fixed_controllers/REPORT.md).
- Q3_population: [review/q3_fresh_instrument_qualification_postmortem/Q3_4_QUALIFICATION_FAILURE_BEHAVIORAL_POSTMORTEM.md](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/q3_fresh_instrument_qualification_postmortem/Q3_4_QUALIFICATION_FAILURE_BEHAVIORAL_POSTMORTEM.md).
- repeatability: [review/geometry_specificity/REPEATABILITY_REPORT.md](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/review/geometry_specificity/REPEATABILITY_REPORT.md).
- Q2_plot_source: [src/epistemic_geometry/publication/q2_oos/plotting.py](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/src/epistemic_geometry/publication/q2_oos/plotting.py).
- Q2_figure_provenance: [manuscript/figures/paper1_q2_oos/SOURCE_MANIFEST.json](https://github.com/ACS-USP/causal-epistemic-geometry/blob/6780ee36276241d2447cb81d67a53f023ba64a70/manuscript/figures/paper1_q2_oos/SOURCE_MANIFEST.json).

## Focused bibliography additions

Only three gaps were checked in this pass: [ActAdd v5](https://arxiv.org/abs/2308.10248v5), [CAA v4](https://arxiv.org/abs/2312.06681v4), and the [MoSV README](https://github.com/lee-dan/Mixture-of-Steering-Vectors-MoSV), accessed 2026-09-10. The arXiv primary metadata/abstracts support the brief operation descriptions; MoSV's README supports the bank/prompt-hidden-state-router architecture. No external performance or priority claim was imported. Other references retain the preceding draft's verification.

## Remaining scientific and production limits

Same-mask family-only F_B was not executed; complete robustness failed; specificity remains inconclusive; conditional sign inference assumes independent eligible-controller signs given the panel and atlas. Q1 intervals retain their original procedure and are separate from the Q2 item-bootstrap ruling. Figure 1 has not received a new physical-size print review. The publication owner must independently review the exact local payload; no correspondence, commit or push occurred. This finite editorial stage does not guarantee acceptance or readiness for any particular venue.
