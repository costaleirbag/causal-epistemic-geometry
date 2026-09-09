# Matched-orientation pilot: prospective protocol

Status: prospectively frozen by PILOT_PRECHECK.json before pilot vector draws or new model inference. This is an exploratory finite-orientation intervention study on an already exposed task population, not Q3 confirmation. Q3 remains closed.

## Question and limits

Does the constructed rank-eight subspace have stronger observable angular/error-profile alignment than two generic rank-eight orientations? Under a local response p_i(c) approximately a_i+b_i^T c, family-centered response distance is (c-d)^T Cov(b_i)(c-d). An approximately isotropic covariance yields proportionality to 1-cos(c,d) even without a privileged semantic subspace. Thus a positive angular correlation alone is insufficient evidence of specificity.

Compare the original frozen 4096-by-8 basis with two Gaussian-QR isotropic ambient orientations. Root seed 2026090941; coefficient and orientation generators and label-derived seeds are fixed in code. Draw 24 shared normalized Gaussian coefficient vectors once. All three vector banks have the identical coefficient Gram matrix. Reject algebraic degeneracy without drawing replacements. Use the same layer-27 output sustained-current-token hook, one MEDIUM target amplitude 0.25, model/tokenizer bytes and serial BF16 generation regime inherited from Q2. No model, prompt, parser or terminal-rule change.

## Separate qualification and evaluation

Use the existing 12 calibration families, disjoint from the old 300-family evaluation panel. Collect two rollouts of baseline and all 72 interventions: 1,752 trajectories. Calibration uses common random seeds across conditions within family/rollout. Twelve baseline denominator prefills are separate from semantic trajectories. Implemented amplitude is calibrated using the inherited BF16 bisection, with relative error at most 0.005. Conditions are shuffled within family/rollout.

Baseline validity and evaluability must each reach 0.90. Each intervention must have validity and evaluability at least max(0.90, baseline-0.05), terminal-failure/truncation rate at most 0.05, raw token-sequence difference from its matched baseline at least 0.10, and qualified amplitude. This is a weak activity screen, not proof of equal semantic effect or response signal. No reference correctness is inspected for qualification.

Take the first at most 12 coefficient indices passing in all three spaces, in original draw order. Require at least eight common indices and coefficient rank eight. Report all attrition. No new directions, seeds, orientation replacement or threshold relaxation after qualification. Failure ends the pilot as qualification-inconclusive; it does not favor original geometry.

Select 60 of the already exposed 300 evaluation families by the fixed seed/hash ordering, independent of scores. For every selected family collect eight independent condition-specific rollouts of baseline and the retained interventions. At 12 retained indices: 17,760 evaluation trajectories, 19,512 including qualification. At eight: 12,000 evaluation trajectories. Evaluation seeds are hash-derived with deterministic collision resolution; all conditions use the same families and rollout counts. Original and baseline controls are contemporaneous. There is no reuse of historical answers.

## Precision and compute choice

The frozen CPU planning simulations compare 100 families/four rollouts with 60 families/eight rollouts, using logistic local-response scenarios, matched coefficient banks and weak/moderate/strong response scales. They are scenario checks, not an estimated power guarantee. More rollouts reduced attenuation/error in the tested moderate and strong settings, motivating 60-by-eight. Weak effects remain hard to distinguish, and unequal attenuation can imitate specificity. Both scenario outputs and simulator are retained.

Operational ceiling: 20,000 new semantic trajectories and 72 elapsed execution hours. Maximum planned count is 19,512, leaving 488 for explicitly documented operational missing-key recovery, never discretionary scientific extensions. Historical per-row durations of approximately 1.77–8.22 seconds imply approximately 9.6–44.6 hours for the maximal planned schedule, plus loading/verification overhead; new orientations may run slower. A persistent outer timeout enforces 72 hours, including loading and interruptions within that run. An expired/incomplete collection is inconclusive and must not be analyzed as complete. Persist actual usage. No paid compute, second device, reserved families or opportunistic extension.

## Estimands and decisions

For each space, let Y[i,k,r] be binary correctness, invalid responses scored zero. For each controller pair form d[i,r]=Y[i,k,r]-Y[i,l,r], subtract its family mean separately in each rollout, then estimate the mean across families of the average product over distinct rollout pairs. This U-statistic estimates finite-panel family-centered squared response differences under independent rollouts. Retain negative noisy estimates. Do not treat controller-pair entries as independent samples.

Primary observable: Spearman correlation between pairwise 1-cos coefficient geometry and estimated response differences. Primary contrast is original correlation minus the mean of the two random-space correlations. Use 2,000 paired family bootstrap resamples and fixed bootstrap seed in source. The interval is conditional on these coefficients and two orientations; it is not an interval over the population of random subspaces. Family resampling treats the selected exposed families as a sample; it does not create unseen-task confirmation.

Predeclared descriptive classification:
- lower 95% bootstrap endpoint greater than +0.15: OBSERVABLE_ALIGNMENT_HIGHER_FOR_ORIGINAL;
- interval strictly inside [-0.15,+0.15] and all three point correlations greater than 0.30: COMPARABLE_RELATIONAL_ALIGNMENT_IN_TESTED_ORIENTATIONS;
- otherwise: INCONCLUSIVE_SPECIFICITY_CONTRAST.
Undefined correlations or more than 5% degenerate bootstrap draws yield the corresponding degeneracy-inconclusive label. Baseline evaluation validity/evaluability below 0.90 or any space aggregate below max(0.90, baseline-0.05) overrides the result with INCONCLUSIVE_EVALUATION_CHANNEL_CONFOUND, preserving the association-only label separately.

Report accuracy, validity/evaluability, mean displacement, all-rollout doubly-centered cross-rollout stable product and energy ratio, and four-versus-four rollout associations. A higher original observable correlation alone does not isolate latent causal specificity: unequal response scale/repeatability and signal-to-noise attenuation remain alternatives. Comparable alignment only supports the generic explanation within these tested orientations; neither outcome proves universality or deployment benefit. No router is trained.

## Execution and audit

Hash-pin protocol, source, basis/split manifests, private official source identity and qualified model-byte manifest before preparation. Retain generated vectors/schedules privately with hashes. Exclusive collector lock, deterministic schedule identity, flush/fsync journal, and immutable deployment binding prevent duplicate collection and silent changes. Restart only missing predeclared keys after inspecting an operational failure; preserve all complete rows and document potentially completed but unpersisted attempts. Never rerun a persisted unfavorable answer. Stop automatically on exceptions; supervisor diagnoses them without changing the scientific design.

Qualification follows its complete raw seal. If qualified, evaluation follows immediately without manual permission. Correctness scoring follows full evaluation raw seal and exact on-disk key/hash verification. No interim correctness dashboard or outcome-based stopping. Independently audit numerical estimates and counts before interpretation/publication. Release code, protocol and safe aggregates only; individual prompts, answers, identities, vectors and operational infrastructure remain private. Publish an honest bounded conclusion, including qualification or precision failure when applicable.
