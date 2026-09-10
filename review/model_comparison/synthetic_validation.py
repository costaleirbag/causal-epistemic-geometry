"""Synthetic-only examples; no data reader, repository imports, or model inference."""
import json
import numpy as np


def sigmoid(z):
    return np.exp(-np.logaddexp(0.0, -np.asarray(z)))


def center(p):
    return p - p.mean(0, keepdims=True) - p.mean(1, keepdims=True) + p.mean()


def loss(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(np.mean(-y * np.log(p) - (1 - y) * np.log1p(-p)))


def fit(x, successes, trials, penalty):
    """Strictly convex ridge binomial objective; fractional counts only in synthetic checks."""
    b = np.zeros(x.shape[1])
    def objective(v):
        z = x @ v
        return float(np.sum(trials * np.logaddexp(0, z) - successes * z)
                     + .5 * np.sum(penalty * v * v))
    for iteration in range(100):
        p = sigmoid(x @ b)
        g = x.T @ (trials * p - successes) + penalty * b
        if np.max(np.abs(g)) / np.sum(trials) < 1e-9:
            return b, iteration, float(np.max(np.abs(g)) / np.sum(trials))
        h = x.T @ ((trials * p * (1 - p))[:, None] * x) + np.diag(penalty)
        step = np.linalg.solve(h, g)
        old = objective(b)
        for j in range(40):
            rate = 2.0 ** -j
            candidate = b - rate * step
            if objective(candidate) <= old - 1e-4 * rate * (g @ step):
                b = candidate
                break
        else:
            raise RuntimeError('LINE_SEARCH_FAILED')
    raise RuntimeError('NONCONVERGENCE')


def design(f, k, coefficients, model, train_controllers):
    nf = int(f.max()) + 1
    family = np.eye(nf)[f]
    if model == 'family':
        return family, np.full(nf, .01)
    if model == 'local':
        slopes = (family[:, :, None] * coefficients[k, None, :]).reshape(len(f), -1)
        return np.column_stack([family, slopes]), np.r_[np.full(nf, .01), np.ones(slopes.shape[1])]
    if model != 'rasch':
        raise ValueError(model)
    # Orthonormal contrast basis: skill sum zero over training controllers.
    n = len(train_controllers)
    q, _ = np.linalg.qr(np.eye(n)[:, :-1] - np.eye(n)[:, -1:])
    lookup = {int(v): j for j, v in enumerate(train_controllers)}
    skills = np.zeros((len(k), n - 1))
    for row, controller in enumerate(k):
        if int(controller) in lookup:
            skills[row] = q[lookup[int(controller)]]
    return np.column_stack([family, skills]), np.r_[np.full(nf, .01), np.ones(n - 1)]


def run():
    rng = np.random.default_rng(20260910)
    alpha = np.linspace(-3, 2, 16)
    theta = np.linspace(-1.5, 1.5, 12)
    rasch = sigmoid(alpha[:, None] + theta)
    assert np.all(np.diff(rasch, axis=1) > 0)
    energy = float(np.mean(center(rasch) ** 2))
    assert energy > 1e-4
    # A two-coordinate pedagogical panel, deliberately strong crossed slopes.
    # It is not a power calculation for the private rank-eight panel.
    angle = np.arange(12) * 2 * np.pi / 12
    c = np.column_stack([np.cos(angle), np.sin(angle)])
    beta = np.column_stack([2.5 * np.cos(np.arange(16) * 2 * np.pi / 16),
                            2.5 * np.sin(np.arange(16) * 2 * np.pi / 16)])
    true = sigmoid(.3 * alpha[:, None] + beta @ c.T)
    f, k = np.indices(true.shape)
    f, k = f.ravel(), k.ravel()
    train_k = np.array([j for j in range(12) if j % 4 != 0])
    train = np.isin(k, train_k)
    test = ~train
    counts = rng.binomial(8, true.ravel())
    independent = rng.binomial(256, true.ravel()) / 256
    scores, convergence = {}, {}
    for model in ['family', 'rasch', 'local']:
        x, pen = design(f, k, c, model, train_k)
        b, iterations, gradient = fit(x[train], counts[train], np.full(train.sum(), 8), pen)
        scores[model] = loss(independent[test], sigmoid(x[test] @ b))
        convergence[model] = {'iterations': iterations, 'normalized_gradient': gradient}
    assert scores['local'] + .05 < min(scores['family'], scores['rasch'])
    # Expected measurement energy: projection of independent Bernoulli mean noise.
    # Simulation shows attenuation of signal/observed-energy at fewer repeats.
    measurement = {}
    for repeats in [4, 8]:
        energies = [np.mean(center(rng.binomial(repeats, rasch) / repeats) ** 2)
                    for _ in range(256)]
        expected_noise = (1 - 1 / 16) * (1 - 1 / 12) * np.mean(rasch * (1 - rasch)) / repeats
        measurement[str(repeats)] = {'mean_observed_energy': float(np.mean(energies)),
                                    'expected_observed_energy': energy + float(expected_noise),
                                    'signal_over_expected_energy': energy / (energy + float(expected_noise))}
    assert measurement['8']['mean_observed_energy'] < measurement['4']['mean_observed_energy']
    return {'synthetic_only': True, 'seed': 20260910, 'rasch_centered_probability_energy': energy,
            'rasch_crossed_rankings': False, 'slope_heldout_controller_log_loss': scores,
            'convergence': convergence, 'measurement': measurement,
            'scope': 'Strong two-dimensional existence example; not pilot power or real-data evidence.'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
