"""One fixed family-only Stage B estimator. No file or remote data loader."""
import json
import numpy as np

INTERCEPT_PENALTY = 0.01
SPACES = ('ORIGINAL', 'RANDOM_1', 'RANDOM_2')


def fit_counts(successes):
    """Solve 88 sigmoid(a) - s + .01 a = 0, independently per family."""
    s = np.asarray(successes, dtype=float)
    if not np.isfinite(s).all() or np.any((s < 0) | (s > 88) | (s != np.floor(s))):
        raise ValueError('integer successes in [0, 88] required')
    # Fixed bracket has opposite derivative signs for every admissible count.
    lo, hi = np.full(s.shape, -32.), np.full(s.shape, 32.)
    for _ in range(64):
        a = (lo + hi) / 2
        g = 88 * np.exp(-np.logaddexp(0., -a)) - s + INTERCEPT_PENALTY * a
        lo = np.where(g < 0, a, lo)
        hi = np.where(g >= 0, a, hi)
    a = (lo + hi) / 2
    residual = 88 * np.exp(-np.logaddexp(0., -a)) - s + INTERCEPT_PENALTY * a
    if np.max(np.abs(residual), initial=0) > 1e-11:
        raise ArithmeticError('stationarity check failed')
    return a


def training_indices(held):
    if isinstance(held, (bool, np.bool_)) or not isinstance(held, (int, np.integer)) or not 0 <= held < 12:
        raise ValueError('held controller must be integer 0..11')
    return np.delete(np.arange(12), held)


def predict_fold(panel, held):
    """Return (60, 1) logits; only training outcomes are accessed/validated."""
    panel = np.asarray(panel)
    if panel.shape != (60, 12, 8):
        raise ValueError('expected family/controller/rollout shape (60,12,8)')
    train = panel[:, training_indices(held), :]
    if not np.isin(train, [0, 1]).all():
        raise ValueError('binary training outcomes required')
    return fit_counts(train.sum(axis=(1, 2)))[:, None]


def evaluate_fold(logits, held_outcomes):
    """Frozen losses convention: nats/trial and squared probability error/trial."""
    a, y = np.asarray(logits), np.asarray(held_outcomes)
    if a.shape != (60, 1) or not np.isfinite(a).all() or y.shape != (60, 1, 8) or not np.isin(y, [0, 1]).all():
        raise ValueError('invalid held predictions/outcomes')
    raw = np.exp(-np.logaddexp(0., -a))
    p = np.clip(raw, 1e-6, 1-1e-6)[:, :, None]
    ll = -(y*np.log(p)+(1-y)*np.log1p(-p))
    br = (y-p)**2
    return {'family_log_loss': ll.mean(axis=(1, 2)),
            'family_brier': br.mean(axis=(1, 2)),
            'log_loss': float(ll.mean()), 'brier': float(br.mean()),
            'clipped_cells': int(np.count_nonzero(raw != p[:, :, 0]))}


def synthetic_demo():
    counts = np.array([0, 22, 44, 66, 88])
    a = fit_counts(counts)
    return {'synthetic_only': True, 'training_trials': 88,
            'successes': counts.tolist(), 'logits': a.tolist(),
            'probabilities': np.exp(-np.logaddexp(0., -a)).tolist()}


if __name__ == '__main__':
    print(json.dumps(synthetic_demo(), indent=2, allow_nan=False))
