import numpy as np
import pytest
from finite_models import Model, contrasts, fit, losses, sigmoid, split_panel

@pytest.mark.parametrize('name', ['F','R','D','I','C','G','H'])
def test_gradient_and_constraints(name):
    rng = np.random.default_rng(51)
    x = rng.normal(size=(6,3)); x -= x.mean(0)
    m = Model(name,x,7,1.)
    t = m.initial(0)+rng.normal(size=m.size)*.13
    y = rng.binomial(4,.4,size=(7,6)); n = np.full(y.shape,4.)
    value,g = m.objective(t,y,n)
    numerical = []
    for j in range(m.size):
        e = np.eye(1,m.size,j)[0]*1e-5
        numerical.append((m.objective(t+e,y,n)[0]-m.objective(t-e,y,n)[0])/2e-5)
    np.testing.assert_allclose(g,numerical,atol=2e-8,rtol=2e-6)
    z=m.unpack(t)
    for key in ['u','h']:
        if key in z: assert abs((m.fi @ z[key]).sum()) < 1e-12
    if 'b' in z: assert abs((m.ki @ z['b']).sum()) < 1e-12
    if name=='D':
        eta=m.logits(t); b=m.ki @ z['b']
        assert np.all(np.diff(eta[:,np.argsort(b)],axis=1)>=0)
    if 'q' in z:
        tt=t.copy(); tt[m.slices['q']]*=7
        np.testing.assert_allclose(m.logits(t),m.logits(tt),atol=1e-12)


def test_splits_no_leakage():
    rng=np.random.default_rng(5)
    y=rng.binomial(1,.5,(60,12,8)); x=rng.normal(size=(12,8))
    for stage, indices in [('A',range(2)),('B',range(12))]:
        for index in indices:
            a,n,test,xx,xt=split_panel(y,x,stage,index)
            changed=y.copy()
            if stage=='A': changed[:,:,4*(1-index):4*(1-index)+4]=1-changed[:,:,4*(1-index):4*(1-index)+4]
            else: changed[:,index]=1-changed[:,index]
            aa,nn,_,xxx,xtt=split_panel(changed,x,stage,index)
            np.testing.assert_array_equal(a,aa)
            np.testing.assert_array_equal(xx,xxx)
            np.testing.assert_allclose(xx.mean(0),0,atol=1e-15)
            if stage=='B': np.testing.assert_allclose(xt,x[index:index+1]-np.delete(x,index,0).mean(0))
            assert n.sum()+test.size==y.size


def test_rotation_objective_and_gradient():
    rng=np.random.default_rng(24)
    x=rng.normal(size=(12,8)); x-=x.mean(0)
    rot=np.linalg.qr(rng.normal(size=(8,8)))[0]
    for name in ['C','G','H']:
        m=Model(name,x,9,1); mr=Model(name,x@rot,9,1)
        t=m.initial(0); t+=rng.normal(size=m.size)*.1; tr=t.copy()
        for key in ['beta','q']:
            if key in m.slices: tr[m.slices[key]]=rot.T@t[m.slices[key]]
        y=rng.binomial(4,.5,(9,12))
        v,g=m.objective(t,y,4); vr,gr=mr.objective(tr,y,4)
        assert abs(v-vr)<1e-10
        for key in ['beta','q']:
            if key in m.slices: gr[m.slices[key]]=rot@gr[m.slices[key]]
        np.testing.assert_allclose(g,gr,atol=1e-10)


def test_aggregation():
    y=np.arange(24).reshape(3,2,4)%2
    eta=np.array([[1.,2.],[3.,4.],[5.,6.]])
    out=losses(eta,y)
    manual=[]
    for i in range(3):
        terms=[]
        for k in range(2):
            for r in range(4): terms.append(np.logaddexp(0,eta[i,k])-y[i,k,r]*eta[i,k])
        manual.append(np.mean(terms))
    np.testing.assert_allclose(out['family_log_loss'],manual)
    assert abs(out['log_loss']-np.mean(manual))<1e-12

@pytest.mark.parametrize('signal', ['monotonic','rank_one'])
def test_signal_recovery(signal):
    rng=np.random.default_rng(414)
    x=rng.normal(size=(12,3)); x-=x.mean(0)
    f=16
    a=rng.normal(size=f)*.6
    b=np.linspace(-1.5,1.5,12)
    h=np.linspace(-.9,.9,f)
    if signal=='monotonic': eta=a[:,None]+np.exp(h[:,None])*b
    else: eta=a[:,None]+np.linspace(-2,2,f)[:,None]*(x@np.array([1.,0.,0.]))
    # Exact expected counts isolate optimizer/model behavior from Bernoulli noise.
    y=200*sigmoid(eta); n=np.full(y.shape,200.)
    names=['R','D'] if signal=='monotonic' else ['G','H']
    results=[]
    for name in names:
        m=Model(name,x,f,1.)
        runs=[fit(m,y,n,s) for s in range(1 if name in ['R','G'] else 2)]
        assert all(r['status']=='converged' for r in runs), runs
        best=min(runs,key=lambda r:r['objective'])
        results.append(best['objective']/n.sum())
        if name=='D':
            e=m.logits(np.array(best['parameters']))
            assert np.all(np.diff(e[:,np.argsort(e[0])],axis=1)>=0)
    assert results[0]-results[1]>.005

@pytest.mark.parametrize('name',['F','R','D','I','C','G','H'])
def test_finite_fit_deterministic(name):
    rng=np.random.default_rng(301)
    x=rng.normal(size=(12,8)); x-=x.mean(0)
    y=rng.binomial(4,.5,(60,12)); n=np.full(y.shape,4.)
    m=Model(name,x,60,1.)
    r=fit(m,y,n); rr=fit(m,y,n)
    assert r['status']=='converged', r
    assert r['parameters']==rr['parameters']


def test_adapter_and_aggregate_private_boundaries():
    from run_finite_comparison import load_panel, aggregate, write_new
    ids=list(range(60)); keep=list(range(12))
    conditions=['BASELINE']+[f'{s}_{k:02}' for s in ['ORIGINAL','RANDOM_1','RANDOM_2'] for k in keep]
    rows=[dict(item_id=i,condition=c,rollout_index=r,correct=bool((i+r)%2),valid=True,evaluable=True) for i in ids for c in conditions for r in range(8)]
    panel=load_panel(rows,ids,keep,rows)
    assert panel.shape==(3,60,12,8)
    with pytest.raises(ValueError,match='coverage'): load_panel(rows[:-1],ids,keep,rows)
    bad=[dict(r) for r in rows]; bad[0]['correct']=1
    with pytest.raises(ValueError,match='boolean'): load_panel(bad,ids,keep,rows)
    records=[]
    for k in range(12):
        for m in ['G','H']:
            records.append(dict(key=['B',0,k,0,m,1],losses=losses(np.full((60,1), .2 if m=='H' else 0),panel[0,:,k:k+1])))
    public,comparisons,controls=aggregate(records)
    assert len(public)==2 and len(comparisons)==1
    assert all('family_log_loss' not in r for r in public)
    assert all(r['folds_completed']==12 for r in public)
    assert len(comparisons[0]['paired']['controller_log_loss_gains'])==12


def test_checkpoint_exclusive_and_digest(tmp_path):
    from run_finite_comparison import write_new,sha
    p=tmp_path/'checkpoint.json'; write_new(p,{'done':True})
    before=sha(p)
    with pytest.raises(FileExistsError): write_new(p,{'done':False})
    assert sha(p)==before

@pytest.mark.parametrize('penalty',[.25,4])
@pytest.mark.parametrize('name',['D','I','C','H'])
def test_full_size_sensitivity_convergence(name,penalty):
    rng=np.random.default_rng(301)
    x=rng.normal(size=(12,8)); x/=np.linalg.norm(x,axis=1)[:,None]; x-=x.mean(0)
    y=rng.binomial(4,.5,(60,12)); n=np.full(y.shape,4.)
    m=Model(name,x,60,penalty)
    for start in range(2):
        r=fit(m,y,n,start)
        assert r['status']=='converged',r
