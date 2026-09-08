#!/usr/bin/env python3
"""Freeze the post-hoc Q3.4 unsteered diagnostic before model inference."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "review/q3_fresh_unsteered_diagnostic"
QUALIFICATION = ROOT / "review/q3_fresh_instrument_qualification"
MANIFEST = QUALIFICATION / "QUALIFICATION_FAMILY_MANIFEST.json"
HISTORICAL_SCHEDULE = QUALIFICATION / "Q3_FRESH_QUALIFICATION_SCHEDULE.json"
HISTORICAL_LOCK = QUALIFICATION / "Q3_FRESH_QUALIFICATION_EXECUTION_LOCK.json"
RUNNER = ROOT / "scripts/execute_q3_fresh_unsteered_diagnostic.py"
SCORER = ROOT / "scripts/analyze_q3_fresh_unsteered_diagnostic.py"
TESTS = ROOT / "tests/test_q3_fresh_unsteered_diagnostic.py"

SOURCE_CLOSEOUT = "827f4cc8adc8cd89b2cf270a89806950bbf5ac77"
DATASET_SHA256 = "c791e38c29d36a43fbac8ce00412e4c77d533665e0b8cb9eef8fa12fb918ac1d"
PRIVATE_PROMPT_SHA256 = "17a2634a0f8f56e9ea6b7aefadcc640c3086ed134fc5689a4fae540a30fd6a8b"
PARSER_SHA256 = "51ac492a6cea1284c36df6ef659520adf4a04e0595cf0e66bfd15ba172b960c3"
MODEL_REVISION = "b968826d9c46dd6066d109eabc6255188de91218"
MODEL_BYTE_MANIFEST_SHA256 = "cedc88ba2f732baea6bb71f5e6d7f6bc3aad00d302c3456d208a21687c9e069c"
CONDITION = "UNSTEERED_BASELINE_POSTHOC_DIAGNOSTIC"
SEED_NAMESPACE = "Q3-FRESH-QUALIFICATION-UNSTEERED-POSTHOC-V1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def seed_for(family_id: str, rollout_index: int) -> int:
    payload = f"{SEED_NAMESPACE}|{DATASET_SHA256}|{family_id}|{CONDITION}|{rollout_index}"
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big") & ((1 << 63) - 1)


def build_schedule() -> dict[str, Any]:
    manifest = read_json(MANIFEST)
    rows = []
    for family in manifest["families"]:
        for rollout in (0, 1):
            rows.append(
                {
                    "family_id": family["family_id"],
                    "family_order": int(family["order"]),
                    "condition": CONDITION,
                    "rollout_index": rollout,
                    "seed": seed_for(str(family["family_id"]), rollout),
                    "prompt_sha256": family["prompt_sha256"],
                }
            )
    keys = {(row["family_id"], row["condition"], row["rollout_index"]) for row in rows}
    seeds = {int(row["seed"]) for row in rows}
    historical_seeds = {int(row["seed"]) for row in read_json(HISTORICAL_SCHEDULE)["rows"]}
    if (
        len(manifest["families"]) != 300
        or len(rows) != 600
        or len(keys) != 600
        or len(seeds) != 600
        or seeds & historical_seeds
    ):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_SCHEDULE_INVALID")
    return {
        "schema_version": "q3-fresh-unsteered-posthoc-schedule-v1",
        "status": "FROZEN_POSTHOC_NOT_RUN",
        "evidence_level": "POST_HOC_DIAGNOSTIC_ONLY",
        "condition": CONDITION,
        "families": 300,
        "rollouts": [0, 1],
        "logical_generations": 600,
        "seed_namespace": SEED_NAMESPACE,
        "unique_seeds": 600,
        "historical_seed_collisions": 0,
        "rows": rows,
    }


def main() -> None:
    expected = {
        "qualification_manifest_sha256": (
            "9a01142e4825efad36c9ede99cacf88ec6c8cc42d37f24c2ba213bb6c4a790a1"
        ),
        "historical_schedule_sha256": (
            "edba56fc8435cdc34b6f7551fc2d1b4a6d4cc3d87fc34127a5096526d670a635"
        ),
        "historical_lock_sha256": (
            "3a51a8d6d9fe57722f9ca740e1c5281e0645031f1641cb824c469ab4dc36635f"
        ),
    }
    observed = {
        "qualification_manifest_sha256": sha256_file(MANIFEST),
        "historical_schedule_sha256": sha256_file(HISTORICAL_SCHEDULE),
        "historical_lock_sha256": sha256_file(HISTORICAL_LOCK),
    }
    if observed != expected:
        raise RuntimeError(f"Q3_UNSTEERED_DIAGNOSTIC_SOURCE_HASH_MISMATCH: {observed}")
    if not all(path.is_file() for path in (RUNNER, SCORER, TESTS)):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_IMPLEMENTATION_INCOMPLETE")

    REVIEW.mkdir(parents=True, exist_ok=True)
    schedule_path = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_SCHEDULE.json"
    write_json(schedule_path, build_schedule())
    precheck = {
        "schema_version": "q3-fresh-unsteered-posthoc-precheck-v1",
        "status": "FROZEN_POSTHOC_DIAGNOSTIC_NOT_RUN",
        "classification_boundary": {
            "historical_status": "Q3_FRESH_INSTRUMENT_NOT_QUALIFIED",
            "historical_forensic_status": ("Q3_FRESH_INSTRUMENT_QUALIFICATION_FORENSIC_CLEAN"),
            "historical_result_mutable": False,
            "q3_confirmatory_result": "NOT_RUN",
        },
        "purpose": (
            "Determine whether low qualification performance is also present "
            "without activation intervention."
        ),
        "source_closeout_commit": SOURCE_CLOSEOUT,
        "sources": {**observed, "private_qualification_dataset_sha256": DATASET_SHA256},
        "instrument": {
            "families": 300,
            "condition": CONDITION,
            "rollouts": 2,
            "logical_generations": 600,
            "same_prompts": True,
            "same_parser": "external-semantic-v3",
            "parser_sha256": PARSER_SHA256,
            "steering": "NONE",
            "router": "NONE",
            "seed_namespace": SEED_NAMESPACE,
            "new_unique_seeds": 600,
            "historical_seed_collisions": 0,
        },
        "model": {
            "id": "Qwen/Qwen3-8B",
            "revision": MODEL_REVISION,
            "tokenizer_revision": MODEL_REVISION,
            "model_byte_manifest_sha256": MODEL_BYTE_MANIFEST_SHA256,
            "dtype": "BF16",
            "attention": "SDPA",
        },
        "generation": {
            "do_sample": True,
            "temperature": 0.6,
            "top_p": 0.95,
            "top_k": 20,
            "min_p": 0.0,
            "max_new_tokens": 4096,
            "enable_thinking": False,
            "termination": "EXTREME_MECHANICAL_REPETITION_V1",
        },
        "analysis": {
            "comparison": "unsteered diagnostic versus frozen external champion",
            "quantities": [
                "accuracy",
                "commitment_validity",
                "semantic_evaluability",
                "correct-set overlap",
                "output-type accuracy",
                "generated-token and elapsed-time distributions",
            ],
            "no_new_primary_endpoint": True,
            "no_historical_reclassification": True,
        },
        "firewall": {
            "partial_correctness_inspection": False,
            "confirmation_qwen_access": 0,
            "reserve_qwen_access": 0,
            "historical_conditions_reexecuted": 0,
            "spark1_only": True,
            "spark2": False,
            "runpod": False,
        },
    }
    precheck_path = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_PRECHECK.json"
    write_json(precheck_path, precheck)
    lock = {
        "schema_version": "q3-fresh-unsteered-posthoc-execution-lock-v1",
        "status": "FROZEN_POSTHOC_BEFORE_MODEL_INFERENCE",
        "source_closeout_commit": SOURCE_CLOSEOUT,
        "scientific_outcomes_before_lock": 0,
        "correctness_inspected": False,
        "precheck_sha256": sha256_file(precheck_path),
        "schedule_sha256": sha256_file(schedule_path),
        "private_prompt_sha256": PRIVATE_PROMPT_SHA256,
        "private_dataset_sha256": DATASET_SHA256,
        "qualification_manifest_sha256": observed["qualification_manifest_sha256"],
        "runner_sha256": sha256_file(RUNNER),
        "scorer_sha256": sha256_file(SCORER),
        "tests_sha256": sha256_file(TESTS),
        "parser_sha256": PARSER_SHA256,
        "model_revision": MODEL_REVISION,
        "model_byte_manifest_sha256": MODEL_BYTE_MANIFEST_SHA256,
        "condition": CONDITION,
        "expected_rows": 600,
        "confirmation_qwen_access": 0,
        "reserve_qwen_access": 0,
    }
    write_json(REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_EXECUTION_LOCK.json", lock)
    print(json.dumps({"status": precheck["status"], "schedule_rows": 600}))


if __name__ == "__main__":
    main()
