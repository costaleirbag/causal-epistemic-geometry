"""Private in-place adapter and append-only executor; exports aggregates only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import time
import numpy as np
from finite_models import Model, fit, losses, split_panel
from revised_feasibility import fit_plan, schedule_gate

SPACES = ['ORIGINAL','RANDOM_1','RANDOM_2']

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()


def write_new(path,obj):
    with Path(path).open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())


def load_panel(rows, ids, keep, schedule):
    expected={(r['item_id'],r['condition'],r['rollout_index']) for r in schedule}
    actual=[(r['item_id'],r['condition'],r['rollout_index']) for r in rows]
    if len(actual)!=len(set(actual)) or set(actual)!=expected: raise ValueError('score coverage')
    y=np.full((3,60,12,8),np.nan)
    for row in rows:
        if any(type(row[k]) is not bool for k in ['correct','valid','evaluable']): raise ValueError('score boolean')
        if row['correct'] and not(row['valid'] and row['evaluable']): raise ValueError('correctness convention')
        if row['condition']=='BASELINE': continue
        space,k=row['condition'].rsplit('_',1)
        y[SPACES.index(space),ids.index(row['item_id']),keep.index(int(k)),row['rollout_index']]=row['correct']
    if not np.isfinite(y).all(): raise ValueError('incomplete tensor')
    return y


def paired(a,b):
    out={}
    for metric in ['log_loss','brier']:
        d=np.array(a['family_'+metric])-np.array(b['family_'+metric])
        out[metric]={'mean':float(d.mean()),'median':float(np.median(d)),
                     'minimum':float(d.min()),'maximum':float(d.max()),'fraction_positive':float((d>0).mean())}
        out['controller_'+metric+'_gains']=(np.array(a['controller_'+metric])-np.array(b['controller_'+metric])).tolist()
    return out


def aggregate(records):
    # A separate half; B concatenate held controllers before family aggregation.
    groups={}
    for rec in records:
        key=tuple(rec['key'])
        stage,orientation,split=key[:3]
        if stage=='A': _,_,_,model,penalty=key; group=(stage,orientation,split,model,penalty)
        else: _,_,_,assignment,model,penalty=key; group=(stage,orientation,assignment,model,penalty)
        groups.setdefault(group,[]).append(rec['losses'])
    averaged={}
    for key,rows in groups.items():
        avg={k:np.mean([r[k] for r in rows],axis=0).tolist() for k in ['log_loss','brier','family_log_loss','family_brier']}
        for metric in ['log_loss','brier']:
            avg['controller_'+metric]=(sum([r['controller_'+metric] for r in rows],[]) if key[0]=='B' else rows[0]['controller_'+metric])
        avg['clipped_cells']=sum(r['clipped_cells'] for r in rows)
        avg['folds_completed']=len(rows)
        averaged[key]=avg
    comparisons=[]
    for key,b in averaged.items():
        stage,o,s,model,penalty=key
        base={'R':'F','D':'R','I':'D','C':'D','H':'G'}.get(model)
        if base:
            bk=(stage,o,s,base,1 if base=='F' else penalty)
            if bk in averaged:
                comparisons.append({'key':list(key),'baseline':base,'positive_favors':model,'paired':paired(averaged[bk],b)})
    controls=[]
    for o in range(3):
        for assignment in range(1,4):
            for model in ['G','H']:
                actual=('B',o,0,model,1); control=('B',o,assignment,model,1)
                if actual in averaged and control in averaged:
                    controls.append({'orientation':o,'assignment':assignment,'model':model,'positive_favors':'actual','paired':paired(averaged[control],averaged[actual])})
    public=[dict(key=list(k),**{n:v for n,v in row.items() if not n.startswith('family_')}) for k,row in averaged.items()]
    return public,comparisons,controls


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('output'); ap.add_argument('precheck'); args=ap.parse_args()
    root=Path(args.input); output=Path(args.output); prepath=Path(args.precheck)
    pre=json.loads(prepath.read_text())
    assert pre['status']=='EXECUTABLE' and pre['ready_for_real_fitting']
    for name,digest in pre['code_hashes'].items(): assert sha(prepath.parent/name)==digest, name
    for name,digest in pre['input_hashes'].items(): assert sha(root/name)==digest, name
    read=lambda name:json.loads((root/name).read_text())
    schedule=read('EVALUATION_SCHEDULE.json'); schedule_gate(schedule)
    prepared=read('PREPARED.json'); keep=read('QUALIFICATION.json')['common_safe_indices']
    seal=read('EVALUATION_SEAL.json'); selection=read('SELECTION_SEAL.json')
    assert seal['journal_sha256']==pre['input_hashes']['evaluation.jsonl']
    assert seal['protocol_sha256']==pre['original_precheck_sha256']
    assert seal['schedule_sha256']==selection['schedule_sha256']==pre['input_hashes']['EVALUATION_SCHEDULE.json']
    assert seal['deployment_sha256']==selection['deployment_sha256']==pre['input_hashes']['DEPLOYMENT.json']
    assert prepared['vectors_sha256']==pre['input_hashes']['vectors.npz']
    assert selection['qualification_sha256']==pre['input_hashes']['QUALIFICATION.json']
    with np.load(root/'vectors.npz',allow_pickle=False) as archive: x=archive['coefficients'][keep]
    assert x.shape==(12,8) and np.isfinite(x).all()
    assert np.allclose(np.linalg.norm(x,axis=1),1,atol=1e-10)
    ranks=[]
    for perm in [list(range(12))]+pre['permutations']:
        for held in range(12):
            train=np.delete(x[perm],held,axis=0); train-=train.mean(0)
            singular=np.linalg.svd(train,compute_uv=False)
            assert np.linalg.matrix_rank(train)==8
            ranks.append({'assignment':len(ranks)//12,'held':held,'rank':8,'singular_values':singular.tolist(),'condition_number':float(singular[0]/singular[-1])})
    output.mkdir(exist_ok=True)
    identity=output/'IDENTITY.json'
    if identity.exists(): assert json.loads(identity.read_text())['precheck_sha256']==sha(prepath)
    else: write_new(identity,{'precheck_sha256':sha(prepath)})
    if (output/'MODEL_COMPARISON_RESULTS.json').exists():
        result=json.loads((output/'MODEL_COMPARISON_RESULTS.json').read_text())
        assert result['precheck_sha256']==sha(prepath)
        print(json.dumps({'status':result['status'],'idempotent_existing_result':True})); return
    lock=output/'ACTIVE.lock'
    # An existing lock is an explicit stop, never automatically stolen.
    with lock.open('x') as f: f.write(str(os.getpid()))
    try:
        journal=output/'attempts.jsonl'
        entries=[json.loads(s) for s in journal.read_text().splitlines()] if journal.exists() else []
        attempted={r['attempt'] for r in entries if r['event']=='begin'}
        completed={r['attempt'] for r in entries if r['event']=='end'}
        if attempted!=completed: raise RuntimeError('interrupted attempt requires disposition; no retry')
        cpu_prior=sum(r['cpu_seconds'] for r in entries if r['event']=='end')
        wall_prior=sum(r['wall_seconds'] for r in entries if r['event']=='end')
        start_cpu=time.process_time(); start_wall=time.monotonic()
        resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        resource.setrlimit(resource.RLIMIT_CPU,(int(7200-cpu_prior),int(7200-cpu_prior)+1))
        def gate():
            if cpu_prior+time.process_time()-start_cpu>=7200 or wall_prior+time.monotonic()-start_wall>=7200: raise RuntimeError('resource ceiling')
        def log(obj):
            with journal.open('a') as f: f.write(json.dumps(obj,allow_nan=False)+'\n'); f.flush(); os.fsync(f.fileno())
        y=load_panel(read('PRIVATE_SCORES.json'),prepared['evaluation_items'],keep,schedule)
        plan=fit_plan(False); assert len(plan)==780
        checkpoints=[]; records=[]; reason=None
        for attempt,spec in enumerate(plan):
            gate()
            stage,o,split=spec[:3]
            if stage=='A': _,_,_,name,penalty,start=spec; assignment=0
            else: _,_,_,assignment,name,penalty,start=spec
            permutation=list(range(12)) if assignment==0 else pre['permutations'][assignment-1]
            successes,n,test,xx,xt=split_panel(y[o],x[permutation],stage,split)
            m=Model(name,xx,60,penalty)
            checkpoint=output/('fit_%04d.json'%attempt)
            if attempt in completed: rec=json.loads(checkpoint.read_text())
            else:
                assert len(attempted)<1000; log({'event':'begin','attempt':attempt,'spec':spec}); attempted.add(attempt)
                ac,aw=time.process_time(),time.monotonic()
                try: result=fit(m,successes,n,start,gate)
                except RuntimeError as exc:
                    reason=str(exc); break
                rec={'attempt':attempt,'spec':spec,'fit':result}
                write_new(checkpoint,rec)
                log({'event':'end','attempt':attempt,'cpu_seconds':time.process_time()-ac,'wall_seconds':time.monotonic()-aw})
            checkpoints.append(rec)
            if rec['fit']['status']!='converged': reason='numerical_convergence_failure'; break
            # A completed fit group includes both predetermined starts.
            if attempt+1<len(plan) and plan[attempt+1][:-1]==spec[:-1]: continue
            group=[r for r in checkpoints if r['spec'][:-1]==list(spec[:-1]) or tuple(r['spec'][:-1])==spec[:-1]]
            best=min(group,key=lambda r:(r['fit']['objective'],r['spec'][-1]))
            parameters=np.array(best['fit']['parameters'])
            eta=m.logits(parameters,xt if stage=='B' else None)
            records.append({'key':list(spec[:-1]),'selected_start':best['spec'][-1],'losses':losses(eta,test)})
        public,comparisons,controls=aggregate(records)
        # Preserve detailed per-family values and coefficients only in private checkpoints.
        write_new(output/'PRIVATE_METRICS.json',records)
        unchanged=all(sha(root/name)==digest for name,digest in pre['input_hashes'].items())
        result={'status':'complete' if len(checkpoints)==780 and reason is None and unchanged else 'incomplete',
                'reason':reason,'precheck_sha256':sha(prepath),'historical_inputs_unchanged':unchanged,
                'attempts_started':len(attempted),'attempts_completed':len(checkpoints),'expected_attempts':780,
                'cpu_seconds':cpu_prior+time.process_time()-start_cpu,'wall_seconds':wall_prior+time.monotonic()-start_wall,
                'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                'losses':public,'paired_comparisons':comparisons,'assignment_controls':controls,
                'coordinate_diagnostics':ranks,
                'convergence':[{'attempt':r['attempt'],'spec':r['spec'],**{k:v for k,v in r['fit'].items() if k!='parameters'}} for r in checkpoints],
                'limitations':['Retrospective exposed pilot; internal separation only.','Nonconvex stationary points, not global optimum claims.','Finite selected controllers and two random orientations.','No A0 identification, semantic axes, Jacobian, new-family or deployment claim.','No significance tests; .005 nats is exploratory.','Independent audit pending.']}
        write_new(output/'MODEL_COMPARISON_RESULTS.json',result)
        print(json.dumps({'status':result['status'],'attempts':result['attempts_completed'],'reason':reason}))
    finally: lock.unlink()

if __name__=='__main__': main()
