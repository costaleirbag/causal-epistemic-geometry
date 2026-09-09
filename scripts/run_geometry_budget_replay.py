"""Fixed retrospective Q2 budget comparison; CPU only, no inference dependencies."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

import geometry_budget_replay as g
import numpy as np

HIST = "review/q2_v4_1_prediction_lock/"
FRESH = "review/q2_oos_fresh_controller_design/v2_presemantic_closeout/"
HBANK = "review/q2_v4_1_31_safe_bank_review/SAFE_31_IMMUTABLE_MANIFEST.json"
FCAND = "review/q2_oos_fresh_controller_design/v2_final_presemantic/V2_CANDIDATE_BANK_MANIFEST.json"
METRICS = ("opportunity", "fixed_policy_accuracy", "uniform_policy_accuracy")
ORDERS = ("A0_MAXIMIN", "UNIFORM")
SELECTORS = ("TOP_COMPETENCE", "GREEDY_OPPORTUNITY")


def read(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def assemble_geometry(hids, fids, refs, h, ff, fr, coords):
    if len(set(hids + fids)) != len(hids + fids) or set(refs) != set(hids):
        raise ValueError("GEOMETRY_AXIS")
    if len(set(refs)) != len(refs):
        raise ValueError("GEOMETRY_AXIS")
    if (
        h.shape != (len(hids), len(hids))
        or ff.shape != (len(fids), len(fids))
        or fr.shape != (len(fids), len(refs))
    ):
        raise ValueError("GEOMETRY_BLOCK_SHAPE")
    aligned = fr[:, [refs.index(p) for p in hids]]
    distance = np.block([[h, aligned.T], [aligned, ff]])
    ids = hids + fids
    unit = np.stack([coords[p] for p in ids])
    unit = unit / np.linalg.norm(unit, axis=1, keepdims=True)
    independent = 1 - np.clip(unit @ unit.T, -1, 1)
    np.fill_diagonal(independent, 0)
    if not np.allclose(distance, independent, atol=1e-10, rtol=0):
        raise ValueError("GEOMETRY_COORDINATE_MISMATCH")
    g.acquisition_orders(ids, distance, g.SEEDS[0])
    return [p + "_MEDIUM" for p in ids], distance


def geometry(root):
    hm, fm = (
        read(root / HIST / "PREDICTION_MATRIX_METADATA.json"),
        read(root / FRESH / "PREDICTION_MATRIX_METADATA.json"),
    )
    hids, fids = hm["controller_order"], fm["fresh_controller_order"]
    if len(hids) != 31 or len(fids) != 16:
        raise ValueError("CONTROLLER_COUNT")
    coords = {
        r["candidate_id"]: np.array(r["coefficients"]) for r in read(root / HBANK)["directions"]
    }
    coords.update(
        {
            r["candidate_id"]: np.array(r["coefficients"])
            for r in read(root / FCAND)["candidates"]
            if r["candidate_id"] in fids
        }
    )
    if set(read(root / FRESH / "V2_SELECTED_CONTROLLER_BANK.json")["selected_ids"]) != set(fids):
        raise ValueError("SELECTED_AXIS")
    with (
        np.load(root / HIST / "PREDICTION_MATRICES.npz", allow_pickle=False) as h,
        np.load(root / FRESH / "PREDICTION_MATRICES.npz", allow_pickle=False) as f,
    ):
        return assemble_geometry(
            hids,
            fids,
            fm["reference_controller_order"],
            h["A0_MEDIUM"],
            f["A0_MEDIUM_FRESH_FRESH"],
            f["A0_MEDIUM_FRESH_REFERENCE"],
            coords,
        )


def load_sources(hist_path, fresh_path, source_hashes, items, ids):
    # Validate every row in both full historical sources, including unused shells.
    hc = ["BASELINE"] + [
        p.removesuffix("_MEDIUM") + "_" + shell for p in ids[:31] for shell in ("MEDIUM", "STRONG")
    ]
    fc = [
        p.removesuffix("_MEDIUM") + "_" + shell for p in ids[31:] for shell in ("MEDIUM", "STRONG")
    ]
    hy, ht = g.load_numeric(hist_path, source_hashes["historical_scores"], items, hc)
    fy, ft = g.load_numeric(fresh_path, source_hashes["fresh_scores"], items, fc)
    hi, fi = [hc.index(p) for p in ids[:31]], [fc.index(p) for p in ids[31:]]
    return np.concatenate([hy[:, hi], fy[:, fi]], axis=1), np.concatenate(
        [ht[:, hi], ft[:, fi]], axis=1
    )


def validate_plans(records, ids):
    expected = set(itertools.product(range(5), g.SEEDS, g.BUDGETS, ORDERS, SELECTORS))
    keys = [(r["fold"], r["seed"], r["budget"], r["ordering"], r["selector"]) for r in records]
    if len(records) != 5120 or len(set(keys)) != len(keys) or set(keys) != expected:
        raise ValueError("PLAN_COVERAGE")
    lookup = dict(zip(keys, records, strict=True))
    for r in records:
        if (
            len(set(r["bank"])) != 8
            or not set(r["bank"]) <= set(r["acquired"]) <= set(ids)
            or r["champion"] not in r["bank"]
        ):
            raise ValueError("PLAN_BANK")
        if (
            len(set(r["acquired"])) != r["budget"]
            or len(r["acquired"]) != r["budget"]
            or r["cells"] != 480 * r["budget"]
        ):
            raise ValueError("PLAN_COST")
        full = lookup[(r["fold"], r["seed"], 47, r["ordering"], r["selector"])]
        if r["acquired"] != full["acquired"][: r["budget"]]:
            raise ValueError("PLAN_PREFIX")
    for fold, selector in itertools.product(range(5), SELECTORS):
        full = [
            r
            for r in records
            if r["fold"] == fold and r["selector"] == selector and r["budget"] == 47
        ]
        if len({(tuple(r["bank"]), r["champion"]) for r in full}) != 1:
            raise ValueError("B47_NOT_CONVERGED")


def summary(values):
    a = np.asarray(values, dtype=float)
    return dict(
        mean=float(a.mean()),
        median=float(np.median(a)),
        q025=float(np.quantile(a, 0.025)),
        q975=float(np.quantile(a, 0.975)),
        minimum=float(a.min()),
        maximum=float(a.max()),
        positive_fraction=float((a > 0).mean()),
    )


def aggregate(records):
    lookup = {(r["fold"], r["seed"], r["budget"], r["ordering"], r["selector"]): r for r in records}

    def means(b, o, s, metric):
        return np.array(
            [np.mean([lookup[(f, seed, b, o, s)][metric] for f in range(5)]) for seed in g.SEEDS]
        )

    cells, effects = [], []
    for b, o, s in itertools.product(g.BUDGETS, ORDERS, SELECTORS):
        cells.append(
            dict(
                budget=b,
                ordering=o,
                selector=s,
                metrics={m: summary(means(b, o, s, m)) for m in METRICS},
                acquired_labels=480 * b,
                acquired_tokens=summary(means(b, o, s, "tokens")),
            )
        )
    for b, s, m in itertools.product(g.BUDGETS, SELECTORS, METRICS):
        delta = means(b, ORDERS[0], s, m) - means(b, ORDERS[1], s, m)
        effects.append(
            dict(
                contrast="A0_MINUS_UNIFORM",
                budget=b,
                selector=s,
                metric=m,
                seed_distribution=summary(delta),
                fold_mean_differences=[
                    float(
                        np.mean(
                            [
                                lookup[(f, seed, b, ORDERS[0], s)][m]
                                - lookup[(f, seed, b, ORDERS[1], s)][m]
                                for seed in g.SEEDS
                            ]
                        )
                    )
                    for f in range(5)
                ],
            )
        )
    selection, interaction = [], []
    for b, m in itertools.product(g.BUDGETS, METRICS):
        deltas = {}
        for o in ORDERS:
            deltas[o] = means(b, o, SELECTORS[1], m) - means(b, o, SELECTORS[0], m)
            selection.append(
                dict(
                    budget=b,
                    ordering=o,
                    metric=m,
                    contrast="GREEDY_MINUS_TOP_COMPETENCE",
                    seed_distribution=summary(deltas[o]),
                )
            )
        interaction.append(
            dict(
                budget=b, metric=m, seed_distribution=summary(deltas[ORDERS[0]] - deltas[ORDERS[1]])
            )
        )
    return dict(
        cells=cells,
        acquisition_effects=effects,
        selection_effects=selection,
        interactions=interaction,
        uncertainty=(
            "Empirical algorithm-seed variability, not confidence intervals "
            "or independent data replications."
        ),
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--precheck", type=Path, required=True)
    p.add_argument("--precheck-sha", required=True)
    p.add_argument("--historical-scores", type=Path, required=True)
    p.add_argument("--fresh-scores", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if g.sha(args.precheck) != args.precheck_sha:
        raise ValueError("PRECHECK_HASH")
    lock = read(args.precheck)
    if lock["status"] != "FROZEN_BEFORE_REPLAY":
        raise ValueError("PRECHECK_NOT_FROZEN")
    for path, expected in lock["sources"].items():
        if (
            path not in ("historical_scores", "fresh_scores")
            and g.sha(args.root / path) != expected
        ):
            raise ValueError("PUBLIC_SOURCE_HASH")
    # Exclusive directory prevents replay overwrite or duplicate run at this destination.
    args.output.mkdir(mode=0o700, parents=False, exist_ok=False)
    start = time.perf_counter()
    ids, distance = geometry(args.root)
    items = read(args.root / HIST / "SEMANTIC_PANEL_MANIFEST.json")["item_ids"]
    split = g.folds(items)
    assignment = dict(zip(items, map(int, split), strict=True))
    if (
        len(items) != 300
        or [int((split == f).sum()) for f in range(5)] != [60] * 5
        or digest(assignment) != lock["splits"]["canonical_assignment_sha256"]
    ):
        raise ValueError("SPLIT_MISMATCH")
    y, tokens = load_sources(args.historical_scores, args.fresh_scores, lock["sources"], items, ids)
    records = []
    for fold in range(5):
        train, test = split != fold, split == fold
        for seed in g.SEEDS:
            batch = g.plan_banks(y[train], tokens[train], ids, distance, seed)
            for row in batch:
                row.update(
                    fold=fold,
                    train_ids_sha256=digest(
                        [i for i, take in zip(items, train, strict=True) if take]
                    ),
                    test_ids_sha256=digest(
                        [i for i, take in zip(items, test, strict=True) if take]
                    ),
                )
            records.extend(batch)
        print(f"planned_fold={fold} banks={len(records)}", flush=True)
    validate_plans(records, ids)
    plan_path = args.output / "PRIVATE_BANKS.json"
    seal = g.save_plan(plan_path, records)
    g.save_plan(
        args.output / "BANK_SEAL.json",
        dict(sha256=seal, count=len(records), precheck_sha256=args.precheck_sha),
    )
    print("all_5120_banks_sealed_before_test_evaluation", flush=True)
    evaluated = []
    for fold in range(5):
        evaluated.extend(g.evaluate_saved(plan_path, seal, y[split == fold], ids, fold=fold))
    result_hash = g.save_plan(args.output / "PRIVATE_EVALUATION.json", evaluated)
    result = aggregate(evaluated)
    result.update(
        status="RETROSPECTIVE_REPLAY_COMPLETE",
        precheck_sha256=args.precheck_sha,
        bank_sha256=seal,
        private_evaluation_sha256=result_hash,
        records=len(evaluated),
        source_rows=dict(historical=37800, fresh=19200),
        cpu_wall_seconds=time.perf_counter() - start,
        new_model_forwards=0,
        b47_convergence=True,
    )
    g.save_plan(args.output / "AGGREGATES.json", result)
    print("replay_complete", flush=True)


if __name__ == "__main__":
    main()
