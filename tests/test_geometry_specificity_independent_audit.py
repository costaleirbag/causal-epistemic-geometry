import numpy as np
import pytest
from scripts.audit_geometry_specificity_pilot import distances, ranks, correlation, classify, calculate


def test_tied_ranks():
    assert ranks([4, 1, 4, 2, 2]).tolist() == [3.5, 0, 3.5, 1.5, 1.5]


def test_distinct_products_against_literal_pairs():
    y = np.random.default_rng(71).integers(0, 2, (7, 4, 3)).astype(float)
    expected = np.zeros((4, 4))
    for k in range(4):
        for l in range(4):
            d = y[:, k] - y[:, l]
            d -= d.mean(axis=0)
            expected[k,l] = np.mean([d[i,r]*d[i,s] for i in range(7) for r in range(3) for s in range(3) if r != s])
    np.testing.assert_allclose(distances(y), expected, atol=1e-15)
    np.testing.assert_allclose(distances(y + np.arange(7)[:,None,None]), expected, atol=1e-15)


def test_negative_noise_is_retained():
    y = np.array([[[1,0],[0,1]], [[0,1],[1,0]]],float)
    assert distances(y)[0,1] == -1
    with pytest.raises(ValueError): distances(y[:,:,:1])


def test_degeneracy_and_strict_margin():
    c = np.array([[1,0],[0,1],[-1,0]],float)
    y = np.zeros((3,5,3,8))
    assert correlation(y[0],c) is None
    assert calculate(y,c)['classification'] == 'INCONCLUSIVE_DEGENERATE_RESPONSE'
    assert classify([.6,.6,.6],[-.15,.1]) == 'INCONCLUSIVE_SPECIFICITY_CONTRAST'
    assert classify([.6,.6,.6],[-.14,.14]) == 'COMPARABLE_RELATIONAL_ALIGNMENT_IN_TESTED_ORIENTATIONS'
    assert classify([.6,.2,.2],[.151,.4]) == 'OBSERVABLE_ALIGNMENT_HIGHER_FOR_ORIGINAL'


def test_paired_bootstrap_identical_spaces_zero_contrast():
    rng = np.random.default_rng(991)
    c = rng.normal(size=(4,3))
    c /= np.linalg.norm(c,axis=1,keepdims=True)
    a = rng.integers(0,2,(9,4,8)).astype(float)
    result = calculate(np.stack([a,a,a]),c,draws=30)
    assert result['contrast'] == 0
    assert result['paired_family_bootstrap_q025_q975'] == [0,0]
    assert result['bootstrap_valid_draws'] == 30


def test_integer_ties_and_rollout_permutation():
    from scripts.audit_geometry_specificity_pilot import exact_correlation
    c = np.array([[1,0],[0,1],[-1,0]],float)
    a = np.array([[[1,1],[0,0],[1,1]],[[0,0],[1,1],[0,0]]],float)
    assert exact_correlation(a,c) == -1
    assert exact_correlation(a[:,:,::-1],c) == -1
