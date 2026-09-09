# Q3.4 unsteered diagnostic closeout

The unsteered Qwen3-8B baseline reproduced the frozen champion's complete correctness pattern on this qualification population: both scored 80/600 (13.33%), with exactly the same 80 correct family/rollout keys. Removing steering did not restore observed competence on these tasks.

This is a **post-hoc diagnostic**, not a confirmatory evaluation. `Q3_FRESH_INSTRUMENT_NOT_QUALIFIED`, `Q3_FRESH_INSTRUMENT_QUALIFICATION_FORENSIC_CLEAN`, and Q3 confirmatory `NOT_RUN` remain unchanged.

## Results

| Measure | Unsteered | Historical frozen champion |
|---|---:|---:|
| Correct / trajectories | 80/600 | 80/600 |
| Accuracy | 13.33% | 13.33% |
| Valid and evaluable | 600/600 | 600/600 |
| Boolean correct / trajectories | 80/128 | 80/128 |
| Non-Boolean correct / trajectories | 0/472 | 0/472 |
| Generated tokens | 7,007 | 7,152 |
| Sum of persisted generation durations | 725.64 s | 735.42 s |

Correct-set intersection and union both equal 80; neither condition has an exclusively correct key. The observed accuracy difference is zero. Runtime numbers summarize persisted successful generations, not total experiment wall time; they exclude model loading, interruptions, and unpersisted attempts. They do not establish a performance speedup.

The comparison uses the same 300 qualification families and two rollouts per condition, with independently frozen diagnostic seeds. Rollout indices align records, but do not imply common random numbers. These 600 trajectories are not 600 independent families. No equivalence test or general equivalence claim is made.

## Interpretation and next decision

The low accuracy is also present without activation steering. This weakens an explanation in which steering alone caused the competence collapse. It does not identify whether task density, prompt design, model competence, or another shared feature caused the failure, nor prove identical answers or internal computation. In particular, correctness overlap alone does not establish that the baseline emitted a constant Boolean literal.

This diagnostic offers no basis for reopening confirmation or tuning the router on this population. A useful next research decision would be a small, explicitly exploratory examination of task/prompt suitability before investing in another routing campaign. That is a proposal for a separate iteration; no new inference or instrument tuning was initiated here.

## Provenance and validation

- Execution and scorer frozen at commit `5c866334004d99fb9688a3bb681d40c969515003`.
- Frozen scorer SHA-256: `bbf3af700d923f6b9c9131424fb260492d57a2b21ef39daefc65c1e83512ee79`.
- Final raw journal SHA-256: `9ca08598dc81c3414394951cb56cbfc129466c63cb8e5570f208551a3640240d`.
- Private score SHA-256: `30dd57131b3f0823df1642e2dabb0d511e10c8fe8acf49e0e98c53100df7b0b0`.
- Frozen scorer verified input hashes, schedule identities, raw seal, full coverage, parser, and historical comparator provenance before releasing aggregates.
- Separate mechanical validation confirmed 600 unique keys, score totals, journal/score hashes, token total, and byte-for-byte preservation of both pre-resume prefixes.
- Correctness first inspected after the complete raw seal. No manual adjudication or scientific code changes.

## Operational record

An initial environment check failed before model loading and was corrected without scientific changes. During collection, the unchanged journal integrity guard stopped the process at 330 and 356 persisted rows following metadata changes. The actor responsible for those changes was not established. Each prefix was mechanically audited, privately snapshotted, and preserved byte for byte; the unchanged runner resumed only missing scheduled keys with their original seeds. No persisted trajectory was replaced. A generation attempted before an append failure may have been reexecuted because its key was absent; therefore the release field `retry_rows: 0` describes persisted journal bookkeeping, not proof of zero additional model executions. These two operational resumes were not outcome-driven.

Raw outputs, individual scores, snapshots and operational receipts remain private. Confirmation and reserve had zero Qwen access; no historical condition was reexecuted. No Spark 2, RunPod, paid inference, retuning, or new candidate was used.

See [machine-readable aggregate](Q3_FRESH_UNSTEERED_DIAGNOSTIC_RESULT.json).
