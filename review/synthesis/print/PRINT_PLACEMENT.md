# Generic 7-inch print placement

This single version comprises three separate 7 x 9 inch pages/panels, A, B, C,
in that order. The PDF MediaBox is 504 x 648 points on every page. Place each
page at exactly 7 inches wide and 9 inches high (100% scale), without cropping
or fit-to-page reduction. Allocate three figure pages; keep the caption on an
adjacent text page. This is generic document packaging, not venue compliance.

Prefer the vector PDF. For LaTeX, use graphicx with
`\includegraphics[page=1,width=7in]{explanatory_figure_print.pdf}` and repeat
with page=2 and page=3 on separate pages. Ensure the text area accommodates
7 x 9 inches. In a word processor use the PNGs in order:
`explanatory_figure_print.png` (A), `explanatory_figure_print_B.png` (B),
`explanatory_figure_print_C.png` (C); lock aspect ratio and set width 7 inches.
Each PNG is 2100 x 2700 pixels at 300 dpi. Do not insert all three side by side
or shrink the whole three-page set onto one page. Typography is 9 pt minimum
at the specified size, independently checked in embedded PDF font operators;
pixel density alone is not the readability criterion. A future narrower layout
requires a new physical-size review (9 pt becomes 8 pt at 6.222 inches wide).

## Reproduction and provenance

From the repository root, with Python and matplotlib installed:

```sh
python review/synthesis/plot_explanatory_figure_print.py --output-dir NEW_DIRECTORY
```

The output directory must not exist. The script resolves inputs relative to
its repository location and uses a temporary matplotlib cache. It reads only
`review/model_comparison/MODEL_COMPARISON_RESULTS.json` (pinned SHA256 in code)
and `review/synthesis/PLOTTED_VALUES.csv`. It performs aggregate arithmetic,
not model fitting. It checks all 54 rows and 108 log-loss/Brier values exactly
against the original CSV, retaining its order. Brier remains in the unchanged
CSV; it is not plotted on the nats axis. Original exports and caption are unchanged.
The validation records automated geometry/font checks and separate human visual
inspection of all PDF pages rendered at 100 pixels/inch (700 x 900 pixels per
page), an actual-size-equivalent raster for a 100-ppi display. Physical display
size depends on monitor scaling; print/use the PDF at 100% for physical output.
The inspection found legible labels, separate legends and axis titles, visible
negative points, all controls, and no clipping. No physical printer proof is claimed.
Reproduction resets the human visual-QA field to pending, requiring inspection
of any regenerated delivery. Release only the exact additional manifest payload;
existing CSV, caption and published JSON are unchanged dependencies.

## Accompanying caption (unchanged)

Predictive improvements depend on the comparator and the information available at prediction. **A**, new repetitions of known policies and families: reduction in log loss from Rasch R to positive-discrimination model D, and from D to coordinate-interaction model C, for original and both random orientations. Both directions of the four-rollout split and all three fixed penalties are shown. The generic monotonic model materially improves on Rasch in the original orientation; additional coordinate improvement is sensitive to penalty and split and also occurs in random orientations. **B**, controller exclusion on known families: reduction in log loss from coordinate-global G to family-varying rank-one H, aggregated over all twelve held-controller folds, for all orientations and penalties. Every label from the predicted controller is excluded from training and coordinate centering uses only the other eleven. Each family nevertheless supplies 88 responses from those policies before prediction of the twelfth; this is not new-task prediction. **C**, assignment sensitivity: actual G−H improvement minus permuted G−H improvement for each of the three executed coordinate permutations in each orientation, at lambda 1 only. Controls compare increments because permutation changes both G and H. Positive values favor the candidate in A/B and the actual assignment in C. Filled circles mark primary lambda 1 estimates in A/B; open triangles and squares mark penalty sensitivities .25 and 4. These points are specifications, not confidence intervals. Panel C's labeled diamonds are descriptive assignment controls, not a permutation significance test. Loss reduction is measured in nats per trial, aggregated family-first; it is not accuracy gain. The full robust-benefit rule failed. The same-mask family-only comparator F_B was not executed, so B cannot establish value beyond family knowledge alone. In original/Random 1/Random 2, 42/42/43 of 60 families had homogeneous observed outcomes, not proven deterministic probabilities. Claims C13–C14; sources pinned above.
