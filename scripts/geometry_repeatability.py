"""Retrospective two-rollout repeatability; no model inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geometry_budget_replay as g
import numpy as np
import run_geometry_budget_replay as source


def centered(y):
    return (
        y
        - y.mean(axis=1, keepdims=True)
        - y.mean(axis=0, keepdims=True)
        + y.mean(axis=(0, 1), keepdims=True)
    )


def components(y):
    z = centered(y)
    stable = float(np.mean(z[:, :, 0] * z[:, :, 1]))
    energy = float(np.mean(z**2))
    noise = float(np.mean((z[:, :, 0] - z[:, :, 1]) ** 2) / 2)
    marginal = y.mean(axis=0)
    correlation = None
    if np.std(marginal[:, 0]) > 0 and np.std(marginal[:, 1]) > 0:
        correlation = float(np.corrcoef(marginal.T)[0, 1])
    return dict(
        stable_product=stable,
        observed_energy=energy,
        disagreement_energy=noise,
        signed_reproducibility=stable / energy if energy > 0 else None,
        marginal_policy_accuracy_correlation=correlation,
    )


def winners(train_rollout, order):
    # order is fixed independently of evaluation labels; handles all-wrong ties.
    return np.asarray(order)[np.argmax(train_rollout[:, order], axis=1)]


def cross_rollout(y, seeds=range(2026090920, 2026090984)):
    values = []
    for seed in seeds:
        order = np.random.default_rng(seed).permutation(y.shape[1])
        accuracy = []
        for r in (0, 1):
            selected = winners(y[:, :, r], order)
            accuracy.append(float(y[np.arange(len(y)), selected, 1 - r].mean()))
        values.append(float(np.mean(accuracy)))
    return dict(
        cross_rollout_accuracy_mean=float(np.mean(values)),
        cross_rollout_seed_q025_q975=np.quantile(values, [0.025, 0.975]).tolist(),
        empirical_mean_before_max=float(y.mean(axis=2).max(axis=1).mean()),
        uniform_policy_accuracy=float(y.mean()),
        marginal_policy_accuracy_min_max=[
            float(y.mean(axis=(0, 2)).min()),
            float(y.mean(axis=(0, 2)).max()),
        ],
        interpretation=(
            "Privileged same-family labeled repetition; "
            "not deployable routing or held-out-family utility."
        ),
    )


def analyze(y):
    result = components(y)
    rng = np.random.default_rng(2026090917)
    boot = [components(y[rng.integers(0, len(y), len(y))]) for _ in range(2000)]
    result["family_bootstrap_q025_q975"] = {
        key: np.quantile([r[key] for r in boot if r[key] is not None], [0.025, 0.975]).tolist()
        for key in (
            "stable_product",
            "observed_energy",
            "disagreement_energy",
            "signed_reproducibility",
        )
        if any(r[key] is not None for r in boot)
    }
    z = centered(y)
    rng = np.random.default_rng(2026090918)
    broken = {"policy_permutation": [], "family_permutation": []}
    for _ in range(999):
        broken["policy_permutation"].append(
            float(np.mean(z[:, :, 0] * z[:, rng.permutation(y.shape[1]), 1]))
        )
        broken["family_permutation"].append(
            float(np.mean(z[:, :, 0] * z[rng.permutation(len(y)), :, 1]))
        )
    result["broken_alignment_descriptive"] = {
        k: dict(mean=float(np.mean(v)), q025_q975=np.quantile(v, [0.025, 0.975]).tolist())
        for k, v in broken.items()
    }
    result["oracle_diagnostic"] = cross_rollout(y)
    # Separate direct projection arithmetic audit of the primary scalar quantities.
    a = np.eye(len(y)) - np.ones((len(y), len(y))) / len(y)
    b = np.eye(y.shape[1]) - np.ones((y.shape[1], y.shape[1])) / y.shape[1]
    u, v = a @ y[:, :, 0] @ b, a @ y[:, :, 1] @ b
    direct = dict(
        stable_product=float(np.sum(u * v) / u.size),
        observed_energy=float((np.sum(u * u) + np.sum(v * v)) / (2 * u.size)),
        disagreement_energy=float(np.sum((u - v) ** 2) / (2 * u.size)),
    )
    discrepancy = max(abs(result[k] - v) for k, v in direct.items())
    if (
        discrepancy > 1e-12
        or abs(result["observed_energy"] - result["stable_product"] - result["disagreement_energy"])
        > 1e-12
    ):
        raise ValueError("NUMERICAL_AUDIT")
    result["audit_maximum_difference"] = discrepancy
    result["interpretation"] = (
        "Exploratory exposed-panel estimate, fixed controller population, two rollout draws. Conditional independence assumed for squared-interaction interpretation. Permutation summaries are not p-values."
    )
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "precheck", "historical-scores", "fresh-scores", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--precheck-sha", required=True)
    a = p.parse_args()
    if g.sha(a.precheck) != a.precheck_sha:
        raise ValueError("PRECHECK_HASH")
    lock = json.loads(a.precheck.read_text())
    for name, expected in lock["sources"].items():
        if g.sha(a.root / name) != expected:
            raise ValueError("SOURCE_HASH")
    budget = json.loads((a.root / "review/geometry_budget_replay/PRECHECK.json").read_text())
    for name, expected in budget["sources"].items():
        if name not in ("historical_scores", "fresh_scores") and g.sha(a.root / name) != expected:
            raise ValueError("HISTORICAL_PUBLIC_SOURCE_HASH")
    ids, _ = source.geometry(a.root)
    items = json.loads((a.root / source.HIST / "SEMANTIC_PANEL_MANIFEST.json").read_text())[
        "item_ids"
    ]
    y, _ = source.load_sources(a.historical_scores, a.fresh_scores, budget["sources"], items, ids)
    result = analyze(y)
    result.update(precheck_sha256=a.precheck_sha, dimensions=list(y.shape), new_model_forwards=0)
    g.save_plan(a.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
