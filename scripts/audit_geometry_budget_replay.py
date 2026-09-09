"""Post-run numerical audit of sealed banks using direct per-family arithmetic."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import geometry_budget_replay as g
import numpy as np
import run_geometry_budget_replay as driver


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--historical-scores", type=Path, required=True)
    p.add_argument("--fresh-scores", type=Path, required=True)
    p.add_argument("--results", type=Path, required=True)
    args = p.parse_args()
    read = lambda p: json.loads(p.read_text())  # noqa: E731
    public = read(args.results / "AGGREGATES.json")
    lock = read(args.root / "review/geometry_budget_replay/PRECHECK.json")
    banks = read(args.results / "PRIVATE_BANKS.json")
    evaluated = read(args.results / "PRIVATE_EVALUATION.json")
    if (
        g.sha(args.results / "PRIVATE_BANKS.json") != public["bank_sha256"]
        or g.sha(args.results / "PRIVATE_EVALUATION.json") != public["private_evaluation_sha256"]
    ):
        raise ValueError("SEALED_ARTIFACT_MISMATCH")
    ids, _ = driver.geometry(args.root)
    items = read(args.root / driver.HIST / "SEMANTIC_PANEL_MANIFEST.json")["item_ids"]
    y, t = driver.load_sources(
        args.historical_scores, args.fresh_scores, lock["sources"], items, ids
    )
    split = g.folds(items)
    key = lambda r: (r["fold"], r["seed"], r["budget"], r["ordering"], r["selector"])  # noqa: E731
    bykey = {key(r): r for r in evaluated}
    if len(bykey) != 5120 or len(banks) != 5120:
        raise ValueError("AUDIT_COVERAGE")
    independent = {}
    maximum = 0.0
    for row in banks:
        bank = [ids.index(p) for p in row["bank"]]
        acquired = [ids.index(p) for p in row["acquired"]]
        champ = ids.index(row["champion"])
        test = np.flatnonzero(split == row["fold"])
        train = np.flatnonzero(split != row["fold"])
        # Direct sums over both rollouts, then max; no primary evaluator used.
        scores = np.sum(y[test][:, bank], axis=2) / 2
        metrics = dict(
            opportunity=float(sum(max(a) for a in scores) / len(test)),
            fixed_policy_accuracy=float(np.sum(y[test, champ]) / (2 * len(test))),
            uniform_policy_accuracy=float(np.sum(scores) / (len(test) * len(bank))),
        )
        for m, value in metrics.items():
            maximum = max(maximum, abs(value - bykey[key(row)][m]))
        if row["tokens"] != int(np.sum(t[train][:, acquired])) or row["cells"] != len(
            train
        ) * 2 * len(acquired):
            raise ValueError("AUDIT_COST")
        training = {
            p: float(np.sum(y[train, ids.index(p)]) / (2 * len(train))) for p in row["acquired"]
        }
        champion = min(row["acquired"], key=lambda p: (-training[p], p))
        if champion != row["champion"]:
            raise ValueError("AUDIT_CHAMPION")
        independent[key(row)] = metrics
    aggregate_difference = 0.0
    for cell in public["cells"]:
        b, o, s = cell["budget"], cell["ordering"], cell["selector"]
        for m in driver.METRICS:
            value = sum(
                independent[(f, seed, b, o, s)][m]
                for f, seed in itertools.product(range(5), g.SEEDS)
            ) / (5 * len(g.SEEDS))
            aggregate_difference = max(
                aggregate_difference, abs(value - cell["metrics"][m]["mean"])
            )
    if maximum > 1e-12 or aggregate_difference > 1e-12:
        raise ValueError("AUDIT_NUMERICAL_DIFFERENCE")
    result = dict(
        status="PASS",
        records_checked=len(banks),
        bank_sha256=public["bank_sha256"],
        evaluation_sha256=public["private_evaluation_sha256"],
        maximum_metric_difference=maximum,
        maximum_aggregate_mean_difference=aggregate_difference,
        costs_and_champions_verified=True,
        audit_uses_primary_numeric_loader=True,
        primary_evaluator_or_aggregator_used=False,
        runtime=dict(numpy=np.__version__),
        new_model_forwards=0,
    )
    g.save_plan(args.results / "AUDIT.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
