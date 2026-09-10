import numpy as np
from synthetic_validation import center, design, fit, loss, run, sigmoid


def test_examples():
    result = run()
    assert result['synthetic_only'] and not result['rasch_crossed_rankings']


def test_optimizer_and_extreme_losses():
    x = np.ones((2, 1))
    b, _, gradient = fit(x, np.array([0., 10.]), np.array([10., 10.]), np.array([.01]))
    assert abs(b[0]) < 1e-10 and gradient < 1e-9
    b, _, _ = fit(x, np.array([10., 10.]), np.array([10., 10.]), np.array([.01]))
    assert np.isfinite(b).all()
    assert np.isfinite(loss(np.array([1., 0.]), np.array([0., 1.])))
    assert np.isfinite(sigmoid(np.array([-10000., 10000.]))).all()


def test_unseen_skill_and_centering():
    f = np.array([0, 0, 0])
    k = np.array([0, 1, 2])
    x, _ = design(f, k, np.zeros((3, 2)), 'rasch', [0, 1])
    assert np.all(x[2, 1:] == 0)
    assert np.allclose(x[:2, 1:].sum(0), 0)
    assert np.allclose(center(np.arange(12).reshape(3, 4)), 0)


def test_fit_has_no_test_outcome_dependency():
    x = np.column_stack([np.ones(4), np.arange(4)])
    y = np.array([0., 1., 0., 1.])
    mask = np.array([True, True, False, False])
    b, _, _ = fit(x[mask], y[mask], np.ones(2), np.ones(2))
    y[~mask] = 1 - y[~mask]
    other, _, _ = fit(x[mask], y[mask], np.ones(2), np.ones(2))
    assert np.array_equal(b, other)
