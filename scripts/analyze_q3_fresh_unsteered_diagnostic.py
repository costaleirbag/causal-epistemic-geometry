#!/usr/bin/env python3
"""Post-seal scoring and aggregate comparison for the unsteered Q3.4 diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from epistemic_geometry.benchmarks.external.semantic_v3 import (  # noqa: E402
    PARSER_VERSION,
    evaluate_external_answer_v3,
)
from epistemic_geometry.research.durable_journal import decode, snapshot  # noqa: E402

REVIEW = ROOT / "review/q3_fresh_unsteered_diagnostic"
LOCK = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_EXECUTION_LOCK.json"
SCHEDULE = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_SCHEDULE.json"
PARSER_SOURCE = ROOT / "src/epistemic_geometry/benchmarks/external/semantic_v3.py"
EXPECTED_DATASET_SHA256 = "c791e38c29d36a43fbac8ce00412e4c77d533665e0b8cb9eef8fa12fb918ac1d"
EXPECTED_CHAMPION_SCORES_SHA256 = "c3b4ab47cf2422afb311fa978496e2abfbe5485ac76040ee3dcead2986ace533"
EXPECTED_CHAMPION_JOURNAL_SHA256 = (
    "2194646bcf25ff9512c5e3aaf35d4c2d0ed922f1f86ba6480709a1958dc89431"
)
EXPECTED_PARSER_SHA256 = "51ac492a6cea1284c36df6ef659520adf4a04e0595cf0e66bfd15ba172b960c3"
CONDITION = "UNSTEERED_BASELINE_POSTHOC_DIAGNOSTIC"
CHAMPION = "V4_DIRECTION_02_MEDIUM"
KEY_FIELDS = ("family_id", "condition", "rollout_index")
EXPECTED_ROWS = 600
TERMINAL = {"EXTREME_MECHANICAL_REPETITION_V1", "max_new_tokens", "model_runtime_error"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def key(row: dict[str, Any]) -> tuple[str, str, int]:
    return str(row["family_id"]), str(row["condition"]), int(row["rollout_index"])


def quantiles(values: Iterable[float]) -> dict[str, float]:
    array = np.asarray(list(values), dtype=np.float64)
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "p95": float(np.quantile(array, 0.95)),
        "p99": float(np.quantile(array, 0.99)),
        "max": float(np.max(array)),
    }


def write_exclusive(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            if written <= 0:
                raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_SCORE_SHORT_WRITE")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)


def load_raw(
    execution_dir: Path, schedule: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    journal = execution_dir / "journal.jsonl"
    seal_path = execution_dir / "COLLECTION_COMPLETE_SEAL.json"
    seal = read_json(seal_path)
    raw = snapshot(journal)
    if (
        seal.get("status") != "COLLECTION_COMPLETE_RAW_UNSCORED"
        or seal.get("completed") != EXPECTED_ROWS
        or seal.get("expected") != EXPECTED_ROWS
        or seal.get("missing") != 0
        or seal.get("unexpected") != 0
        or seal.get("duplicates") != 0
        or seal.get("correctness_inspected") is not False
        or seal.get("semantic_scoring") != "NOT_RUN"
        or hashlib.sha256(raw).hexdigest() != seal.get("journal_sha256")
        or len(raw) != seal.get("journal_bytes")
    ):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_RAW_SEAL_INVALID")
    first = json.loads(raw.splitlines()[0])
    identity = first["identity"]
    view = decode(raw, identity, KEY_FIELDS)
    expected = {key(row): (index, row) for index, row in enumerate(schedule)}
    if set(view.rows) != set(expected):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_RAW_COVERAGE_INVALID")
    for logical_key, row in view.rows.items():
        index, planned = expected[logical_key]
        if row.get("schedule_index") != index or any(
            row.get(field) != value for field, value in planned.items()
        ):
            raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_RAW_PROVENANCE_INVALID")
    return list(view.rows.values()), seal


def load_champion_runtime(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    if sha256_file(path) != EXPECTED_CHAMPION_JOURNAL_SHA256:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_CHAMPION_JOURNAL_HASH_MISMATCH")
    raw = snapshot(path)
    first = json.loads(raw.splitlines()[0])
    view = decode(raw, first["identity"], KEY_FIELDS)
    rows = {
        (str(row["family_id"]), int(row["rollout_index"])): row
        for row in view.rows.values()
        if row["condition"] == CHAMPION
    }
    if len(rows) != EXPECTED_ROWS:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_CHAMPION_RUNTIME_COVERAGE_INVALID")
    return rows


def classify(raw: dict[str, Any], reference: str) -> dict[str, Any]:
    terminal = str(raw.get("terminal_reason", ""))
    if terminal in TERMINAL or raw.get("runtime_error") is not None:
        status = (
            "REPETITION_STOP"
            if terminal == "EXTREME_MECHANICAL_REPETITION_V1"
            else "HARD_CAP"
            if terminal == "max_new_tokens"
            else "RUNTIME_ERROR"
        )
        parsed = {
            "commitment_valid": False,
            "semantic_evaluable": False,
            "correct": False,
            "value_type": None,
            "canonical_value": None,
            "failure_reason": terminal or "runtime error",
        }
    else:
        value = evaluate_external_answer_v3(
            str(raw.get("raw_output", "")),
            reference,
            truncated=bool(raw.get("truncated", False)),
            runtime_error=False,
        )
        status = (
            "VALID_CORRECT"
            if value.correct
            else "VALID_WRONG"
            if value.commitment_valid and value.semantic_evaluable
            else "INVALID_FORMAT"
        )
        parsed = {
            "commitment_valid": bool(value.commitment_valid),
            "semantic_evaluable": bool(value.semantic_evaluable),
            "correct": bool(value.correct),
            "value_type": value.value_type,
            "canonical_value": value.canonical_value,
            "failure_reason": value.failure_reason,
        }
    return {
        **{field: raw[field] for field in KEY_FIELDS},
        **parsed,
        "status": status,
        "terminal_reason": terminal,
        "generated_token_count": int(raw["generated_token_count"]),
        "elapsed_seconds": float(raw["elapsed_seconds"]),
        "raw_output_sha256": hashlib.sha256(str(raw["raw_output"]).encode()).hexdigest(),
    }


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(row["status"]) for row in rows)
    return {
        "rows": len(rows),
        "correct": sum(bool(row["correct"]) for row in rows),
        "accuracy": float(np.mean([bool(row["correct"]) for row in rows])),
        "commitment_valid": sum(bool(row["commitment_valid"]) for row in rows),
        "commitment_validity": float(np.mean([bool(row["commitment_valid"]) for row in rows])),
        "semantic_evaluable": sum(bool(row["semantic_evaluable"]) for row in rows),
        "semantic_evaluability": float(np.mean([bool(row["semantic_evaluable"]) for row in rows])),
        "status_counts": dict(sorted(statuses.items())),
        "generated_tokens": quantiles(int(row["generated_token_count"]) for row in rows),
        "elapsed_seconds": quantiles(float(row["elapsed_seconds"]) for row in rows),
        "total_generated_tokens": sum(int(row["generated_token_count"]) for row in rows),
        "summed_generation_seconds": sum(float(row["elapsed_seconds"]) for row in rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-dir", type=Path, required=True)
    parser.add_argument("--private-dataset", type=Path, required=True)
    parser.add_argument("--champion-scores", type=Path, required=True)
    parser.add_argument("--champion-journal", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--release-output", type=Path, required=True)
    args = parser.parse_args()

    lock = read_json(LOCK)
    schedule = list(read_json(SCHEDULE)["rows"])
    if (
        lock.get("status") != "FROZEN_POSTHOC_BEFORE_MODEL_INFERENCE"
        or sha256_file(SCHEDULE) != lock["schedule_sha256"]
        or sha256_file(PARSER_SOURCE) != EXPECTED_PARSER_SHA256
        or sha256_file(args.private_dataset) != EXPECTED_DATASET_SHA256
        or sha256_file(args.champion_scores) != EXPECTED_CHAMPION_SCORES_SHA256
        or len(schedule) != EXPECTED_ROWS
    ):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_SCORING_INPUT_INVALID")
    raw_rows, raw_seal = load_raw(args.execution_dir, schedule)

    references: dict[str, str] = {}
    output_types: dict[str, str] = {}
    with args.private_dataset.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            references[str(row["family_id"])] = str(row["reference_repr"])
            output_types[str(row["family_id"])] = str(row["reference_type"])
    if len(references) != 300:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_REFERENCE_COVERAGE_INVALID")

    scored = [classify(row, references[str(row["family_id"])]) for row in raw_rows]
    score_bytes = "".join(
        json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in scored
    ).encode()
    write_exclusive(args.private_output, score_bytes)

    champion: dict[tuple[str, int], dict[str, Any]] = {}
    with args.champion_scores.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["condition"] == CHAMPION:
                champion[(str(row["family_id"]), int(row["rollout_index"]))] = row
    if len(champion) != EXPECTED_ROWS:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_CHAMPION_COVERAGE_INVALID")
    champion_runtime = load_champion_runtime(args.champion_journal)
    for logical_key, row in champion.items():
        raw = champion_runtime[logical_key]
        if int(raw["generated_token_count"]) != int(row["generated_token_count"]):
            raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_CHAMPION_TOKEN_MISMATCH")
        row["elapsed_seconds"] = float(raw["elapsed_seconds"])

    diagnostic_by_key = {(str(row["family_id"]), int(row["rollout_index"])): row for row in scored}
    diagnostic_correct = {logical for logical, row in diagnostic_by_key.items() if row["correct"]}
    champion_correct = {logical for logical, row in champion.items() if row["correct"]}
    output_type_table = {}
    for output_type in sorted(set(output_types.values())):
        diagnostic_subset = [
            row for row in scored if output_types[str(row["family_id"])] == output_type
        ]
        champion_subset = [
            row for row in champion.values() if output_types[str(row["family_id"])] == output_type
        ]
        output_type_table[output_type] = {
            "rows": len(diagnostic_subset),
            "unsteered_correct": sum(bool(row["correct"]) for row in diagnostic_subset),
            "unsteered_accuracy": float(
                np.mean([bool(row["correct"]) for row in diagnostic_subset])
            ),
            "champion_correct": sum(bool(row["correct"]) for row in champion_subset),
            "champion_accuracy": float(np.mean([bool(row["correct"]) for row in champion_subset])),
        }

    release = {
        "schema_version": "q3-fresh-unsteered-posthoc-result-v1",
        "status": "Q3_FRESH_UNSTEERED_POSTHOC_DIAGNOSTIC_COMPLETE",
        "evidence_level": "POST_HOC_DIAGNOSTIC_ONLY",
        "historical_classification_modified": False,
        "historical_status": "Q3_FRESH_INSTRUMENT_NOT_QUALIFIED",
        "historical_forensic_status": "Q3_FRESH_INSTRUMENT_QUALIFICATION_FORENSIC_CLEAN",
        "raw": {
            "journal_sha256": raw_seal["journal_sha256"],
            "journal_bytes": raw_seal["journal_bytes"],
            "collection_seal_sha256": sha256_file(
                args.execution_dir / "COLLECTION_COMPLETE_SEAL.json"
            ),
            "rows": EXPECTED_ROWS,
            "missing": 0,
            "unexpected": 0,
            "duplicates": 0,
            "replacements": 0,
            "retry_rows": raw_seal["retry_rows"],
            "runtime_errors": raw_seal["runtime_errors"],
            "correctness_inspected_before_seal": False,
        },
        "scoring": {
            "parser": PARSER_VERSION,
            "parser_sha256": sha256_file(PARSER_SOURCE),
            "private_scores_sha256": hashlib.sha256(score_bytes).hexdigest(),
            "correctness_first_inspected_after_raw_seal": True,
            "manual_adjudication": False,
        },
        "unsteered": summary(scored),
        "champion": summary(list(champion.values())),
        "comparison": {
            "accuracy_delta_unsteered_minus_champion": float(
                np.mean([row["correct"] for row in scored])
                - np.mean([row["correct"] for row in champion.values()])
            ),
            "correct_intersection": len(diagnostic_correct & champion_correct),
            "correct_union": len(diagnostic_correct | champion_correct),
            "correct_jaccard": len(diagnostic_correct & champion_correct)
            / len(diagnostic_correct | champion_correct)
            if diagnostic_correct | champion_correct
            else 1.0,
            "unsteered_only_correct": len(diagnostic_correct - champion_correct),
            "champion_only_correct": len(champion_correct - diagnostic_correct),
            "output_type": output_type_table,
        },
        "firewall": {
            "confirmation_qwen_access": 0,
            "reserve_qwen_access": 0,
            "historical_conditions_reexecuted": 0,
            "spark2_used": False,
            "runpod_used": False,
            "q3_confirmatory_result": "NOT_RUN",
            "raw_text_released": False,
        },
    }
    write_exclusive(
        args.release_output,
        (json.dumps(release, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(),
    )
    print(json.dumps({"status": release["status"], "rows": EXPECTED_ROWS}))


if __name__ == "__main__":
    main()
