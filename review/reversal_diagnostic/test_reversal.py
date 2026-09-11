from dataclasses import replace
import numpy as np
import pytest
from reversal import select, evaluate, TRAIN, HELD


def panel():
    fs = tuple(f'f{i:02d}' for i in range(60))
    ps = tuple(f'p{i:02d}' for i in range(12))
    p = np.full((60, 12), .5)
    p[:30, 0] = .2
    p[30:, 0] = .8
    return p, fs, ps


def choose(p, fs, ps, **kw):
    return select(p, fs, ps, train_rollouts=TRAIN, **kw)


def test_true_crossing_and_family_first_arithmetic():
    p, fs, ps = panel()
    s = choose(p, fs, ps)
    assert s.pair == ('p00', 'p01')
    y = np.zeros((60, 12, 4))
    y[:30, 1] = 1
    y[30:, 0] = 1
    result = evaluate(s, y, fs, ps, rollout_ids=HELD)
    assert result['practical_crossing'] and result['opposite_signs']
    assert result['low']['advantage'] == -1
    assert result['high']['advantage'] == 1


def test_same_sign_heterogeneity_is_not_reversal():
    p, fs, ps = panel()
    s = choose(p, fs, ps)
    y = np.zeros((60, 12, 4))
    y[:30, 0, 0] = 1
    y[30:, 0] = 1
    r = evaluate(s, y, fs, ps, rollout_ids=HELD)
    assert not r['opposite_signs'] and not r['practical_crossing']
    # Training heterogeneity with a globally monotonic policy order also fails.
    p[:, 0] = np.linspace(.6, .9, 60)
    assert choose(p, fs, ps) is None


def test_ties_and_input_order_invariance():
    p, fs, ps = panel()
    s = choose(p, fs, ps)
    assert s.low == fs[:30] and s.high == fs[30:]
    assert s == choose(p[::-1, ::-1], fs[::-1], ps[::-1])
    assert choose(np.full_like(p, .5), fs, ps) is None


@pytest.mark.parametrize('change', [dict(stage='B'), dict(model='H'),
    dict(orientation='RANDOM_1'), dict(penalty=.25)])
def test_training_provenance_boundary(change):
    with pytest.raises(ValueError):
        choose(*panel(), **change)


def test_rollout_and_outcome_boundary():
    p, fs, ps = panel()
    with pytest.raises(ValueError):
        select(p, fs, ps, train_rollouts=HELD)
    with pytest.raises(ValueError):
        select(np.zeros((60, 12, 8)), fs, ps, train_rollouts=TRAIN)
    s = choose(p, fs, ps)
    with pytest.raises(ValueError):
        evaluate(s, np.zeros((60, 12, 4)), fs, ps, rollout_ids=TRAIN)
    with pytest.raises(TypeError):
        choose(p, fs, ps, held_metrics={})
    # Evaluation receives no predictor and cannot return a different pair/group.
    for value in [0, 1]:
        assert not evaluate(s, np.full((60, 12, 4), value), fs, ps,
                            rollout_ids=HELD)['opposite_signs']
    assert choose(p, fs, ps) == s


def test_empty_duplicate_overlapping_groups_and_nonfinite():
    p, fs, ps = panel()
    s = choose(p, fs, ps)
    for bad in [replace(s, low=()), replace(s, high=s.low)]:
        with pytest.raises(ValueError):
            evaluate(bad, np.zeros((60, 12, 4)), fs, ps, rollout_ids=HELD)
    with pytest.raises(ValueError):
        choose(p[:0], (), ps)
    with pytest.raises(ValueError):
        choose(p, (fs[0],)*60, ps)
    p[0, 0] = np.nan
    with pytest.raises(ValueError):
        choose(p, fs, ps)


def test_small_crossing_is_not_practical():
    p, fs, ps = panel()
    s = choose(p, fs, ps)
    y = np.zeros((60, 12, 4))
    y[0, 1, 0] = y[30, 0, 0] = 1
    r = evaluate(s, y, fs, ps, rollout_ids=HELD)
    assert r['opposite_signs'] and not r['practical_crossing']
    p[:30, 0], p[30:, 0] = .49, .51
    assert choose(p, fs, ps) is None
