import hashlib
import json
import sys

import numpy as np
import pytest

sys.path.insert(0, "scripts")
import geometry_budget_replay as g  # noqa: E402


def test_folds_match_actual_historical_code():
    from pathlib import Path

    import design_q3_realizable_utility as historical

    ids = json.loads(
        Path("review/q2_v4_1_prediction_lock/SEMANTIC_PANEL_MANIFEST.json").read_text()
    )["item_ids"]
    assert np.array_equal(
        g.folds(ids), historical.balanced_hash_folds(ids, 5, "q3-realizable-utility-v1")
    )
    assert [int((g.folds(ids) == i).sum()) for i in range(5)] == [60] * 5


def fixture():
    ids = [f"p{i:02}" for i in range(47)]
    rng = np.random.default_rng(71)
    y = rng.integers(0, 2, (12, 47, 2)).astype(float)
    tokens = np.ones_like(y) * 7
    coords = rng.normal(size=(47, 8))
    d = np.linalg.norm(coords[:, None] - coords[None, :], axis=2)
    return ids, y, tokens, d


def test_b47_and_real_budget_and_prefixes():
    ids, y, t, d = fixture()
    records = g.plan_banks(y, t, ids, d, 123)
    assert records == g.plan_banks(y, t, ids, d, 123)
    for method in ("TOP_COMPETENCE", "GREEDY_OPPORTUNITY"):
        full = [r for r in records if r["budget"] == 47 and r["selector"] == method]
        assert full[0]["bank"] == full[1]["bank"] and full[0]["champion"] == full[1]["champion"]
    orders = g.acquisition_orders(ids, d, 123)
    assert orders["A0_MAXIMIN"][0] == orders["UNIFORM"][0]
    for r in records:
        assert len(set(r["acquired"])) == r["budget"]
        assert r["acquired"] == orders[r["ordering"]][: r["budget"]]
        assert r["cells"] == 24 * r["budget"] and r["tokens"] == 7 * r["cells"]


def test_unacquired_scrambling_and_duplicate_queries():
    ids, y, t, d = fixture()
    order = g.acquisition_orders(ids, d, 123)["A0_MAXIMIN"]
    a = g.Acquisition(y, t, ids)
    shuffled = y.copy()
    for p in set(ids) - set(order[:8]):
        shuffled[:, ids.index(p), :] = 1 - shuffled[:, ids.index(p), :]
    b = g.Acquisition(shuffled, t, ids)
    for p in order[:8]:
        a.acquire(p)
        b.acquire(p)
    for method in ("TOP_COMPETENCE", "GREEDY_OPPORTUNITY"):
        assert g.select_bank(a.observed(), method) == g.select_bank(b.observed(), method)
    with pytest.raises(ValueError, match="DUPLICATE_QUERY"):
        a.acquire(order[0])


def test_test_labels_cannot_change_banks_and_seal(tmp_path):
    ids, y, t, d = fixture()
    full = np.concatenate([y, y], axis=0)
    before = g.plan_banks(full[:12], np.ones_like(full[:12]), ids, d, 123)
    full[12:] = 1 - full[12:]
    after = g.plan_banks(full[:12], np.ones_like(full[:12]), ids, d, 123)
    assert before == after
    p = tmp_path / "banks.json"
    h = g.save_plan(p, before)
    assert len(g.evaluate_saved(p, h, full[12:], ids)) == 16
    with pytest.raises(FileExistsError):
        g.save_plan(p, after)
    with pytest.raises(ValueError, match="SEAL"):
        g.evaluate_saved(p, "wrong", full[12:], ids)


def test_manual_selection_averages_rollouts_before_max():
    observed = {
        "a": np.array([[1, 1], [0, 0]]),
        "b": np.array([[0, 0], [1, 1]]),
        "c": np.array([[1, 0], [1, 0]]),
    }
    assert g.select_bank(observed, "TOP_COMPETENCE", 2) == ["a", "b"]
    assert g.select_bank(observed, "GREEDY_OPPORTUNITY", 2) == ["a", "b"]
    # c has .5 everywhere, not a per-rollout oracle of 1.
    assert observed["c"].mean(axis=1).mean() == 0.5


def test_loader_missing_duplicate_and_alignment(tmp_path):
    p = tmp_path / "x.jsonl"
    rows = [
        dict(item_id=i, condition="p", rollout_index=r, correct=i == "a", generated_token_count=3)
        for i in ("b", "a")
        for r in (1, 0)
    ]

    def put(values):
        p.write_text("".join(json.dumps(r) + "\n" for r in values))
        return hashlib.sha256(p.read_bytes()).hexdigest()

    y, t = g.load_numeric(p, put(rows), ["a", "b"], ["p"])
    assert y[:, 0, 0].tolist() == [1, 0]
    with pytest.raises(ValueError, match="DUPLICATE"):
        g.load_numeric(p, put(rows + [rows[0]]), ["a", "b"], ["p"])
    with pytest.raises(ValueError, match="MISSING"):
        g.load_numeric(p, put(rows[:-1]), ["a", "b"], ["p"])


def test_fold_specific_evaluation(tmp_path):
    records = [dict(fold=f, bank=["a"], champion="a") for f in (0, 1)]
    p = tmp_path / "banks.json"
    h = g.save_plan(p, records)
    zeros = np.zeros((3, 1, 2))
    ones = np.ones((3, 1, 2))
    a = g.evaluate_saved(p, h, zeros, ["a"], fold=0)
    b = g.evaluate_saved(p, h, ones, ["a"], fold=1)
    assert len(a) == len(b) == 1
    assert a[0]["opportunity"] == 0 and b[0]["opportunity"] == 1
    with pytest.raises(ValueError, match="FOLD_REQUIRED"):
        g.evaluate_saved(p, h, zeros, ["a"])
    with pytest.raises(ValueError, match="FOLD_MISSING"):
        g.evaluate_saved(p, h, zeros, ["a"], fold=2)


def test_invalid_distance_rejected():
    ids, _, _, d = fixture()
    for bad in (d - 1, d + np.eye(47), np.full_like(d, np.nan)):
        with pytest.raises(ValueError, match="GEOMETRY_INVALID"):
            g.acquisition_orders(ids, bad, 123)


def test_geometry_axes_realign_and_detect_corruption():
    import run_geometry_budget_replay as driver

    coords = {"a": np.array([1.0, 0.0]), "b": np.array([0.0, 1.0]), "c": np.array([0.6, 0.8])}
    h = np.array([[0.0, 1.0], [1.0, 0.0]])
    ff = np.zeros((1, 1))
    fr = np.array([[0.2, 0.4]])  # reference order b,a
    ids, d = driver.assemble_geometry(["a", "b"], ["c"], ["b", "a"], h, ff, fr, coords)
    assert ids == ["a_MEDIUM", "b_MEDIUM", "c_MEDIUM"]
    assert np.allclose(d[2], [0.4, 0.2, 0.0])
    with pytest.raises(ValueError, match="COORDINATE_MISMATCH"):
        driver.assemble_geometry(["a", "b"], ["c"], ["a", "b"], h, ff, fr, coords)


def test_real_geometry_public_only():
    from pathlib import Path

    import run_geometry_budget_replay as driver

    ids, d = driver.geometry(Path("."))
    assert len(ids) == 47 and d.shape == (47, 47)


def test_full_sources_validated_before_medium_selection(tmp_path):
    import run_geometry_budget_replay as driver

    ids = [f"h{i}_MEDIUM" for i in range(31)] + [f"f{i}_MEDIUM" for i in range(16)]
    items = ["a", "b"]
    paths, hashes = [], {}
    for name, selected, baseline in [("historical", ids[:31], True), ("fresh", ids[31:], False)]:
        conditions = (["BASELINE"] if baseline else []) + [
            p.removesuffix("_MEDIUM") + "_" + shell
            for p in selected
            for shell in ("MEDIUM", "STRONG")
        ]
        rows = [
            dict(item_id=i, condition=c, rollout_index=r, correct=i == "a", generated_token_count=3)
            for c in reversed(conditions)
            for i in reversed(items)
            for r in (1, 0)
        ]
        path = tmp_path / name
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
        paths.append(path)
        hashes[name + "_scores"] = g.sha(path)
    y, t = driver.load_sources(*paths, hashes, items, ids)
    assert y.shape == (2, 47, 2) and y[0].sum() == 94 and y[1].sum() == 0
    assert t.sum() == 564
    # The removed row is STRONG, unused by the analysis but required by source contract.
    lines = paths[1].read_text().splitlines()
    paths[1].write_text("\n".join(lines[1:]) + "\n")
    hashes["fresh_scores"] = g.sha(paths[1])
    with pytest.raises(ValueError, match="MISSING_KEY"):
        driver.load_sources(*paths, hashes, items, ids)


def test_aggregate_pairs_seeds_and_folds():
    import itertools

    import run_geometry_budget_replay as driver

    rows = []
    for f, seed, b, o, s in itertools.product(
        range(5), g.SEEDS, g.BUDGETS, driver.ORDERS, driver.SELECTORS
    ):
        value = (
            f / 10 + (0.02 if o == "A0_MAXIMIN" else 0) + (0.01 if s == "GREEDY_OPPORTUNITY" else 0)
        )
        rows.append(
            dict(
                fold=f,
                seed=seed,
                budget=b,
                ordering=o,
                selector=s,
                tokens=100,
                **dict.fromkeys(driver.METRICS, value),
            )
        )
    result = driver.aggregate(rows)
    assert all(
        abs(r["seed_distribution"]["mean"] - 0.02) < 1e-12 for r in result["acquisition_effects"]
    )
    assert all(
        abs(r["seed_distribution"]["mean"] - 0.01) < 1e-12 for r in result["selection_effects"]
    )
    assert all(abs(r["seed_distribution"]["mean"]) < 1e-12 for r in result["interactions"])


def test_plan_coverage_and_convergence(tmp_path):
    import copy

    import run_geometry_budget_replay as driver

    ids, y, t, d = fixture()
    y, t = np.tile(y, (20, 1, 1)), np.tile(t, (20, 1, 1))
    template = g.plan_banks(y, t, ids, d, g.SEEDS[0])
    records = []
    for fold in range(5):
        for seed in g.SEEDS:
            for row in template:
                records.append(dict(row, fold=fold, seed=seed))
    driver.validate_plans(records, ids)
    with pytest.raises(ValueError, match="PLAN_COVERAGE"):
        driver.validate_plans(records[:-1], ids)
    bad = copy.deepcopy(records)
    full = next(r for r in bad if r["budget"] == 47)
    full["bank"] = list(reversed(full["bank"]))
    with pytest.raises(ValueError, match="B47_NOT_CONVERGED"):
        driver.validate_plans(bad, ids)
