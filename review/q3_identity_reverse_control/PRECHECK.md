# Identity versus reversal: final bounded engineering control

Authorized 2026-09-09: six synthetic ASCII inputs, identity/reversal, two rollouts = 24 planned generations once, Qwen unsteered, existing runtime and typed parser. Fixtures are permanently excluded from every scientific evaluation. No historical population is changed or reopened.

MANIFEST.json records prompts, hashes, paired seeds, counterbalanced condition order, frozen model/generation settings, source hashes and stopping rule. REFERENCES.json is CPU-verified using fixed Python functions and independent direct/reversed constructions; collection never loads this file, and the existing model_item passes a reference-unavailable placeholder. No target is supplied to the backend.

Primary description: complete correct pairs out of 12 (six inputs and two repetitions), not 24 independent tasks. Report identity/reversal accuracy, reversal copying, validity/evaluability, termination, tokens and generation durations. Perfect 12/12 is a pass on these fixtures only; otherwise inspect only these outputs and stop without tuning or more generations. No statistical significance or general reliability claim. Passing cannot establish why the old population failed.

Implementation reuses build_backend/model_item, mechanical repetition termination, SingleWriterJournal and existing classify/summary functions. It adds a bounded panel adapter, not a new framework. Four CPU-only tests passed: paired fixtures/reference construction, exact successful pair scoring, copy-only failure, and rejection of altered raw bytes before scoring. Journal seal precedes scoring. No automatic retries or second panel.

After this check, stop this diagnostic. Do not use confirmation/reserve, other models/prompts, steering, new difficulty curves or additional infrastructure. Q3_FRESH_INSTRUMENT_NOT_QUALIFIED and Q3 NOT_RUN remain preserved.
