"""Additive loader repair: use the already pinned full panel for evaluation items."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geometry_budget_replay as g
import run_geometry_specificity_pilot as runner

ORIGINAL_LOAD_ITEMS = runner.load_items
AMENDMENT = runner.ROOT / "review/geometry_specificity/LOADER_AMENDMENT_1.json"


def load_items(official, ids):
    from epistemic_geometry.benchmarks.external.base import ExternalItem

    panel = runner.read(runner.ROOT / runner.PANEL)
    records = {r["item_id"]: r for r in panel["items"]}
    old_ids = set(ids) - records.keys()
    result = ORIGINAL_LOAD_ITEMS(official, old_ids) if old_ids else {}
    for item_id in set(ids) & records.keys():
        row = records[item_id]
        result[item_id] = ExternalItem(
            item_id=item_id,
            benchmark="CRUXEval",
            subtask="output_prediction",
            prompt=row["prompt"],
            reference_answer=row["reference_answer"],
            evaluator="python_literal",
            source_revision=str(panel["dataset_revision"]),
            metadata={},
        )
    if set(result) != set(ids):
        raise ValueError("AMENDED_ITEM_COVERAGE")
    return result


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--loader-amendment-sha", required=True)
    parser.add_argument("--analysis", action="store_true")
    args, remaining = parser.parse_known_args()
    if g.sha(AMENDMENT) != args.loader_amendment_sha:
        raise ValueError("AMENDMENT_HASH")
    amendment = runner.read(AMENDMENT)
    if g.sha(Path(__file__)) != amendment["adapter_sha256"]:
        raise ValueError("ADAPTER_HASH")
    lock_path = runner.ROOT / "review/geometry_specificity/PILOT_PRECHECK.json"
    runner.verify(lock_path, amendment["original_precheck_sha256"])
    # Explicit versioned adapter; frozen sources and scientific identities stay intact.
    runner.load_items = load_items
    sys.argv = [sys.argv[0], *remaining]
    if args.analysis:
        import analyze_geometry_specificity_pilot as analysis

        analysis.main()
    else:
        runner.main()


if __name__ == "__main__":
    main()
