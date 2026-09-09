# Final identity/reversal engineering control

**Result: ELEMENTARY_CONTROL_MIXED_OR_FAILED.** Identity was correct in 12/12 generations and reversal in 8/12. Eight of twelve input/rollout pairs had both answers exactly correct. This shows that correct elementary transformation is observable in this configuration; it does not pass the pre-recorded perfect-pair control or establish reliable Python execution.

## What was tested

Six short synthetic ASCII inputs, two functions differing only in `return data["text"]` versus `return data["text"][::-1]`, and two rollouts: exactly 24 planned and persisted generations. Within a pair, input dictionary, wrapper, FINAL contract, model and sampling settings were identical. Seeds were paired across conditions, distinct between input/rollout pairs; condition order was counterbalanced prospectively. These are six engineering inputs and two program templates, not 24 independent scientific tasks. Fixtures are permanently excluded from all scientific evaluations.

The frozen Qwen3-8B backend/tokenizer revision, BF16/SDPA, non-thinking chat mode, temperature 0.6, top-p 0.95, top-k 20, max 4096 tokens, repetition guard, typed parser and corrected SingleWriterJournal were reused. No steering/router hooks were installed. References were verified on CPU before inference and never loaded by collection or passed to the backend.

## Results

| Quantity | Identity | Reversal |
|---|---:|---:|
| Correct | 12/12 | 8/12 |
| Valid/evaluable under frozen parser | 12/12 | 12/12 |
| Generated tokens | 72 | 90 |
| Summed generation durations | 6.950 s | 7.735 s |
| Natural completion | 12/12 | 12/12 |

- Complete correct pairs: 8/12; 4/6 in each rollout.
- Inputs with all four answers correct: 3/6.
- Reversal answers equal to original input: 0/12.
- Hard caps, repetition stops, runtime errors and collection restarts: zero.
- 162 generated tokens; 14.685 seconds of generation, excluding model loading and verification.
- No extra generations or panel were run after scoring.

## Inspection of the mixed result

Only these synthetic fixtures were inspected. The four reversal errors were:

| Synthetic input | Expected reversal | Persisted answer after FINAL | Rollout |
|---|---|---|---:|
| b7K2 | 2K7b | }2K7b | 1 |
| cobalt | tlaboc | 'tablac' | 0 |
| cobalt | tlaboc | 'tablac' | 1 |
| raven9 | 9nevar | 9nevaR | 0 |

The frozen parser accepts bare string answers in this context, so all four are valid/evaluable but wrong. Validity here is not a separate guarantee of strictly quoted Python-literal formatting. No manual adjudication or score change was made.

CPU tokenizer replay reproduced all 24 rendered-prompt hashes and all 24 decodings of persisted generated tokens; complete source prompts were preserved. The 24 logical keys and recorded schedule were verified. No concrete prompt or decoding defect was identified. These checks cannot prove absence of every internal execution issue. No additional model forwards were used for inspection.

## Operational decision and remaining uncertainty

The backend need not be declared incapable of anything beyond copying: eight reversals were correct and none simply copied the input. Conversely, the mixed result does not certify this model/configuration as reliably performing even this elementary panel. No concrete executor defect was identified that would justify changing it in this iteration. Reuse of the execution machinery remains possible, but a future expensive scientific campaign needs its own competence/instrument check; this control supplies no general reliability guarantee.

Do not infer that program length, composition or steering caused the original failure. Do not launch new prompts, models, generation modes or difficulty curves to improve this result. The current population remains closed as a Q3 candidate. This diagnostic ends here; the next scientific project is a separate decision about geometry and efficient portfolio discovery/construction.

## Provenance and scope

- Pre-inference code/manifest commit: `d1f3768`.
- Manifest SHA-256: `a49bf8a29d1b5df9e30ced5e2e4dad01e080d3b7ef741e55881987bfd014d171`.
- Raw journal SHA-256: `141e9b0ea7cbd57a1b4c4a9a40175ed17b7f5a6c8ec9df2c30f6df6b3d48df7e`.
- Scores SHA-256: `7f0c659747e18f24dd1b9c091979f3fc07371ddfd85047841587ca7a26ac0c7f`.
- Seal SHA-256: `0d67ef572b5092f83efd899079ef3f01b03e03a1ef310ca9376331d5772fd753`.
- Four CPU-only software tests passed before collection. Complete raw seal preceded scoring.
- The previously private component/copy aggregate was separately published under direct authorization and reproduced with exact JSON equality from the sealed source files. Its guarantee of scientific key identity remains inherited from prior audits, as documented.

Q1/Q2 and previous Q3 results unchanged. `Q3_FRESH_INSTRUMENT_NOT_QUALIFIED` and Q3 confirmatory `NOT_RUN` preserved. Zero confirmation/reserve model access. No other compute provider, retuning, paper workspace or handbook changes. No open-ended monitoring remains.

[Results](RESULT.json) · [Interface inspection](INTERFACE_AUDIT.json) · [Precheck](PRECHECK.md) · [Manifest](MANIFEST.json)
