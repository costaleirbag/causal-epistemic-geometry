"""Scoring and finite-orientation comparison, only after the complete evaluation seal."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import geometry_budget_replay as g
import geometry_specificity_pilot as p
import numpy as np
import run_geometry_specificity_pilot as runner

sys.path.insert(0, str(runner.ROOT / "src"))


def summarize(y, c, draws=2000):
    rho = [p.association(space, c) for space in y]
    result = dict(
        associations=rho,
        accuracy=[float(a.mean()) for a in y],
        mean_pair_displacement=[float(p.dshape(a)[np.triu_indices(len(c), 1)].mean()) for a in y],
    )
    if any(r is None for r in rho):
        result.update(classification="INCONCLUSIVE_DEGENERATE_RESPONSE", contrast=None)
        return result
    delta = rho[0] - (rho[1] + rho[2]) / 2
    rng = np.random.default_rng(2026090937)
    boot = []
    for _ in range(draws):
        ix = rng.integers(0, y.shape[1], y.shape[1])
        values = [p.association(a[ix], c) for a in y]
        if all(v is not None for v in values):
            boot.append(values[0] - (values[1] + values[2]) / 2)
    if len(boot) < 0.95 * draws:
        result.update(classification="INCONCLUSIVE_BOOTSTRAP_DEGENERACY", contrast=delta)
        return result
    ci = np.quantile(boot, [0.025, 0.975]).tolist()
    # Finite sampled-orientation evidence only. Margin is fixed before the pilot.
    if ci[0] > 0.15:
        classification = "OBSERVABLE_ALIGNMENT_HIGHER_FOR_ORIGINAL"
    elif ci[0] > -0.15 and ci[1] < 0.15 and min(rho) > 0.30:
        classification = "COMPARABLE_RELATIONAL_ALIGNMENT_IN_TESTED_ORIENTATIONS"
    else:
        classification = "INCONCLUSIVE_SPECIFICITY_CONTRAST"
    result.update(
        contrast=delta,
        paired_family_bootstrap_q025_q975=ci,
        bootstrap_valid_draws=len(boot),
        classification=classification,
        margin=0.15,
        interpretation=(
            "Conditional on these controller coefficients and two random orientations; "
            "no subspace-population or new-task claim. "
            "No absence-of-significance equivalence claim."
        ),
    )
    reproducibility = []
    for a in y:
        z = (
            a
            - a.mean(axis=1, keepdims=True)
            - a.mean(axis=0, keepdims=True)
            + a.mean(axis=(0, 1), keepdims=True)
        )
        stable = float(
            np.mean((z.sum(axis=2) ** 2 - (z * z).sum(axis=2)) / (a.shape[2] * (a.shape[2] - 1)))
        )
        energy = float(np.mean(z * z))
        reproducibility.append(
            dict(
                stable_product=stable,
                observed_energy=energy,
                ratio=stable / energy if energy > 0 else None,
            )
        )
    result["response_reproducibility"] = reproducibility
    result["specificity_warning"] = (
        "Observed rho differences can reflect unequal noise attenuation. "
        "Higher original alignment alone does not isolate latent geometric specificity; "
        "interpret with response scale and repeatability, especially for weak random controls."
    )
    result["rollout_half_associations"] = [
        [p.association(a[:, :, : p.R // 2], c), p.association(a[:, :, p.R // 2 :], c)] for a in y
    ]
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--official", type=Path, required=True)
    ap.add_argument("--precheck", type=Path, required=True)
    ap.add_argument("--precheck-sha", required=True)
    a = ap.parse_args()
    lock = runner.verify(a.precheck, a.precheck_sha)
    seal = runner.read(a.run / "EVALUATION_SEAL.json")
    if (
        seal["protocol_sha256"] != a.precheck_sha
        or g.sha(a.run / "evaluation.jsonl") != seal["journal_sha256"]
    ):
        raise ValueError("RAW_SEAL_MISMATCH")
    if g.sha(a.official) != lock["official_source_sha256"]:
        raise ValueError("OFFICIAL_HASH")
    selection = runner.read(a.run / "SELECTION_SEAL.json")
    for name, key in [
        ("DEPLOYMENT.json", "deployment_sha256"),
        ("EVALUATION_SCHEDULE.json", "schedule_sha256"),
    ]:
        if g.sha(a.run / name) != seal[key] or seal[key] != selection[key]:
            raise ValueError("SEALED_DEPENDENCY_CHANGED")
    if g.sha(a.run / "QUALIFICATION.json") != selection["qualification_sha256"]:
        raise ValueError("QUALIFICATION_CHANGED")
    prepared = runner.read(a.run / "PREPARED.json")
    if (
        prepared["protocol_sha256"] != a.precheck_sha
        or g.sha(a.run / "vectors.npz") != prepared["vectors_sha256"]
    ):
        raise ValueError("PREPARED_HASH")
    q = runner.read(a.run / "QUALIFICATION.json")
    if not q["qualified"]:
        raise ValueError("NOT_QUALIFIED")
    keep = q["common_safe_indices"]
    ids = prepared["evaluation_items"]
    items = runner.load_items(a.official, ids)
    raw = [
        json.loads(line)["row"] for line in (a.run / "evaluation.jsonl").read_text().splitlines()
    ]
    expected = {
        (r["item_id"], r["condition"], r["rollout_index"])
        for r in runner.read(a.run / "EVALUATION_SCHEDULE.json")
    }
    keys = [(r["item_id"], r["condition"], r["rollout_index"]) for r in raw]
    if len(set(keys)) != len(keys) or set(keys) != expected:
        raise ValueError("SCORE_COVERAGE")
    from epistemic_geometry.benchmarks.external.semantic_v3 import evaluate_external_answer_v3

    y = np.zeros((3, len(ids), len(keep), p.R))
    baseline = np.zeros((len(ids), p.R))
    scored = []
    for row in raw:
        failed = bool(row["terminal_answer_channel_failure"])
        score = evaluate_external_answer_v3(
            row["raw_output"],
            items[row["item_id"]].reference_answer,
            truncated=failed,
            runtime_error=False,
        )
        correct = bool(score.correct) and not failed
        record = dict(
            item_id=row["item_id"],
            condition=row["condition"],
            rollout_index=row["rollout_index"],
            correct=correct,
            valid=bool(score.commitment_valid) and not failed,
            evaluable=bool(score.semantic_evaluable) and not failed,
        )
        scored.append(record)
        i = ids.index(row["item_id"])
        r = row["rollout_index"]
        if row["condition"] == "BASELINE":
            baseline[i, r] = correct
        else:
            space, index = row["condition"].rsplit("_", 1)
            y[p.SPACES.index(space), i, keep.index(int(index)), r] = correct
    c = np.load(a.run / "vectors.npz", allow_pickle=False)["coefficients"][keep]
    result = summarize(y, c)
    result.update(
        baseline_accuracy=float(baseline.mean()),
        dimensions=list(y.shape),
        raw_sha256=seal["journal_sha256"],
        precheck_sha256=a.precheck_sha,
        eval_rows=len(raw),
        new_semantic_trajectories=seal["rows"]
        + runner.read(a.run / "CALIBRATION_SEAL.json")["rows"],
    )
    result["validity"] = {
        s: float(np.mean([r["valid"] for r in scored if r["condition"].startswith(s + "_")]))
        for s in p.SPACES
    }
    result["evaluability"] = {
        s: float(np.mean([r["evaluable"] for r in scored if r["condition"].startswith(s + "_")]))
        for s in p.SPACES
    }
    baseline_valid = float(np.mean([r["valid"] for r in scored if r["condition"] == "BASELINE"]))
    baseline_evaluable = float(
        np.mean([r["evaluable"] for r in scored if r["condition"] == "BASELINE"])
    )
    result["evaluation_channel_qualified"] = (
        baseline_valid >= 0.90
        and baseline_evaluable >= 0.90
        and all(v >= max(0.90, baseline_valid - 0.05) for v in result["validity"].values())
        and all(v >= max(0.90, baseline_evaluable - 0.05) for v in result["evaluability"].values())
    )
    if not result["evaluation_channel_qualified"]:
        result["association_classification_before_channel_guard"] = result["classification"]
        result["classification"] = "INCONCLUSIVE_EVALUATION_CHANNEL_CONFOUND"
    g.save_plan(a.run / "PRIVATE_SCORES.json", scored)
    g.save_plan(a.run / "RESULTS.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
