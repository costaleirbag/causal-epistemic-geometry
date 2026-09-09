"""Prospectively locked matched-orientation collection; scoring is a separate command."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import geometry_budget_replay as g
import geometry_specificity_pilot as p
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASIS = "review/q2_v4_spark1_presemantic/SPARK1_SUBSPACE_Q.npy"
PANEL = "review/q2_v4_1_prediction_lock/SEMANTIC_PANEL_MANIFEST.json"
CAL = "review/q2_v4_spark1_presemantic/SHELL_CALIBRATION_MANIFEST.json"


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    # Atomic checkpoint replacement is only for operational status, not scientific seals.
    path = Path(path)
    temp = path.with_suffix(".tmp")
    with temp.open("w") as f:
        json.dump(value, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


def verify(lock_path, expected):
    if g.sha(lock_path) != expected:
        raise ValueError("PROTOCOL_HASH")
    lock = read(lock_path)
    if lock["status"] != "FROZEN_BEFORE_PILOT":
        raise ValueError("PROTOCOL_STATUS")
    for name, h in lock["sources"].items():
        if g.sha(ROOT / name) != h:
            raise ValueError("FROZEN_SOURCE_HASH:" + name)
    return lock


def prepare(run, lock, lock_sha):
    run.mkdir(mode=0o700, parents=False, exist_ok=False)
    c, v = p.make_geometry(np.load(ROOT / BASIS, allow_pickle=False), lock["root_seed"])
    np.savez(run / "vectors.npz", coefficients=c, vectors=v)
    items = read(ROOT / PANEL)["item_ids"]
    selected = sorted(
        items,
        key=lambda i: hashlib.sha256(f"{lock['root_seed']}|evaluation|{i}".encode()).hexdigest(),
    )[: p.N]
    calibration = read(ROOT / CAL)["item_ids"]
    if len(calibration) != 12 or set(calibration) & set(selected):
        raise ValueError("SPLIT_OVERLAP")
    conditions = ["BASELINE"] + [f"{s}_{i:02}" for s in p.SPACES for i in range(p.K)]
    plan = p.schedule(calibration, conditions, 2, lock["root_seed"], "calibration")
    g.save_plan(run / "CALIBRATION_SCHEDULE.json", plan)
    g.save_plan(
        run / "PREPARED.json",
        dict(
            protocol_sha256=lock_sha,
            root_seed=lock["root_seed"],
            vectors_sha256=g.sha(run / "vectors.npz"),
            calibration_schedule_sha256=g.sha(run / "CALIBRATION_SCHEDULE.json"),
            evaluation_items=selected,
            calibration_items=calibration,
            calibration_rows=len(plan),
            maximum_evaluation_rows=p.N * p.R * (3 * p.MAX_BANK + 1),
        ),
    )


def load_items(official, ids):
    from epistemic_geometry.benchmarks.external.base import ExternalItem
    from epistemic_geometry.experiments.q2_v3_prompt_provenance import canonical_q2_v3_task_prompt

    selected = {}
    for line in Path(official).read_text().splitlines():
        row = json.loads(line)
        if row["id"] in ids:
            selected[row["id"]] = ExternalItem(
                item_id=row["id"],
                benchmark="CRUXEval",
                subtask="output_prediction",
                prompt=canonical_q2_v3_task_prompt(str(row["code"]), str(row["input"])),
                reference_answer=str(row["output"]),
                evaluator="python_literal",
                source_revision=str(row["dataset_revision"]),
                metadata={},
            )
    if set(selected) != set(ids):
        raise ValueError("ITEM_COVERAGE")
    return selected


def collect(run, lock, lock_sha, model_path, official, phase):
    from execute_q2_oos_v2_semantic import verify_spark1_environment
    from run_q2_oos_v2_semantic import frozen_terminal_metadata, generate_frozen_semantic_output
    from run_q2_v3 import _calibrate_alpha, _mechanical_parse
    from run_q2_v4_presemantic import _baseline_denominator, _condition_context, build_v4_backend

    from epistemic_geometry.research.reliability import CrashSafeJournal

    prepared = read(run / "PREPARED.json")
    if (
        prepared["protocol_sha256"] != lock_sha
        or g.sha(run / "vectors.npz") != prepared["vectors_sha256"]
    ):
        raise ValueError("PREPARED_HASH")
    if g.sha(official) != lock["official_source_sha256"]:
        raise ValueError("PRIVATE_SOURCE_HASH")
    if (run / f"{phase.upper()}_SEAL.json").exists():
        raise ValueError("ALREADY_SEALED")
    if phase == "evaluation":
        selection = read(run / "SELECTION_SEAL.json")
        for name, key in [
            ("DEPLOYMENT.json", "deployment_sha256"),
            ("QUALIFICATION.json", "qualification_sha256"),
            ("EVALUATION_SCHEDULE.json", "schedule_sha256"),
        ]:
            if g.sha(run / name) != selection[key]:
                raise ValueError("SELECTION_HASH_CHANGED")
        qualified = read(run / "QUALIFICATION.json")
        if not qualified["qualified"]:
            raise ValueError("PILOT_NOT_QUALIFIED")
        if (
            g.sha(run / "calibration.jsonl")
            != read(run / "CALIBRATION_SEAL.json")["journal_sha256"]
        ):
            raise ValueError("CALIBRATION_SEAL_CHANGED")
    if phase == "calibration" and (
        g.sha(run / "CALIBRATION_SCHEDULE.json") != prepared["calibration_schedule_sha256"]
    ):
        raise ValueError("CALIBRATION_SCHEDULE_CHANGED")
    schedule = read(
        run
        / ("CALIBRATION_SCHEDULE.json" if phase == "calibration" else "EVALUATION_SCHEDULE.json")
    )
    wanted = {(r["item_id"], r["condition"], r["rollout_index"]) for r in schedule}
    if len(wanted) != len(schedule):
        raise ValueError("SCHEDULE_COVERAGE")
    itemmap = load_items(
        official,
        prepared["calibration_items"] if phase == "calibration" else prepared["evaluation_items"],
    )
    journal = CrashSafeJournal(
        run / f"{phase}.jsonl",
        identity=dict(
            campaign="GEOMETRY_SPECIFICITY_PILOT",
            protocol_sha256=lock_sha,
            phase=phase,
            schedule_sha256=g.sha(
                run
                / (
                    "CALIBRATION_SCHEDULE.json"
                    if phase == "calibration"
                    else "EVALUATION_SCHEDULE.json"
                )
            ),
        ),
        key_fields=("item_id", "condition", "rollout_index"),
    )
    done = set(journal.rows)
    if not done <= wanted:
        raise ValueError("UNEXPECTED_PERSISTED_ROW")
    arrays = np.load(run / "vectors.npz", allow_pickle=False)
    vectors = {
        f"{s}_{i:02}": arrays["vectors"][si, i] for si, s in enumerate(p.SPACES) for i in range(p.K)
    }
    environment = verify_spark1_environment(model_path)
    env_path = run / "ENVIRONMENT.json"
    if env_path.exists():
        if read(env_path) != environment:
            raise ValueError("ENVIRONMENT_DRIFT")
    else:
        g.save_plan(env_path, environment)
    start_path = run / "EXECUTION_START.json"
    if not start_path.exists():
        g.save_plan(start_path, {"unix_time": time.time()})
    deadline = read(start_path)["unix_time"] + lock["wall_seconds_ceiling"]
    if time.time() >= deadline:
        raise RuntimeError("CAMPAIGN_RUNTIME_CEILING")
    attempts = CrashSafeJournal(
        run / "attempts.jsonl",
        identity={"campaign": "GEOMETRY_SPECIFICITY_PILOT", "protocol_sha256": lock_sha},
        key_fields=("attempt_index",),
    )
    attempt_count = len(attempts.rows)
    backend = build_v4_backend(model_path)
    if not (run / "DEPLOYMENT.json").exists():
        if phase != "calibration" or done:
            raise ValueError("MISSING_DEPLOYMENT")
        denom, records = _baseline_denominator(
            backend, [itemmap[i] for i in prepared["calibration_items"]]
        )
        deployment = {
            c: dict(candidate_id=c, **_calibrate_alpha(v, lock["target_amplitude"], denom))
            for c, v in vectors.items()
        }
        g.save_plan(
            run / "DEPLOYMENT.json",
            dict(
                denominator=denom,
                denominator_records=records,
                prefill_count=len(records),
                controllers=deployment,
            ),
        )
    deployment_hash = g.sha(run / "DEPLOYMENT.json")
    deployment_binding = run / "DEPLOYMENT_HASH.json"
    if deployment_binding.exists():
        if read(deployment_binding)["sha256"] != deployment_hash:
            raise ValueError("DEPLOYMENT_CHANGED_DURING_COLLECTION")
    elif done:
        raise ValueError("MISSING_DEPLOYMENT_BINDING")
    else:
        g.save_plan(deployment_binding, {"sha256": deployment_hash})
    deployment = read(run / "DEPLOYMENT.json")["controllers"]
    # Runtime ceiling includes collection time recorded in both phase journals.
    elapsed = sum(float(r.get("elapsed_seconds", 0)) for r in journal.rows.values())
    if phase == "evaluation":
        elapsed += read(run / "CALIBRATION_SEAL.json")["elapsed_seconds"]
    started = time.monotonic()
    for row in schedule:
        key = (row["item_id"], row["condition"], row["rollout_index"])
        if key in done:
            continue
        if (
            time.time() >= deadline
            or elapsed + time.monotonic() - started >= lock["wall_seconds_ceiling"]
        ):
            raise RuntimeError("CAMPAIGN_RUNTIME_CEILING")
        context, modelrow = _condition_context(
            backend, itemmap[row["item_id"]], row["condition"], vectors, deployment
        )
        if attempt_count >= 20000:
            raise RuntimeError("CAMPAIGN_TRAJECTORY_CEILING")
        attempts.append(dict(row, phase=phase, attempt_index=attempt_count, unix_time=time.time()))
        attempt_count += 1
        begin = time.monotonic()
        with context as trace:
            output = generate_frozen_semantic_output(
                backend,
                modelrow,
                sampling_seed=row["seed"],
                intervention_metadata=dict(
                    experiment="GEOMETRY_SPECIFICITY_PILOT", phase=phase, condition=row["condition"]
                ),
            )
        terminal = frozen_terminal_metadata(output)
        result = dict(
            row,
            raw_output=output.raw_output,
            generated_token_ids=output.metadata.get("generated_token_ids", []),
            **terminal,
            elapsed_seconds=time.monotonic() - begin,
            hook_trace=trace.metadata() if trace is not None else None,
        )
        if phase == "calibration":
            mechanical = _mechanical_parse(
                output.raw_output, int(terminal["generated_token_count"])
            )
            result.update(
                commitment_valid=bool(mechanical["commitment_valid"])
                and not terminal["terminal_answer_channel_failure"],
                semantic_evaluable=bool(mechanical["semantic_evaluable"])
                and not terminal["terminal_answer_channel_failure"],
            )
        journal.append(result)
        done.add(key)
        if len(done) % 25 == 0:
            write(
                run / "STATUS.json",
                dict(
                    phase=phase,
                    completed=len(done),
                    expected=len(schedule),
                    updated_at=time.time(),
                    pid=os.getpid(),
                ),
            )
            print(f"{phase}: {len(done)}/{len(schedule)}", flush=True)
    # Reopen on disk; never trust an in-memory count as the raw-data seal.
    persisted = CrashSafeJournal(
        journal.path, identity=journal.identity, key_fields=journal.key_fields
    )
    if set(persisted.rows) != wanted:
        raise ValueError("PERSISTED_COVERAGE")
    rows = list(persisted.rows.values())
    seal = dict(
        protocol_sha256=lock_sha,
        journal_sha256=g.sha(journal.path),
        deployment_sha256=g.sha(run / "DEPLOYMENT.json"),
        schedule_sha256=g.sha(
            run
            / (
                "CALIBRATION_SCHEDULE.json"
                if phase == "calibration"
                else "EVALUATION_SCHEDULE.json"
            )
        ),
        rows=len(rows),
        elapsed_seconds=sum(r["elapsed_seconds"] for r in rows),
        generated_tokens=sum(r["generated_token_count"] for r in rows),
        correctness_inspected=False,
    )
    g.save_plan(run / f"{phase.upper()}_SEAL.json", seal)
    if phase == "calibration":
        finish_qualification(run)
    write(
        run / "STATUS.json",
        dict(phase=phase, status="SEALED", rows=len(rows), updated_at=time.time()),
    )


def finish_qualification(run):
    seal = read(run / "CALIBRATION_SEAL.json")
    if g.sha(run / "calibration.jsonl") != seal["journal_sha256"]:
        raise ValueError("CALIBRATION_SEAL_CHANGED")
    if g.sha(run / "DEPLOYMENT.json") != seal["deployment_sha256"]:
        raise ValueError("DEPLOYMENT_SEAL_CHANGED")
    rows = [
        json.loads(line)["row"] for line in (run / "calibration.jsonl").read_text().splitlines()
    ]
    deployment = read(run / "DEPLOYMENT.json")["controllers"]
    q = p.qualify(rows, deployment)
    q["qualified"] = bool(q["qualified"])
    keep = q["common_safe_indices"]
    arrays = np.load(run / "vectors.npz", allow_pickle=False)
    if len(keep) >= 8 and np.linalg.matrix_rank(arrays["coefficients"][keep]) != 8:
        q["qualified"] = False
    if (run / "QUALIFICATION.json").exists():
        if read(run / "QUALIFICATION.json") != q:
            raise ValueError("QUALIFICATION_REDERIVATION_MISMATCH")
    else:
        g.save_plan(run / "QUALIFICATION.json", q)
    if q["qualified"]:
        prepared = read(run / "PREPARED.json")
        conditions = ["BASELINE"] + [f"{s}_{i:02}" for s in p.SPACES for i in keep]
        schedule = p.schedule(
            prepared["evaluation_items"], conditions, p.R, prepared["root_seed"], "evaluation"
        )
        path = run / "EVALUATION_SCHEDULE.json"
        if path.exists():
            if read(path) != schedule:
                raise ValueError("EVALUATION_SCHEDULE_REDERIVATION_MISMATCH")
        else:
            g.save_plan(path, schedule)
        seal = dict(
            deployment_sha256=g.sha(run / "DEPLOYMENT.json"),
            qualification_sha256=g.sha(run / "QUALIFICATION.json"),
            schedule_sha256=g.sha(path),
        )
        if (run / "SELECTION_SEAL.json").exists():
            if read(run / "SELECTION_SEAL.json") != seal:
                raise ValueError("SELECTION_SEAL_CHANGED")
        else:
            g.save_plan(run / "SELECTION_SEAL.json", seal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "qualify", "calibration", "evaluation"])
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--precheck", type=Path, required=True)
    parser.add_argument("--precheck-sha", required=True)
    parser.add_argument("--model-path")
    parser.add_argument("--official", type=Path)
    a = parser.parse_args()
    lock = verify(a.precheck, a.precheck_sha)
    if a.mode == "prepare":
        prepare(a.run, lock, a.precheck_sha)
        return
    if a.mode == "qualify":
        finish_qualification(a.run)
        return
    # Exclusive OS lock prevents parallel collectors without changing infrastructure.
    with (a.run / "COLLECTOR.lock").open("a") as guard:
        fcntl.flock(guard, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if a.model_path is None or a.official is None:
            raise ValueError("MODEL_AND_PRIVATE_SOURCE_REQUIRED")
        collect(a.run, lock, a.precheck_sha, a.model_path, a.official, a.mode)


if __name__ == "__main__":
    main()
