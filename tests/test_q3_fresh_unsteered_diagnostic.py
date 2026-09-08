from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "scripts")

import execute_q3_fresh_unsteered_diagnostic as executor  # noqa: E402
import prepare_q3_fresh_unsteered_diagnostic as prepare  # noqa: E402

from epistemic_geometry.research.durable_journal import (  # noqa: E402
    JournalIntegrityError,
    SingleWriterJournal,
)


def test_schedule_has_600_new_unique_noncolliding_seeds() -> None:
    schedule = prepare.build_schedule()
    rows = schedule["rows"]
    historical = prepare.read_json(prepare.HISTORICAL_SCHEDULE)["rows"]
    assert len(rows) == 600
    assert len({row["seed"] for row in rows}) == 600
    assert {row["seed"] for row in rows}.isdisjoint({row["seed"] for row in historical})
    assert {row["condition"] for row in rows} == {prepare.CONDITION}


def test_collector_has_no_parser_router_or_steering_path() -> None:
    source = inspect.getsource(executor)
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not any("semantic_v3" in name for name in imports)
    assert "generation_context(" not in source
    assert "load_vectors(" not in source
    assert "load_router(" not in source
    assert '"steering": "NONE"' in source
    assert '"router": "NONE"' in source


def test_collect_refuses_without_preopen_before_model_load(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[str] = []
    monkeypatch.setattr(executor, "validate_inputs", lambda *_: called.append("inputs"))
    monkeypatch.setattr(executor.frozen, "build_backend", lambda *_: called.append("model"))
    with pytest.raises(RuntimeError, match="PREOPEN_REQUIRED"):
        executor.collect(tmp_path, "model", tmp_path / "prompts")
    assert called == []


def test_persisted_seal_rejects_incomplete_schedule(tmp_path: Path) -> None:
    path = tmp_path / "journal.jsonl"
    identity = {"experiment": "synthetic-unsteered"}
    schedule = [
        {
            "family_id": "f0",
            "condition": executor.CONDITION,
            "rollout_index": rollout,
            "seed": 10 + rollout,
        }
        for rollout in (0, 1)
    ]
    with SingleWriterJournal(path, identity=identity, key_fields=executor.KEY_FIELDS) as journal:
        journal.append({**schedule[0], "schedule_index": 0})
        with pytest.raises(JournalIntegrityError, match="COVERAGE_INCOMPLETE"):
            journal.seal(tmp_path / "seal.json", schedule, lambda _rows: {})


def test_identical_resume_row_is_not_regenerated(tmp_path: Path) -> None:
    path = tmp_path / "journal.jsonl"
    identity = {"experiment": "synthetic-unsteered"}
    row = {
        "family_id": "f0",
        "condition": executor.CONDITION,
        "rollout_index": 0,
        "seed": 10,
    }
    with SingleWriterJournal(path, identity=identity, key_fields=executor.KEY_FIELDS) as journal:
        journal.append(row)
    with SingleWriterJournal(path, identity=identity, key_fields=executor.KEY_FIELDS) as journal:
        assert tuple(row[field] for field in executor.KEY_FIELDS) in journal.rows
        journal.append(row)
        assert len(journal.rows) == 1
