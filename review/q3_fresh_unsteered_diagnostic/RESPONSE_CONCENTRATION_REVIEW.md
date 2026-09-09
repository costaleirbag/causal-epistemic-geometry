# Q3.4 response concentration and interface review

POST_HOC_DIAGNOSTIC_ONLY. Closed qualification and unsteered results remain unchanged. This audit used existing sealed records and CPU tokenizer replay, with zero model forwards.

## Discriminative finding

Identical correctness does not mean identical answers. All 128 Boolean responses used one canonical value and agreed with the champion. That constant response accounts for all 80 correct rows. Non-Boolean responses were diverse, matched their expected types, but were all incorrect. Across all types, only 146/600 answers agreed with the champion; outside Booleans, agreement was 18/472 (3.81%). Independent seeds preclude treating individual disagreement as an execution defect.

| Expected type | Rows | Unique answers | Modal count | Same answer across rollouts (families) | Same answer as champion | Correct |
|---|---:|---:|---:|---:|---:|---:|
| bool | 128 | 1 | 128 | 64/64 | 128 | 80 |
| int | 128 | 38 | 36 | 15/64 | 14 | 0 |
| str | 128 | 118 | 3 | 3/64 | 2 | 0 |
| list | 88 | 87 | 2 | 1/44 | 2 | 0 |
| dict | 64 | 64 | 1 | 0/32 | 0 | 0 |
| tuple | 64 | 64 | 1 | 0/32 | 0 | 0 |

Predicted and expected types matched in 600/600 rows. No individual canonical value is released. The evidence supports Boolean response collapse and successful type/format production without exact computational success. It does not establish general content insensitivity, a model mechanism, or difficulty as the cause. Diverse incorrect outputs could still depend strongly on program content.

## Interface and provenance

All five sealed source hashes were checked before analysis. The 300 private source prompts were distinct, matched their dataset prompts, and contained the complete source and input. All 600 source hashes matched journal provenance, all 600 seeds were distinct, and CPU replay of the local tokenizer reproduced all 600 recorded rendered-prompt hashes. Decoding persisted generated tokens reproduced all 600 raw outputs and their score hashes.

Code review at the closed lineage: `model_item` assigns the supplied prompt directly; `render_prompt` passes it as the user message with generation prompt and `enable_thinking=False`; `_encode_item` supplies no truncation option; `generate_reasoning` decodes only `generated[0, input_length:]`. The scorer extracts FINAL, canonicalizes predicted and reference values independently, and compares tagged values exactly (including Boolean versus integer distinction).

These checks find no prompt omission, accidental shared input, output-decoding mismatch, or type-comparison mismatch. They do not independently prove the correctness of all reference computations, nor reconstruct unrecorded model internals. Token replay verifies persisted output decoding, not every internal generation operation. Semantic evaluability means parseability in this parser; expected-type matching was checked separately here.

## One proposed next test — not executed

Use an excluded synthetic fixture panel to test **input-value sensitivity** while holding code, output type, wrapper, model and generation settings fixed. Proposed size: six trivial typed identity programs, two input values per program, two rollouts = 24 unsteered generations. Choose each pair so exact outputs must differ; balance the Boolean pair. Dual CPU references establish outputs before any model call. The original wrapper and frozen parser serve as positive controls for simple execution and answer-channel handling. Change only the input value within each pair. Report exact correctness and whether outputs change in the required direction; no inferential claim or Q3 gate.

If trivial controls pass, the interface works for those fixtures and complexity becomes a better candidate for a later isolated test. If they fail or ignore input changes, investigate elementary input interpretation/presentation before any costly portfolio run. Failure would not by itself prove a parser defect. This proposal neither changes the generator nor authorizes new inference.

## Sources and boundary

- [Closed diagnostic](Q3_FRESH_UNSTEERED_DIAGNOSTIC_CLOSEOUT.md), commit `ccfc2f4f59313f2c0018f009e8d0162f83d1cac0`.
- [Aggregate audit](RESPONSE_CONCENTRATION_AGGREGATE.json).
- [Reproduction script](../../scripts/audit_q3_unsteered_response_concentration.py), containing the five expected private source hashes; all private paths supplied as CLI arguments.
- [Prompt constructor](../../scripts/execute_q3_fresh_qualification.py), [chat renderer](../../src/epistemic_geometry/benchmarks/prompts.py), [backend](../../src/epistemic_geometry/backends/huggingface.py), [typed scorer](../../src/epistemic_geometry/benchmarks/external/semantic_v3.py).

No raw text was manually displayed, no individual values exported, no GPU used, no confirmation/reserve accessed. Q3_FRESH_INSTRUMENT_NOT_QUALIFIED and Q3 confirmatory NOT_RUN remain preserved. No follow-up was launched.
