import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from family_baseline import fit_counts, predict_fold, training_indices, evaluate_fold
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'model_comparison'))
from finite_models import Model, split_panel, losses


def test_all_counts_unique_optimum_and_symmetry():
    s = np.arange(89)
    a = fit_counts(s)
    p = 1/(1+np.exp(-a))
    assert np.max(np.abs(88*p-s+.01*a)) < 1e-11
    assert np.all(np.diff(a)>0)
    np.testing.assert_allclose(a, -a[::-1], atol=2e-12)
    assert a[44] == pytest.approx(0, abs=1e-14)
    assert 0 < p[0] < .001 and .999 < p[-1] < 1
    # Strict convexity and increase on either side of the stationary solution.
    objective = lambda z: 88*np.logaddexp(0,z)-s*z+.005*z*z
    assert np.all(objective(a+.01) > objective(a))
    assert np.all(objective(a-.01) > objective(a))


def test_exact_masks_and_held_labels_unread_all_folds():
    rng=np.random.default_rng(12)
    panel=rng.integers(0,2,(60,12,8)).astype(float)
    x=rng.normal(size=(12,8))
    original=panel.copy()
    for held in range(12):
        indices=training_indices(held)
        assert len(indices)==11 and held not in indices
        counts,n,test,_,_=split_panel(panel,x,'B',held)
        np.testing.assert_array_equal(counts.sum(1),panel[:,indices,:].sum((1,2)))
        assert np.all(n.sum(1)==88)
        prediction=predict_fold(panel,held)
        poisoned=panel.copy(); poisoned[:,held,:]=np.nan
        np.testing.assert_array_equal(prediction,predict_fold(poisoned,held))
        poisoned[:,held,:]=1-panel[:,held,:]
        np.testing.assert_array_equal(prediction,predict_fold(poisoned,held))
        np.testing.assert_array_equal(test,panel[:,held:held+1,:])
    np.testing.assert_array_equal(panel,original)


def test_matches_existing_intercept_objective_and_loss_units():
    panel=np.random.default_rng(90).integers(0,2,(60,12,8))
    counts,n,test,x,_=split_panel(panel,np.zeros((12,8)),'B',3)
    a=predict_fold(panel,3)[:,0]
    model=Model('F',x,60,4)
    value,gradient=model.objective(a,counts,n)
    assert np.max(np.abs(gradient))<1e-11
    expected=np.sum(88*np.logaddexp(0,a)-counts.sum(1)*a+.005*a*a)
    assert value==pytest.approx(expected,abs=1e-10)
    for key,val in evaluate_fold(a[:,None],test).items():
        np.testing.assert_allclose(val,losses(a[:,None],test)[key],atol=1e-14)
    balanced=evaluate_fold(np.zeros((60,1)),test)
    assert balanced['log_loss']==pytest.approx(np.log(2))
    assert balanced['brier']==pytest.approx(.25)


def test_family_first_aggregation_and_36_calculations():
    panels=np.random.default_rng(5).integers(0,2,(3,60,12,8))
    calls=0
    for panel in panels:
        family=[]; direct=[]
        for held in range(12):
            a=predict_fold(panel,held); calls+=1
            y=panel[:,held:held+1,:]
            family.append(evaluate_fold(a,y)['family_log_loss'])
            p=1/(1+np.exp(-a))
            direct.append(-(y*np.log(p[:,:,None])+(1-y)*np.log1p(-p[:,:,None])))
        np.testing.assert_allclose(np.mean(family,axis=0),np.concatenate(direct,axis=1).mean((1,2)))
    assert calls==36


@pytest.mark.parametrize('held',[-1,12,True,1.5])
def test_reject_bad_held(held):
    with pytest.raises(ValueError): training_indices(held)


@pytest.mark.parametrize('counts',[-1,89,.5,np.nan,np.inf])
def test_reject_bad_counts(counts):
    with pytest.raises(ValueError): fit_counts(counts)


def test_training_validation():
    with pytest.raises(ValueError): predict_fold(np.zeros((60,12,7)),0)
    panel=np.zeros((60,12,8)); panel[0,1,0]=np.nan
    with pytest.raises(ValueError): predict_fold(panel,0)
