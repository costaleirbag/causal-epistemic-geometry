"""Independent rational oracle and deliberate binary tie/negative cases."""
import importlib.util
from fractions import Fraction
from pathlib import Path
import numpy as np
import pytest

spec = importlib.util.spec_from_file_location('diagnostic', Path(__file__).parents[1]/'scripts/reconcile_geometry_specificity_numerics.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def rational(y):
    n, k, r = y.shape
    out = []
    for j in range(k):
        row = []
        for l in range(k):
            x = [[int(y[i,j,u])-int(y[i,l,u]) for u in range(r)] for i in range(n)]
            means = [Fraction(sum(a[u] for a in x), n) for u in range(r)]
            row.append(sum((a[u]-means[u])*(a[v]-means[v]) for a in x for u in range(r) for v in range(r) if u != v)/ (n*r*(r-1)))
        out.append(row)
    return out


@pytest.mark.parametrize('kind', ['duplicate', 'complement', 'negative', 'constant', 'repeated_families', 'random'])
def test_exact_against_fraction_oracle(kind):
    y = np.random.default_rng(16).integers(0, 2, (7, 4, 4))
    if kind == 'duplicate': y[:, 1] = y[:, 0]
    if kind == 'complement': y[:, 1] = 1-y[:, 0]
    if kind == 'negative':
        y[:, 0, 1::2] = 1-y[:, 0, ::2]
        y[:, 1] = 0
    if kind == 'constant': y[:] = 1
    if kind == 'repeated_families': y = y[[0,0,0,2,2,5,6]]
    a, b = d.numerator_gram(y), d.numerator_pairs(y)
    assert np.array_equal(a, b)
    den = y.shape[0]**2*y.shape[2]*(y.shape[2]-1)
    oracle = rational(y)
    assert all(Fraction(int(a[j,l]), den) == oracle[j][l] for j in range(4) for l in range(4))
    if kind == 'duplicate':
        assert a[0,2] == a[1,2] and a[0,3] == a[1,3]
    if kind == 'negative': assert a[0,1] < 0


def test_exact_ties_and_distinct_orders():
    y = np.zeros((7,4,4), int)
    y[:3,1,:] = 1
    y[:3,2,:] = 1
    y[3:6,3,:] = 1
    a = d.numerator_gram(y)
    v = a[np.triu_indices(4,1)]
    assert len(np.unique(v)) < len(v) and len(np.unique(v)) > 1
    assert np.array_equal(d.ranks(v), d.ranks(v*100))


def test_nonbinary_rejected():
    with pytest.raises(ValueError): d.numerator_gram(np.full((3,2,4), .5))
