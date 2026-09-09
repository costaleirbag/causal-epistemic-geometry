import sys

import numpy as np

sys.path.insert(0, "scripts")
import geometry_repeatability as r  # noqa: E402


def test_additive_and_stable_interaction():
    a = np.tile(np.array([0.0, 1.0, 0.0, 1.0])[:, None, None], (1, 6, 2))
    assert r.components(a)["observed_energy"] == 0
    checker = (np.indices((20, 6)).sum(axis=0) % 2).astype(float)
    y = np.stack([checker, checker], axis=2)
    c = r.components(y)
    assert c["signed_reproducibility"] == 1
    assert c["disagreement_energy"] == 0
    assert np.allclose(r.centered(y).mean(axis=0), 0)
    assert np.allclose(r.centered(y).mean(axis=1), 0)


def test_independent_noise_and_negative_retained():
    rng = np.random.default_rng(3)
    y = rng.integers(0, 2, (10000, 20, 2)).astype(float)
    c = r.components(y)
    assert abs(c["signed_reproducibility"]) < 0.015
    assert abs(c["observed_energy"] - c["stable_product"] - c["disagreement_energy"]) < 1e-12
    a = (np.indices((20, 6)).sum(axis=0) % 2).astype(float)
    c = r.components(np.stack([a, 1 - a], axis=2))
    assert c["signed_reproducibility"] == -1


def test_winners_and_evaluation_independence():
    train = np.array([[0, 1, 1], [0, 0, 0], [1, 0, 0]])
    order = np.array([2, 1, 0])
    before = r.winners(train, order)
    evaluation = np.zeros_like(train)
    evaluation[:] = 1
    assert np.array_equal(before, r.winners(train, order))
    assert before.tolist() == [2, 2, 0]
    y = np.stack([train, train], axis=2)
    assert r.cross_rollout(y)["cross_rollout_accuracy_mean"] == 2 / 3


def test_independent_projection_audit_and_axis_invariance():
    rng = np.random.default_rng(7)
    y = rng.integers(0, 2, (20, 7, 2)).astype(float)
    a = r.analyze(y)
    assert a["audit_maximum_difference"] < 1e-12
    c = r.components(y[::-1, ::-1])
    for key in ("stable_product", "observed_energy", "disagreement_energy"):
        assert abs(c[key] - a[key]) < 1e-12
