# Existing-data component and input-copy diagnostic

Post-hoc description only; no primary score changed. Sources are hash-pinned in `COMPONENT_COPY_AGGREGATE.json`. The companion script accepts private input paths, prints aggregates only, and performs no model inference or program execution. It preserves the arithmetic of the privately reviewed analysis while exposing paths as CLI arguments.

Both conditions reproduce the original input text in all 128 string answers. The 52 correct text components occur precisely where the original text equals the final reference; all 76 components requiring a different text are incorrect. This is not full-answer accuracy: complete string answers remain incorrect.

The unsteered accumulator component is correct in 0/344 structured answers; the champion has 3/344. Invariants can be correct without following transformations: dictionary size is correct in 64/64 for both, and tuple text length in 56/64 unsteered. Dictionary text has three transformed-component successes per condition (44 trajectories requiring change), so universal copying is not established.

Twenty-eight aggregate strata were reconciled. Denominators depend on references, never model success. Structural failures count as component errors. The fourth list element occurs in 35 families/70 trajectories. Strings are split at the last colon. Strict type tags are retained. This is not a new independent key audit: full input hashes tie to the previous sealed-file audits, which establish key/rollout integrity. Neither components nor rollouts are independent observations.

These findings narrow the question to reproducing visible information versus correctly applying transformations. They do not identify model internals or establish depth, prompt, or steering as the cause. More subgroup searching is not required. Historical Q3_FRESH_INSTRUMENT_NOT_QUALIFIED and confirmatory NOT_RUN remain unchanged. No private prompts, answers or identifiers are released.
