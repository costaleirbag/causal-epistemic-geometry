"""CPU-only aggregate audit of existing sealed scores; no response values exported."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def read(path, expected):
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, "SOURCE_HASH_MISMATCH"
    return [json.loads(line) for line in raw.splitlines()]


def key(row):
    return row["family_id"], row["rollout_index"]


def audit(args):
    scores = read(args.scores, "30dd57131b3f0823df1642e2dabb0d511e10c8fe8acf49e0e98c53100df7b0b0")
    old = read(args.champion, "c3b4ab47cf2422afb311fa978496e2abfbe5485ac76040ee3dcead2986ace533")
    old = {key(r): r for r in old if r["condition"] == "V4_DIRECTION_02_MEDIUM"}
    data = read(args.dataset, "c791e38c29d36a43fbac8ce00412e4c77d533665e0b8cb9eef8fa12fb918ac1d")
    data = {r["family_id"]: r for r in data}
    prompts = read(args.prompts, "17a2634a0f8f56e9ea6b7aefadcc640c3086ed134fc5689a4fae540a30fd6a8b")
    prompts = {r["family_id"]: r for r in prompts}
    wrappers = read(
        args.journal, "9ca08598dc81c3414394951cb56cbfc129466c63cb8e5570f208551a3640240d"
    )
    rows = {key(w["row"]): w["row"] for w in wrappers}
    assert len(scores) == len(old) == len(rows) == 600
    assert len(data) == len(prompts) == 300
    assert {key(s) for s in scores} == set(rows) == set(old)
    bykey = {key(s): s for s in scores}
    tables = {}
    for typ in sorted({r["reference_type"] for r in data.values()}):
        subset = [s for s in scores if data[s["family_id"]]["reference_type"] == typ]
        counts = Counter(s["canonical_value"] for s in subset)
        families = {s["family_id"] for s in subset}
        tables[typ] = {
            "rows": len(subset),
            "unique_canonical_answers": len(counts),
            "modal_answer_count": max(counts.values()),
            "predicted_type_counts": dict(Counter(s["value_type"] for s in subset)),
            "rollout_agreement_families": sum(
                bykey[(f, 0)]["canonical_value"] == bykey[(f, 1)]["canonical_value"]
                for f in families
            ),
            "families": len(families),
            "champion_answer_agreement_rows": sum(
                s["canonical_value"] == old[key(s)]["canonical_value"] for s in subset
            ),
            "correct": sum(s["correct"] for s in subset),
        }
    checks = {
        "dataset_prompt_matches_families": sum(
            p["prompt"] == data[f]["prompt"] for f, p in prompts.items()
        ),
        "source_complete_in_prompt_families": sum(
            data[f]["source"] in p["prompt"] for f, p in prompts.items()
        ),
        "input_complete_in_prompt_families": sum(
            repr({k: data[f]["input_value"][k] for k in ("n", "values", "text")}) in p["prompt"]
            for f, p in prompts.items()
        ),
        "source_prompt_hash_matches": sum(
            hashlib.sha256(p["prompt"].encode()).hexdigest() == p["prompt_sha256"]
            for p in prompts.values()
        ),
        "distinct_source_prompt_hashes": len({p["prompt_sha256"] for p in prompts.values()}),
        "row_source_prompt_matches": sum(
            r["prompt_sha256"] == prompts[r["family_id"]]["prompt_sha256"] for r in rows.values()
        ),
        "distinct_rendered_prompt_hashes": len(
            {r["condition_metadata"]["prompt_hash"] for r in rows.values()}
        ),
        "distinct_seeds": len({r["seed"] for r in rows.values()}),
        "raw_output_hash_matches_scores": sum(
            hashlib.sha256(r["raw_output"].encode()).hexdigest() == bykey[k]["raw_output_sha256"]
            for k, r in rows.items()
        ),
    }
    # Tokenizer-only replay: never instantiate a model or call generation.
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    rendered_matches = decoded_matches = content_preserved = 0
    for f, p in prompts.items():
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": p["prompt"]}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        content_preserved += p["prompt"] in rendered
        digest = hashlib.sha256(("rendered_prompt\x1f" + rendered).encode()).hexdigest()
        for rollout in (0, 1):
            r = rows[(f, rollout)]
            rendered_matches += digest == r["condition_metadata"]["prompt_hash"]
            decoded_matches += (
                tokenizer.decode(r["generated_token_ids"], skip_special_tokens=True)
                == r["raw_output"]
            )
    checks.update(
        rendered_hash_reproduction_rows=rendered_matches,
        token_decode_reproduction_rows=decoded_matches,
        complete_prompt_preserved_families=content_preserved,
    )
    return {
        "evidence_level": "POST_HOC_DIAGNOSTIC_ONLY",
        "by_expected_type": tables,
        "provenance": checks,
        "new_model_forwards": 0,
        "individual_values_exported": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("scores", "champion", "dataset", "prompts", "journal", "model"):
        parser.add_argument("--" + name, required=True)
    print(json.dumps(audit(parser.parse_args()), indent=2, sort_keys=True))
