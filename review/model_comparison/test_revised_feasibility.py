import pytest
from revised_feasibility import fit_plan, schedule_gate


def fixture():
    return [dict(item_id=f, condition=c, rollout_index=r, seed=(f*37+c)*8+r)
            for f in range(60) for c in range(37) for r in range(8)]


def test_budget_counts_restarts_and_caches_only_identical_family_fit():
    full, reduced = fit_plan(), fit_plan(False)
    assert len(full) == len(set(full)) == 1428
    assert len(reduced) == len(set(reduced)) == 780
    assert sum(x[0] == 'A' for x in full) == 132
    assert sum(x[0] == 'B' for x in full) == 1296
    assert set(reduced).issubset(set(full))
    assert len(full) > 1000 >= len(reduced)


def test_reduction_preserves_all_actual_assignment_sensitivities_and_primary_controls():
    a, b = fit_plan(), fit_plan(False)
    assert [x for x in a if x[0] == 'A'] == [x for x in b if x[0] == 'A']
    assert [x for x in a if x[0] == 'B' and (x[3] == 0 or x[5] == 1)] == [x for x in b if x[0] == 'B']


def test_seed_gate_rejects_cross_half_coupling():
    rows = fixture()
    assert schedule_gate(rows)['half_split_compatible']
    rows[4]['seed'] = rows[0]['seed']
    with pytest.raises(ValueError, match='seed coupling'):
        schedule_gate(rows)


def test_seed_gate_rejects_duplicate_and_missing_keys():
    rows = fixture()
    with pytest.raises(ValueError, match='coverage'):
        schedule_gate(rows[:-1])
    rows[-1] = rows[0]
    with pytest.raises(ValueError, match='coverage'):
        schedule_gate(rows)
