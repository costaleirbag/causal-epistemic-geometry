"""Read-only checkpoint audit. No primary modules imported; no fitting or scoring."""
import argparse, hashlib, json, time, resource
from pathlib import Path
import numpy as np

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()

def basis(n):
    a=np.zeros((n,n-1))
    for col in range(n-1):
        a[:col+1,col]=1
        a[col+1,col]=-col-1
        a[:,col]/=np.sqrt((col+1)*(col+2))
    return a

def decode(t,name,f,k,d):
    sizes=[('a',f)]
    if name in ('R','D','I','C'): sizes.append(('b',k-1))
    if name=='D': sizes.append(('h',f-1))
    if name in ('G','H'): sizes.append(('beta',d))
    if name in ('I','C','H'): sizes.extend([('u',f-1),('q',k-1 if name=='I' else d)])
    z={}; offset=0
    for key,n in sizes: z[key]=t[offset:offset+n]; offset+=n
    assert offset==len(t)
    return z

def arithmetic(t,name,x,f,lam,y=None,n=None,xt=None):
    z=decode(t,name,f,len(x),x.shape[1]); xx=x if xt is None else xt
    eta=np.tile(z['a'][:,None],(1,len(xx)))
    if 'b' in z:
        b=basis(len(x))@z['b']; scale=np.exp(basis(f)@z['h']) if 'h' in z else np.ones(f)
        eta=eta+np.outer(scale,b)
    if 'beta' in z: eta=eta+(xx@z['beta'])[None,:]
    if 'q' in z:
        # Analytic extension of Euclidean normalization allows complex-step derivatives.
        radius=np.sqrt(np.sum(z['q']**2)); assert abs(radius)>0
        right=z['q']/radius
        v=basis(len(x))@right if name=='I' else xx@right
        eta=eta+np.outer(basis(f)@z['u'],v)
    if y is None: return eta
    # Stable complex-compatible softplus, branch determined by real component.
    soft=np.where(eta.real>0,eta,0)+np.log1p(np.exp(-np.where(eta.real>0,eta,-eta)))
    value=np.sum(n*soft-y*eta)
    for key,a in z.items(): value+=.5*(.01 if key=='a' else 0 if key=='q' else lam)*np.sum(a*a)
    return value

def split(y,x,stage,index):
    mask=np.zeros(y.shape,dtype=bool)
    if stage=='A': mask[:,:,index*4:index*4+4]=True
    else: mask[:]=True; mask[:,index,:]=False
    validate_mask(mask,stage,index)
    if stage=='A':
        xx=x-x.mean(0); return y[mask].reshape(len(y),len(x),4).sum(2),np.full(y.shape[:2],4),y[~mask].reshape(len(y),len(x),4),xx,xx
    ids=np.flatnonzero(np.arange(len(x))!=index); center=x[ids].mean(0)
    return y[:,ids].sum(2),np.full((len(y),len(ids)),8),y[:,index:index+1],x[ids]-center,x[index:index+1]-center

def validate_mask(mask,stage,index):
    expected=np.zeros(mask.shape,dtype=bool)
    if stage=='A': expected[:,:,index*4:index*4+4]=True
    else: expected[:]=True; expected[:,index]=False
    if mask.dtype!=bool or not np.array_equal(mask,expected): raise ValueError('leakage or malformed mask')

def metrics(eta,y):
    p=np.clip(1/(1+np.exp(-eta)),1e-6,1-1e-6)
    ll=np.empty(y.shape); br=np.empty(y.shape)
    for r in range(y.shape[2]):
        ll[:,:,r]=-np.where(y[:,:,r]==1,np.log(p),np.log1p(-p))
        br[:,:,r]=(y[:,:,r]-p)**2
    return {**{k:float(v.mean()) for k,v in [('log_loss',ll),('brier',br)]},**{'family_'+k:v.mean(axis=(1,2)).tolist() for k,v in [('log_loss',ll),('brier',br)]},**{'controller_'+k:v.mean(axis=(0,2)).tolist() for k,v in [('log_loss',ll),('brier',br)]}}

def compare(a,b,tol=1e-10):
    delta=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    if delta>tol: raise ValueError('numerical discrepancy '+str(delta))
    return delta

def run(root,out,code):
    started=time.monotonic(); cpu=time.process_time(); resource.setrlimit(resource.RLIMIT_CPU,(1800,1801))
    read=lambda p:json.loads(p.read_text())
    pre=read(code/'MODEL_COMPARISON_PRECHECK.json'); result=read(out/'MODEL_COMPARISON_RESULTS.json')
    hashes={n:sha(root/n) for n in pre['input_hashes']}; assert hashes==pre['input_hashes']
    assert all(sha(code/n)==h for n,h in pre['code_hashes'].items())
    assert sha(code/'MODEL_COMPARISON_PRECHECK.json')==result['precheck_sha256']
    rng=np.random.Generator(np.random.PCG64(20260911)); assert [rng.permutation(12).tolist() for _ in range(3)]==pre['permutations']
    prepared=read(root/'PREPARED.json'); keep=read(root/'QUALIFICATION.json')['common_safe_indices']; ids=prepared['evaluation_items']
    schedule=read(root/'EVALUATION_SCHEDULE.json'); rows=read(root/'PRIVATE_SCORES.json')
    key=lambda r:(r['item_id'],r['condition'],r['rollout_index'])
    keys={key(r) for r in schedule}; assert len(keys)==len(schedule)==17760 and len({r['seed'] for r in schedule})==17760
    assert {key(r) for r in rows}==keys and len(rows)==17760
    conditions={r['condition'] for r in schedule}; assert keys=={(f,c,r) for f in ids for c in conditions for r in range(8)}
    y=np.full((3,60,12,8),np.nan); spaces=['ORIGINAL','RANDOM_1','RANDOM_2']
    for r in rows:
        assert all(type(r[k]) is bool for k in ('correct','valid','evaluable'))
        assert not r['correct'] or (r['valid'] and r['evaluable'])
        if r['condition']=='BASELINE': continue
        s,k=r['condition'].rsplit('_',1); y[spaces.index(s),ids.index(r['item_id']),keep.index(int(k)),r['rollout_index']]=r['correct']
    assert np.isfinite(y).all()
    with np.load(root/'vectors.npz') as a: x=a['coefficients'][keep]
    journal=[json.loads(s) for s in (out/'attempts.jsonl').read_text().splitlines()]; assert len(journal)==1560
    plan=[]
    for o in range(3):
        for half in range(2):
            for m,ns in [('F',1),('R',1),('D',2),('I',2),('C',2)]:
                for l in ([1] if m=='F' else [1,.25,4]):
                    for s in range(ns): plan.append(['A',o,half,m,l,s])
        for h in range(12):
            for a in range(4):
                for l in ([1] if a else [1,.25,4]):
                    for m,ns in [('G',1),('H',2)]:
                        for s in range(ns): plan.append(['B',o,h,a,m,l,s])
    fits=[read(out/('fit_%04d.json'%i)) for i in range(780)]
    pinned={p.name:sha(p) for p in out.glob('fit_*.json')}; pinned['attempts.jsonl']=sha(out/'attempts.jsonl')
    assert len(pinned)==781
    maxgrad=0.; maxobj=0.; groups={}
    for i,(rec,spec) in enumerate(zip(fits,plan)):
        assert time.monotonic()-started<1800
        assert rec['spec']==spec and rec['attempt']==i
        assert journal[2*i]['event']=='begin' and journal[2*i]['attempt']==i and journal[2*i]['spec']==spec
        assert journal[2*i+1]['event']=='end' and journal[2*i+1]['attempt']==i
        stage,o,index=spec[:3]; m,l=spec[-3:-1]; assignment=0 if stage=='A' else spec[3]
        perm=list(range(12)) if assignment==0 else pre['permutations'][assignment-1]
        yy,nn,test,xx,xt=split(y[o],x[perm],stage,index)
        t=np.array(rec['fit']['parameters']); val=arithmetic(t,m,xx,60,l,yy,nn)
        maxobj=max(maxobj,compare(val,rec['fit']['objective'],1e-8))
        grad=[]
        for j in range(len(t)):
            tc=t.astype(complex); tc[j]+=1e-20j
            grad.append(arithmetic(tc,m,xx,60,l,yy,nn).imag/1e-20)
        grad=np.array(grad); z=decode(t,m,60,len(xx),8)
        if 'q' in z: grad[-len(z['q']):]*=max(1,np.linalg.norm(z['q']))
        norm=float(np.max(abs(grad))/nn.sum()); maxgrad=max(maxgrad,norm)
        assert norm<=1e-9 and rec['fit']['status']=='converged'
        groups.setdefault(tuple(spec[:-1]),[]).append((val,rec,test,xx,xt))
    private=read(out/'PRIVATE_METRICS.json'); lookup={tuple(r['key']):r for r in private}; summaries={}; maxloss=0.; differences=[]; reorderings=[]
    for key,g in groups.items():
        if len(g)==2: differences.append(abs(g[0][0]-g[1][0]))
        recomputed_best=min(g,key=lambda a:(a[0],a[1]['spec'][-1]))
        best=min(g,key=lambda a:(a[1]['fit']['objective'],a[1]['spec'][-1])); val,rec,test,xx,xt=best
        if recomputed_best[1]['spec'][-1]!=rec['spec'][-1]: reorderings.append(float(abs(recomputed_best[0]-val)))
        assert lookup[key]['selected_start']==rec['spec'][-1]
        metric=metrics(arithmetic(np.array(rec['fit']['parameters']),key[-2],xx,60,key[-1],xt=xt),test)
        for k,v in metric.items(): maxloss=max(maxloss,compare(v,lookup[key]['losses'][k]))
        group=key if key[0]=='A' else (key[0],key[1],key[3],key[4],key[5])
        summaries.setdefault(group,[]).append(metric)
    avg={}
    for key,ms in summaries.items():
        avg[key]={k:(sum([r[k] for r in ms],[]) if k.startswith('controller_') and key[0]=='B' else np.mean([r[k] for r in ms],axis=0)) for k in ms[0]}
    for row in result['losses']:
        for k in ('log_loss','brier','controller_log_loss','controller_brier'): maxloss=max(maxloss,compare(avg[tuple(row['key'])][k],row[k]))
    def paired(a,b,reported):
        nonlocal maxloss
        for metric in ('log_loss','brier'):
            d=np.array(a['family_'+metric])-np.array(b['family_'+metric])
            stats=dict(mean=d.mean(),median=np.median(d),minimum=d.min(),maximum=d.max(),fraction_positive=np.mean(d>0))
            for k,v in stats.items(): maxloss=max(maxloss,compare(v,reported[metric][k]))
            maxloss=max(maxloss,compare(np.array(a['controller_'+metric])-b['controller_'+metric],reported['controller_'+metric+'_gains']))
    for row in result['paired_comparisons']:
        key=tuple(row['key']); base=key[:-2]+(row['baseline'],1 if row['baseline']=='F' else key[-1]); paired(avg[base],avg[key],row['paired'])
    for row in result['assignment_controls']:
        paired(avg[('B',row['orientation'],row['assignment'],row['model'],1)],avg[('B',row['orientation'],0,row['model'],1)],row['paired'])
    assert all(sha(out/n)==h for n,h in pinned.items()) and all(sha(root/n)==h for n,h in hashes.items())
    gains=lambda o,a,l:float(avg[('B',o,a,'G',l)]['log_loss']-avg[('B',o,a,'H',l)]['log_loss'])
    return dict(passed=True,counts=dict(attempts=780,fit_groups=len(groups),loss_rows=len(avg),paired=90,controls=18,journal=1560,nonconvex_groups=len(differences),distinct_local_objectives=int(sum(d>1e-6 for d in differences))),differences=dict(max_objective=maxobj,max_loss_or_summary=maxloss,max_intrinsic_gradient_per_trial=maxgrad,max_start_objective_difference=max(differences),floating_point_start_reorderings=reorderings),input_hashes=hashes,private_checkpoint_manifest_sha256=hashlib.sha256(json.dumps(pinned,sort_keys=True).encode()).hexdigest(),homogeneous_family_counts=[int(np.sum(np.ptp(a,axis=(1,2))==0)) for a in y],original_stage_B_gains={str(l):gains(0,0,l) for l in [1,.25,4]},incremental_actual_minus_permuted=[[gains(o,0,1)-gains(o,a,1) for a in [1,2,3]] for o in range(3)],orientation_gain_contrasts={str(l):[gains(0,0,l)-gains(o,0,l) for o in [1,2]] for l in [1,.25,4]},audit_cpu_seconds=time.process_time()-cpu,audit_wall_seconds=time.monotonic()-started)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('input',type=Path); p.add_argument('fits',type=Path); p.add_argument('code',type=Path); a=p.parse_args()
    print(json.dumps(run(a.input,a.fits,a.code),indent=2))
