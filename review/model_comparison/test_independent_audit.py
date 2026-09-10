import numpy as np
import pytest
from independent_audit import arithmetic,decode,metrics,compare,split,validate_mask

@pytest.mark.parametrize('name',['F','R','D','I','C','G','H'])
def test_separate_derivative(name):
    rng=np.random.default_rng(92); x=rng.normal(size=(5,3)); x-=x.mean(0)
    sizes={'F':4,'R':8,'D':11,'I':15,'C':14,'G':7,'H':13}
    t=rng.normal(size=sizes[name])*.2; y=rng.binomial(4,.5,(4,5))
    for j in range(len(t)):
        tc=t.astype(complex); tc[j]+=1e-20j
        e=np.zeros(len(t)); e[j]=1e-5
        g=arithmetic(tc,name,x,4,1,y,4).imag/1e-20
        finite=(arithmetic(t+e,name,x,4,1,y,4)-arithmetic(t-e,name,x,4,1,y,4))/2e-5
        assert abs(g-finite)<1e-7
    if name in ('I','C','H'):
        q=decode(t,name,4,5,3)['q']; tt=t.copy(); tt[-len(q):]*=9
        compare(arithmetic(t,name,x,4,1),arithmetic(tt,name,x,4,1))

def test_normalization_failure():
    y=np.zeros((4,5,8)); m=metrics(np.zeros((4,5)),y)
    compare(m['log_loss'],np.log(2))
    with pytest.raises(ValueError): compare(m['log_loss']/8,np.log(2))

def test_mask_and_leakage_failures():
    y=np.zeros((4,5,8)); x=np.arange(15).reshape(5,3)
    for stage,i in [('A',0),('A',1),('B',2)]:
        a,n,t,xx,xt=split(y,x,stage,i)
        changed=y.copy()
        if stage=='B': changed[:,i]=1
        else: changed[:,:,4*(1-i):4*(1-i)+4]=1
        aa,_,_,xxx,_=split(changed,x,stage,i)
        compare(a,aa); compare(xx,xxx)
        with pytest.raises(ValueError): validate_mask(np.ones(y.shape,dtype=bool),stage,i)
    with pytest.raises(ValueError): compare(xt,x[2:3]-x.mean(0)+1)
