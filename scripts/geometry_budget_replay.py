"""CPU-only retrospective acquisition replay. No CLI runs scientific curves.

Selectors receive acquired training arrays only; test evaluation requires a
persisted bank manifest. Frozen experiment modules are not modified/imported.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

K = 8
BUDGETS = (8, 16, 32, 47)
SEEDS = tuple(range(2026090901, 2026090965))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def folds(ids):
    ranked = sorted(
        range(len(ids)),
        key=lambda i: hashlib.sha256(f"{ids[i]}|q3-realizable-utility-v1".encode()).hexdigest(),
    )
    result = np.empty(len(ids), dtype=int)
    for rank, i in enumerate(ranked):
        result[i] = rank % 5
    return result


def load_numeric(path, expected_sha, items, conditions):
    """Hash-pinned allowlist loader; no answer fields retained or emitted."""
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError("SOURCE_HASH_MISMATCH")
    item_index = {item: i for i, item in enumerate(items)}
    policy_index = {p: i for i, p in enumerate(conditions)}
    if len(item_index) != len(items) or len(policy_index) != len(conditions):
        raise ValueError("DUPLICATE_AXIS")
    correct = np.empty((len(items), len(conditions), 2), dtype=float)
    tokens = np.empty_like(correct)
    seen = set()
    for line in raw.splitlines():
        row = json.loads(line)
        key = (row["item_id"], row["condition"], row["rollout_index"])
        if key in seen:
            raise ValueError("DUPLICATE_KEY")
        if (
            key[0] not in item_index
            or key[1] not in policy_index
            or type(key[2]) is not int
            or key[2] not in (0, 1)
        ):
            raise ValueError("UNEXPECTED_KEY")
        if (
            type(row["correct"]) is not bool
            or type(row["generated_token_count"]) is not int
            or row["generated_token_count"] < 0
        ):
            raise ValueError("INVALID_NUMERIC_FIELD")
        i, j, r = item_index[key[0]], policy_index[key[1]], key[2]
        correct[i, j, r] = row["correct"]
        tokens[i, j, r] = row["generated_token_count"]
        seen.add(key)
    if len(seen) != correct.size:
        raise ValueError("MISSING_KEY")
    return correct, tokens


def acquisition_orders(ids, distance, seed):
    if (
        len(set(ids)) != len(ids)
        or distance.shape != (len(ids), len(ids))
        or not np.isfinite(distance).all()
        or not np.allclose(distance, distance.T)
        or np.any(distance < 0)
        or not np.allclose(np.diag(distance), 0, atol=1e-12, rtol=0)
    ):
        raise ValueError("GEOMETRY_INVALID")
    rng = np.random.default_rng(seed)
    uniform = list(rng.permutation(sorted(ids)))
    selected = [uniform[0]]
    ix = {p: i for i, p in enumerate(ids)}
    while len(selected) < len(ids):
        remaining = sorted(set(ids) - set(selected))
        values = {p: min(distance[ix[p], ix[q]] for q in selected) for p in remaining}
        best = max(values.values())
        selected.append(min(p for p in remaining if values[p] == best))
    return {"A0_MAXIMIN": selected, "UNIFORM": uniform}


class Acquisition:
    """Construct with training rows ONLY; no interface to test or unopened labels."""

    def __init__(self, train_correct, train_tokens, ids):
        if train_correct.shape != train_tokens.shape or train_correct.shape[1:] != (len(ids), 2):
            raise ValueError("TRAIN_SHAPE")
        self.__correct = train_correct.copy()
        self.__tokens = train_tokens.copy()
        self.__index = {p: i for i, p in enumerate(ids)}
        self._opened = {}
        self.cells = 0
        self.tokens = 0

    def acquire(self, policy):
        if policy in self._opened:
            raise ValueError("DUPLICATE_QUERY")
        j = self.__index[policy]
        self._opened[policy] = self.__correct[:, j, :].copy()
        self.cells += self.__correct.shape[0] * 2
        self.tokens += int(self.__tokens[:, j, :].sum())

    def observed(self):
        return {p: a.copy() for p, a in sorted(self._opened.items())}


def select_bank(observed, method, k=K):
    if len(observed) < k:
        raise ValueError("INSUFFICIENT_ACQUIRED")
    # Average rollouts BEFORE maximum over policies, in both selection/evaluation.
    means = {p: a.mean(axis=1) for p, a in observed.items()}
    if method == "TOP_COMPETENCE":
        return sorted(means, key=lambda p: (-float(means[p].mean()), p))[:k]
    if method != "GREEDY_OPPORTUNITY":
        raise ValueError("UNKNOWN_SELECTOR")
    chosen = []
    while len(chosen) < k:
        remaining = sorted(set(means) - set(chosen))
        utility = {
            p: float(np.stack([means[q] for q in chosen + [p]], axis=1).max(axis=1).mean())
            for p in remaining
        }
        best = max(utility.values())
        chosen.append(min(p for p in remaining if utility[p] == best))
    return chosen


def plan_banks(train_correct, train_tokens, ids, distance, seed, budgets=BUDGETS, k=K):
    records = []
    for ordering, order in acquisition_orders(ids, distance, seed).items():
        facade = Acquisition(train_correct, train_tokens, ids)
        for b, policy in enumerate(order, 1):
            facade.acquire(policy)
            if b not in budgets:
                continue
            observed = facade.observed()
            for method in ("TOP_COMPETENCE", "GREEDY_OPPORTUNITY"):
                bank = select_bank(observed, method, k)
                champion = min(bank, key=lambda p: (-float(observed[p].mean()), p))
                records.append(
                    dict(
                        ordering=ordering,
                        selector=method,
                        seed=seed,
                        budget=b,
                        bank=bank,
                        champion=champion,
                        cells=facade.cells,
                        tokens=facade.tokens,
                        acquired=list(order[:b]),
                    )
                )
    return records


def save_plan(path, plan):
    """Exclusive prospective bank persistence; caller supplies all folds/seeds."""
    with Path(path).open("x") as f:
        json.dump(plan, f, indent=2)
        f.flush()
        import os

        os.fsync(f.fileno())
    return sha(path)


def evaluate_saved(path, expected_sha, test_correct, ids, *, fold=None):
    if sha(path) != expected_sha:
        raise ValueError("BANK_SEAL_MISMATCH")
    records = json.loads(Path(path).read_text())
    if fold is None and any("fold" in row for row in records):
        raise ValueError("FOLD_REQUIRED")
    if fold is not None:
        records = [row for row in records if row.get("fold") == fold]
        if not records:
            raise ValueError("FOLD_MISSING")
    ix = {p: i for i, p in enumerate(ids)}
    if test_correct.ndim != 3 or test_correct.shape[1:] != (len(ids), 2):
        raise ValueError("TEST_SHAPE")
    y = test_correct.mean(axis=2)
    return [
        dict(
            row,
            opportunity=float(y[:, [ix[p] for p in row["bank"]]].max(axis=1).mean()),
            fixed_policy_accuracy=float(y[:, ix[row["champion"]]].mean()),
            uniform_policy_accuracy=float(y[:, [ix[p] for p in row["bank"]]].mean()),
        )
        for row in records
    ]
