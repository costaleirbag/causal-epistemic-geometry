#!/usr/bin/env python3
"""Blind, fail-closed unsteered Q3.4 post-hoc diagnostic collector."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import execute_q3_fresh_qualification as frozen  # noqa: E402
from run_q2_oos_v2_semantic import (  # noqa: E402
    EXTREME_REPETITION_NAME,
    extreme_mechanical_repetition_v1,
    frozen_terminal_metadata,
)

from epistemic_geometry.research.durable_journal import SingleWriterJournal  # noqa: E402

REVIEW = ROOT / "review/q3_fresh_unsteered_diagnostic"
LOCK = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_EXECUTION_LOCK.json"
SCHEDULE = REVIEW / "Q3_FRESH_UNSTEERED_DIAGNOSTIC_SCHEDULE.json"
EXPECTED_BRANCH = "research/q3-fresh-instrument-unsteered-diagnostic"
EXPECTED_PARENT = "827f4cc8adc8cd89b2cf270a89806950bbf5ac77"
CONDITION = "UNSTEERED_BASELINE_POSTHOC_DIAGNOSTIC"
EXPECTED_ROWS = 600
KEY_FIELDS = ("family_id", "condition", "rollout_index")
MAX_INFRASTRUCTURE_ATTEMPTS = 3


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_exclusive_json(path: Path, value: Any) -> None:
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:])
            if written <= 0:
                raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_SHORT_WRITE")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def git_branch() -> str:
    return subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()


def verify_committed_lock() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lock = read_json(LOCK)
    schedule = list(read_json(SCHEDULE)["rows"])
    head = git_head()
    if (
        git_branch() != EXPECTED_BRANCH
        or subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip()
        or subprocess.run(
            ["git", "merge-base", "--is-ancestor", EXPECTED_PARENT, head], cwd=ROOT
        ).returncode
        or lock.get("status") != "FROZEN_POSTHOC_BEFORE_MODEL_INFERENCE"
        or sha256_file(SCHEDULE) != lock["schedule_sha256"]
        or sha256_file(Path(__file__).resolve()) != lock["runner_sha256"]
        or len(schedule) != EXPECTED_ROWS
        or len({tuple(row[field] for field in KEY_FIELDS) for row in schedule}) != EXPECTED_ROWS
        or len({int(row["seed"]) for row in schedule}) != EXPECTED_ROWS
        or {str(row["condition"]) for row in schedule} != {CONDITION}
    ):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_LOCK_OR_CODE_INVALID")
    return lock, schedule


def identity_for(
    head: str, lock: dict[str, Any], environment: dict[str, Any], private_prompts: Path
) -> dict[str, Any]:
    return {
        "experiment": "Q3_FRESH_UNSTEERED_POSTHOC_DIAGNOSTIC",
        "code_commit": head,
        "lock_sha256": sha256_file(LOCK),
        "schedule_sha256": sha256_file(SCHEDULE),
        "private_prompt_sha256": sha256_file(private_prompts),
        "environment": environment,
        "condition": CONDITION,
        "steering": "NONE",
        "router": "NONE",
        "semantic_scoring": "DEFERRED_UNTIL_RAW_SEAL",
    }


def validate_inputs(
    model_path: str, private_prompts: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    lock, schedule = verify_committed_lock()
    if sha256_file(private_prompts) != lock["private_prompt_sha256"]:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_PROMPT_HASH_MISMATCH")
    frozen.load_prompts(private_prompts)
    environment = frozen.verify_environment(model_path)
    return lock, schedule, environment


def preflight(execution_dir: Path, model_path: str, private_prompts: Path) -> dict[str, Any]:
    journal = execution_dir / "journal.jsonl"
    if journal.exists() and journal.stat().st_size:
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_PREEXISTING_ROWS")
    lock, schedule, environment = validate_inputs(model_path, private_prompts)
    seal = {
        "schema_version": "q3-fresh-unsteered-posthoc-preopen-v1",
        "status": "AUTHORIZED_PREOPEN_NO_DIAGNOSTIC_OUTPUTS",
        "code_commit": git_head(),
        "lock_sha256": sha256_file(LOCK),
        "schedule_sha256": sha256_file(SCHEDULE),
        "expected_rows": len(schedule),
        "private_prompt_sha256": sha256_file(private_prompts),
        "environment": environment,
        "journal_rows": 0,
        "correctness_inspected": False,
        "diagnostic_outcomes": 0,
        "confirmation_qwen_access": 0,
        "reserve_qwen_access": 0,
        "model_load_during_preopen": False,
        "frozen_lock_status": lock["status"],
    }
    write_exclusive_json(execution_dir / "PREOPEN_SEAL.json", seal)
    return seal


def validate_preopen(
    execution_dir: Path, model_path: str, private_prompts: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    path = execution_dir / "PREOPEN_SEAL.json"
    if not path.is_file():
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_PREOPEN_REQUIRED")
    seal = read_json(path)
    lock, schedule, environment = validate_inputs(model_path, private_prompts)
    expected = {
        "status": "AUTHORIZED_PREOPEN_NO_DIAGNOSTIC_OUTPUTS",
        "code_commit": git_head(),
        "lock_sha256": sha256_file(LOCK),
        "schedule_sha256": sha256_file(SCHEDULE),
        "expected_rows": EXPECTED_ROWS,
        "private_prompt_sha256": sha256_file(private_prompts),
        "environment": environment,
        "journal_rows": 0,
        "correctness_inspected": False,
        "diagnostic_outcomes": 0,
        "confirmation_qwen_access": 0,
        "reserve_qwen_access": 0,
    }
    if any(seal.get(field) != value for field, value in expected.items()):
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_PREOPEN_INVALID")
    return lock, schedule, environment


def _retryable(exc: BaseException) -> bool:
    return isinstance(exc, (ConnectionError, TimeoutError, BrokenPipeError, EOFError))


def collect(execution_dir: Path, model_path: str, private_prompts: Path) -> dict[str, Any]:
    lock, schedule, environment = validate_preopen(execution_dir, model_path, private_prompts)
    if (execution_dir / "COLLECTION_COMPLETE_SEAL.json").exists():
        raise RuntimeError("Q3_UNSTEERED_DIAGNOSTIC_ALREADY_SEALED")
    prompts = frozen.load_prompts(private_prompts)
    identity = identity_for(git_head(), lock, environment, private_prompts)
    with SingleWriterJournal(
        execution_dir / "journal.jsonl", identity=identity, key_fields=KEY_FIELDS
    ) as journal:
        backend = frozen.build_backend(model_path)
        started = time.monotonic()
        for index, planned in enumerate(schedule):
            logical_key = tuple(planned[field] for field in KEY_FIELDS)
            if logical_key in journal.rows:
                continue
            item = frozen.model_item(planned["family_id"], prompts[planned["family_id"]])
            attempts = 0
            retry_reasons: list[str] = []
            while True:
                try:
                    trajectory_started = time.perf_counter()
                    output = backend.generate_reasoning(
                        item,
                        sampling_seed=int(planned["seed"]),
                        max_new_tokens=4096,
                        token_stop_predicate=extreme_mechanical_repetition_v1,
                        token_stop_name=EXTREME_REPETITION_NAME,
                    )
                    elapsed = time.perf_counter() - trajectory_started
                    terminal = frozen_terminal_metadata(output)
                    journal.append(
                        {
                            **planned,
                            "schedule_index": index,
                            "raw_output": output.raw_output,
                            "generated_token_ids": output.metadata["generated_token_ids"],
                            **terminal,
                            "condition_metadata": {
                                "condition": CONDITION,
                                "prompt_hash": output.metadata["rendered_prompt_hash"],
                                "steering": "NONE",
                                "router": "NONE",
                                "layer": None,
                                "duration": "none",
                            },
                            "model": frozen.MODEL,
                            "model_revision": frozen.MODEL_REVISION,
                            "seed": int(planned["seed"]),
                            "retry_count": attempts,
                            "retry_reasons": retry_reasons,
                            "elapsed_seconds": elapsed,
                            "runtime_error": None,
                            "semantic_scoring": "DEFERRED_UNTIL_COMPLETE_RAW_SEAL",
                        }
                    )
                    break
                except BaseException as exc:
                    if _retryable(exc) and attempts + 1 < MAX_INFRASTRUCTURE_ATTEMPTS:
                        attempts += 1
                        retry_reasons.append(f"{type(exc).__name__}: {exc}")
                        continue
                    raise
            completed = len(journal.rows)
            if completed == 1 or completed % 50 == 0:
                print(
                    json.dumps({"completed": completed, "pending": EXPECTED_ROWS - completed}),
                    flush=True,
                )

        def metadata(audited: list[dict[str, Any]]) -> dict[str, Any]:
            tokens = np.asarray([int(row["generated_token_count"]) for row in audited])
            elapsed = np.asarray([float(row["elapsed_seconds"]) for row in audited])
            return {
                "schema_version": "q3-fresh-unsteered-posthoc-collection-seal-v1",
                "status": "COLLECTION_COMPLETE_RAW_UNSCORED",
                "condition": CONDITION,
                "replacements": 0,
                "retry_rows": sum(int(row["retry_count"]) > 0 for row in audited),
                "runtime_errors": sum(row["runtime_error"] is not None for row in audited),
                "repetition_stops": sum(
                    row["terminal_reason"] == EXTREME_REPETITION_NAME for row in audited
                ),
                "hard_caps": sum(row["terminal_reason"] == "max_new_tokens" for row in audited),
                "generated_tokens": int(np.sum(tokens)),
                "generated_token_mean": float(np.mean(tokens)),
                "generated_token_median": float(np.median(tokens)),
                "summed_generation_seconds": float(np.sum(elapsed)),
                "collection_invocation_seconds": time.monotonic() - started,
                "preopen_sha256": sha256_file(execution_dir / "PREOPEN_SEAL.json"),
                "correctness_inspected": False,
                "semantic_scoring": "NOT_RUN",
                "confirmation_qwen_access": 0,
                "reserve_qwen_access": 0,
                "environment": environment,
            }

        return journal.seal(execution_dir / "COLLECTION_COMPLETE_SEAL.json", schedule, metadata)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "collect"), required=True)
    parser.add_argument("--execution-dir", type=Path, required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--private-prompts", type=Path, required=True)
    args = parser.parse_args()
    args.execution_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
    result = (
        preflight(args.execution_dir, args.model_path, args.private_prompts)
        if args.mode == "preflight"
        else collect(args.execution_dir, args.model_path, args.private_prompts)
    )
    print(
        json.dumps(
            {
                field: result[field]
                for field in result
                if field in {"status", "completed", "expected"}
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
