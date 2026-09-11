"""Pure in-memory diagnostic. No loaders, fitting, CLI, or filesystem access."""
from dataclasses import dataclass
from itertools import combinations
import math
import numpy as np

MARGIN = 0.05
FAMILIES = 60
POLICIES = 12
GROUP_SIZE = 30
TRAIN = (0, 1, 2, 3)
HELD = (4, 5, 6, 7)


def identities(values, size):
    values = tuple(values)
    if (len(values) != size or any(type(v) is not str or not v for v in values)
            or len(set(values)) != size):
        raise ValueError('complete unique frozen string identities required')
    return values


@dataclass(frozen=True)
class Selection:
    pair: tuple
    low: tuple
    high: tuple
    train_low: float
    train_high: float


def select(predictions, family_ids, policy_ids, *, train_rollouts,
           stage='A', orientation='ORIGINAL', model='C', penalty=1):
    """Only C training-fit probabilities enter this boundary; never outcomes."""
    if (tuple(train_rollouts) != TRAIN or stage != 'A' or
            orientation != 'ORIGINAL' or model != 'C' or penalty != 1):
        raise ValueError('fixed primary training provenance required')
    fs = identities(family_ids, FAMILIES)
    ps = identities(policy_ids, POLICIES)
    p = np.asarray(predictions, dtype=float)
    if p.shape != (FAMILIES, POLICIES) or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError('finite family by policy probabilities required')
    candidates = []
    # Canonical summation order makes input ordering irrelevant.
    for a, b in combinations(sorted(ps), 2):
        d = p[:, ps.index(a)] - p[:, ps.index(b)]
        ordered = sorted(range(FAMILIES), key=lambda f: (float(d[f]), fs[f]))
        lo, hi = ordered[:GROUP_SIZE], ordered[GROUP_SIZE:]
        low = math.fsum(float(d[f]) for f in lo) / GROUP_SIZE
        high = math.fsum(float(d[f]) for f in hi) / GROUP_SIZE
        if low <= -MARGIN and high >= MARGIN:
            s = Selection((a, b), tuple(fs[f] for f in lo), tuple(fs[f] for f in hi), low, high)
            candidates.append((min(-low, high), s))
    if not candidates:
        return None  # NO_GO: do not open held outcomes or relax the rule.
    return min(candidates, key=lambda x: (-x[0], x[1].pair))[1]


def evaluate(selection, outcomes, family_ids, policy_ids, *, rollout_ids):
    """Fixed pair only; paired family-first signed accuracy differences."""
    if not isinstance(selection, Selection) or tuple(rollout_ids) != HELD:
        raise ValueError('sealed selection and held rollouts required')
    fs = identities(family_ids, FAMILIES)
    ps = identities(policy_ids, POLICIES)
    s = selection
    if (len(s.pair) != 2 or s.pair != tuple(sorted(set(s.pair))) or
            not set(s.pair) <= set(ps) or len(s.low) != GROUP_SIZE or len(s.high) != GROUP_SIZE or
            len(set(s.low + s.high)) != FAMILIES or set(s.low + s.high) != set(fs) or
            not math.isfinite(s.train_low) or not math.isfinite(s.train_high) or
            s.train_low > -MARGIN or s.train_high < MARGIN):
        raise ValueError('invalid fixed selection')
    y = np.asarray(outcomes, dtype=float)
    if y.shape != (FAMILIES, POLICIES, 4) or not np.isfinite(y).all() or not np.isin(y, [0, 1]).all():
        raise ValueError('complete binary held panel required')
    d = y[:, ps.index(s.pair[0]), :] - y[:, ps.index(s.pair[1]), :]
    def group(ids):
        rows = d[[fs.index(f) for f in ids]]
        family = rows.mean(axis=1)
        return {'advantage': float(family.mean()),
                'rollout_advantages': rows.mean(axis=0).tolist(),
                'family_range': [float(family.min()), float(family.max())]}
    low, high = group(s.low), group(s.high)
    crossing = low['advantage'] < 0 and high['advantage'] > 0
    return {'low': low, 'high': high, 'opposite_signs': crossing,
            'practical_crossing': low['advantage'] <= -MARGIN and high['advantage'] >= MARGIN,
            'interpretation': 'exploratory finite-panel description; no confirmation or calibrated interval'}
