import sys

import numpy as np
import pytest

sys.path.insert(0, "scripts")
import geometry_specificity_pilot as p  # noqa: E402


def test_matched_gram_and_schedule():
    q = np.linalg.qr(np.random.default_rng(1).normal(size=(40, 8)))[0]
    c, v = p.make_geometry(q, 123)
    assert v.shape == (3, p.K, 40)
    assert np.allclose(v[0] @ v[0].T, v[2] @ v[2].T)
    assert not np.allclose(v[0], v[1])
    cond = ["BASELINE", "ORIGINAL_00", "RANDOM_1_00"]
    rows = p.schedule(["a", "b"], cond, 4, 123, "evaluation")
    assert len(rows) == 24 and len({r["seed"] for r in rows}) == 24
    cal = p.schedule(["a"], cond, 2, 123, "calibration")
    assert len({r["seed"] for r in cal}) == 2


def test_u_statistic_matches_direct_pairs_and_negative_retained():
    rng = np.random.default_rng(5)
    y = rng.integers(0, 2, (20, 5, 4)).astype(float)
    d = p.dshape(y)
    direct = np.zeros((5, 5))
    for a in range(5):
        for b in range(5):
            values = y[:, a] - y[:, b]
            values -= values.mean(axis=0)
            direct[a, b] = np.mean(
                [np.mean(values[:, r] * values[:, s]) for r in range(4) for s in range(4) if r != s]
            )
    assert np.allclose(d, direct)
    assert np.allclose(d, d.T) and np.allclose(np.diag(d), 0)
    assert (d < 0).any()
    with pytest.raises(ValueError):
        p.dshape(y[:, :, :1])


def test_shared_safety_intersection():
    cond = ["BASELINE"] + [f"{s}_{i:02}" for s in p.SPACES for i in range(p.K)]
    rows = p.schedule([str(i) for i in range(12)], cond, 2, 1, "calibration")
    for r in rows:
        r.update(
            commitment_valid=True,
            semantic_evaluable=True,
            truncated=False,
            generated_token_ids=[0] if r["condition"] == "BASELINE" else [1],
        )
    dep = {c: dict(relative_target_error=0) for c in cond if c != "BASELINE"}
    assert len(p.qualify(rows, dep)["common_safe_indices"]) == p.MAX_BANK
    for r in rows:
        if r["condition"].startswith("RANDOM_1_") and int(r["condition"][-2:]) < 17:
            r["generated_token_ids"] = [0]
    result = p.qualify(rows, dep)
    assert not result["qualified"] and result["common_safe_indices"] == list(range(17, 24))


def test_calibration_persistence_and_no_recollection(tmp_path, monkeypatch):
    import types
    from contextlib import nullcontext

    import geometry_budget_replay as g
    import run_geometry_specificity_pilot as r

    source = tmp_path / "source"
    source.mkdir()
    basis = source / r.BASIS
    basis.parent.mkdir(parents=True)
    np.save(basis, np.linalg.qr(np.random.default_rng(1).normal(size=(40, 8)))[0])
    panel = source / r.PANEL
    panel.parent.mkdir(parents=True)
    import json

    panel.write_text(json.dumps({"item_ids": [f"e{i}" for i in range(100)]}))
    (source / r.CAL).write_text(json.dumps({"item_ids": [f"c{i}" for i in range(12)]}))
    monkeypatch.setattr(r, "ROOT", source)
    official = tmp_path / "official"
    official.write_text("fixture")
    lock = dict(
        root_seed=123,
        target_amplitude=0.25,
        wall_seconds_ceiling=1000,
        official_source_sha256=g.sha(official),
    )
    run = tmp_path / "run"
    r.prepare(run, lock, "fixturelock")
    monkeypatch.setattr(
        r, "load_items", lambda path, ids: {i: types.SimpleNamespace(item_id=i) for i in ids}
    )
    calls = []

    interrupted = [False]

    def generate(backend, item, **kwargs):
        cond = kwargs["intervention_metadata"]["condition"]
        if len(calls) == 3 and not interrupted[0]:
            interrupted[0] = True
            raise RuntimeError("SIMULATED_INTERRUPTION")
        calls.append(cond)
        return types.SimpleNamespace(
            raw_output="FINAL: 1",
            metadata={
                "generated_token_ids": [0] if cond == "BASELINE" else [1],
                "generated_token_count": 1,
            },
        )

    monkeypatch.setitem(
        sys.modules,
        "run_q2_v3",
        types.SimpleNamespace(
            _calibrate_alpha=lambda *a: dict(
                alpha=1, implemented_amplitude=0.25, relative_target_error=0
            ),
            _mechanical_parse=lambda *a: dict(commitment_valid=True, semantic_evaluable=True),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "run_q2_v4_presemantic",
        types.SimpleNamespace(
            _baseline_denominator=lambda b, items: (1, [{} for i in items]),
            _condition_context=lambda b, i, *a: (nullcontext(), i),
            build_v4_backend=lambda path: object(),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "run_q2_oos_v2_semantic",
        types.SimpleNamespace(
            generate_frozen_semantic_output=generate,
            frozen_terminal_metadata=lambda output: dict(
                generated_token_count=1,
                truncated=False,
                terminal_reason="natural_completion",
                terminal_answer_channel_failure=False,
            ),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "execute_q2_oos_v2_semantic",
        types.SimpleNamespace(verify_spark1_environment=lambda path: {"fixture": True}),
    )
    with pytest.raises(RuntimeError, match="SIMULATED_INTERRUPTION"):
        r.collect(run, lock, "fixturelock", "fake", official, "calibration")
    assert len(calls) == 3
    r.collect(run, lock, "fixturelock", "fake", official, "calibration")
    assert len(calls) == 1752
    assert r.read(run / "CALIBRATION_SEAL.json")["rows"] == 1752
    assert r.read(run / "QUALIFICATION.json")["qualified"]
    # Re-deriving post-seal qualification is idempotent and performs no generation.
    r.finish_qualification(run)
    assert len(calls) == 1752
    with pytest.raises(ValueError, match="ALREADY_SEALED"):
        r.collect(run, lock, "fixturelock", "fake", official, "calibration")
    assert len(r.read(run / "EVALUATION_SCHEDULE.json")) == p.N * p.R * 37
    # A modified sealed dependency is rejected before any evaluation generation.
    (run / "DEPLOYMENT.json").write_text("{}")
    with pytest.raises(ValueError, match="SELECTION_HASH_CHANGED"):
        r.collect(run, lock, "fixturelock", "fake", official, "evaluation")
    assert len(calls) == 1752


def test_analysis_summary_and_complete_degeneracy():
    import analyze_geometry_specificity_pilot as a

    rng = np.random.default_rng(9)
    c = rng.normal(size=(12, 8))
    c /= np.linalg.norm(c, axis=1, keepdims=True)
    y = rng.integers(0, 2, (3, 30, 12, 8)).astype(float)
    out = a.summarize(y, c, draws=20)
    assert len(out["associations"]) == 3
    assert len(out["rollout_half_associations"]) == 3
    assert np.isfinite(out["contrast"])
    empty = a.summarize(np.zeros_like(y), c, draws=20)
    assert empty["classification"] == "INCONCLUSIVE_DEGENERATE_RESPONSE"
