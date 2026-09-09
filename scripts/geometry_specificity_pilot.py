"""Small matched-orientation pilot: pure design, estimators and qualification rules."""

from __future__ import annotations

import hashlib

import numpy as np

SPACES = ("ORIGINAL", "RANDOM_1", "RANDOM_2")
K = 24
MAX_BANK = 12
N = 60
R = 8


def seed(*parts):
    return int.from_bytes(
        hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big"
    ) % (2**31 - 1)


def make_geometry(basis, root_seed):
    if basis.shape[1] != 8 or not np.allclose(basis.T @ basis, np.eye(8), atol=1e-10):
        raise ValueError("ORIGINAL_BASIS")
    rng = np.random.Generator(np.random.PCG64DXSM(seed(root_seed, "coefficients")))
    c = rng.normal(size=(K, 8))
    c /= np.linalg.norm(c, axis=1, keepdims=True)
    if np.linalg.matrix_rank(c) != 8 or np.max(np.abs((c @ c.T) - np.eye(K))) > 0.98:
        raise ValueError("COEFFICIENT_DEGENERACY_NO_REDRAW")
    bases = [basis]
    for label in SPACES[1:]:
        rng = np.random.Generator(np.random.PCG64DXSM(seed(root_seed, label)))
        q, t = np.linalg.qr(rng.normal(size=basis.shape))
        q *= np.where(np.diag(t) >= 0, 1, -1)
        bases.append(q)
    vectors = np.stack([c @ q.T for q in bases])
    for v in vectors:
        if not np.allclose(v @ v.T, c @ c.T, atol=1e-10):
            raise ValueError("GRAM_MISMATCH")
    return c, vectors


def schedule(items, conditions, repeats, root_seed, phase):
    result = []
    used_seeds = set()
    for item in items:
        for r in range(repeats):
            order = np.random.Generator(
                np.random.PCG64DXSM(seed(root_seed, phase, item, r, "order"))
            ).permutation(conditions)
            for condition in order:
                # Common random numbers in calibration identify response movement;
                # independent condition seeds in evaluation, independent rollout seeds.
                sample = seed(
                    root_seed, phase, item, r, "shared" if phase == "calibration" else condition
                )
                if phase == "evaluation":
                    while sample in used_seeds:
                        sample = (sample + 1) % (2**31 - 1)
                    used_seeds.add(sample)
                result.append(
                    dict(item_id=item, condition=str(condition), rollout_index=r, seed=sample)
                )
    if len({(x["item_id"], x["condition"], x["rollout_index"]) for x in result}) != len(result):
        raise ValueError("SCHEDULE_DUPLICATE")
    return result


def dshape(y):
    if y.ndim != 3 or y.shape[2] < 2:
        raise ValueError("NEED_INDEPENDENT_ROLLOUTS")
    d = y[:, :, None, :] - y[:, None, :, :]
    d -= d.mean(axis=0, keepdims=True)
    r = y.shape[2]
    # U-statistic over distinct rollout pairs; negative estimates are retained.
    return ((d.sum(axis=3) ** 2 - (d * d).sum(axis=3)) / (r * (r - 1))).mean(axis=0)


def association(y, c):
    ix = np.triu_indices(len(c), 1)
    geom = (1 - c @ c.T)[ix]
    response = dshape(y)[ix]
    if np.std(response) < 1e-15 or np.std(geom) < 1e-15:
        return None

    def ranks(x):
        _, inverse, counts = np.unique(x, return_inverse=True, return_counts=True)
        return (np.cumsum(counts) - (counts + 1) / 2)[inverse]

    return float(np.corrcoef(ranks(geom), ranks(response))[0, 1])


def qualify(rows, deployment):
    index = {(r["item_id"], r["condition"], r["rollout_index"]): r for r in rows}
    if len(index) != len(rows) or len(rows) != 12 * 2 * (3 * K + 1):
        raise ValueError("CALIBRATION_COVERAGE")
    baseline = [r for r in rows if r["condition"] == "BASELINE"]
    bv = np.mean([r["commitment_valid"] for r in baseline])
    be = np.mean([r["semantic_evaluable"] for r in baseline])
    report = {}
    for s in SPACES:
        for i in range(K):
            condition = f"{s}_{i:02}"
            selected = [r for r in rows if r["condition"] == condition]
            if len(selected) != 24:
                raise ValueError("CALIBRATION_CONDITION_COVERAGE")
            valid = float(np.mean([r["commitment_valid"] for r in selected]))
            evaluable = float(np.mean([r["semantic_evaluable"] for r in selected]))
            stopped = float(np.mean([r["truncated"] for r in selected]))
            movement = float(
                np.mean(
                    [
                        r["generated_token_ids"]
                        != index[(r["item_id"], "BASELINE", r["rollout_index"])][
                            "generated_token_ids"
                        ]
                        for r in selected
                    ]
                )
            )
            passed = (
                valid >= max(0.90, bv - 0.05)
                and evaluable >= max(0.90, be - 0.05)
                and stopped <= 0.05
                and movement >= 0.10
                and deployment[condition]["relative_target_error"] <= 0.005
            )
            report[condition] = dict(
                validity=valid,
                evaluability=evaluable,
                terminal_failure_rate=stopped,
                movement=movement,
                passed=bool(passed),
            )
    keep = [i for i in range(K) if all(report[f"{s}_{i:02}"]["passed"] for s in SPACES)]
    return dict(
        qualified=bv >= 0.90 and be >= 0.90 and len(keep) >= 8,
        common_safe_indices=keep[:MAX_BANK],
        all_common_safe_indices=keep,
        baseline_validity=float(bv),
        baseline_evaluability=float(be),
        conditions=report,
    )
