import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
import argparse

p = argparse.ArgumentParser()
p.add_argument("--dataset", required=True)
p.add_argument("--unsteered-scores", required=True)
p.add_argument("--historical-scores", required=True)
args = p.parse_args()

def read(path, expected):
    raw=Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==expected
    return [json.loads(x) for x in raw.splitlines()]

def canonical(v):
    if type(v) in (int,bool,str): return [type(v).__name__,v]
    if type(v) in (list,tuple): return [type(v).__name__,[canonical(x) for x in v]]
    if type(v) is dict:
        entries=[[canonical(k),canonical(x)] for k,x in v.items()]
        entries.sort(key=lambda x:json.dumps(x[0],sort_keys=True))
        return ['dict',entries]
    raise ValueError('unexpected reference type')

def parts(v, typ):
    if not v or v[0]!=typ: return None,{}
    if typ=='tuple':
        return len(v[1]),dict(zip(['acc_mod997','text_length','sum_xs_mod997'],v[1],strict=False)) if len(v[1])==3 else {}
    if typ=='list':
        return len(v[1]), {('acc_mod101' if i==0 else f'xs_{i-1}_mod101'):x for i,x in enumerate(v[1])}
    if typ=='dict':
        pairs=v[1]
        if any(k[0]!='str' for k,x in pairs): return None,{}
        result={k[1]:x for k,x in pairs}
        return sorted(result),result
    if typ=='str':
        if ':' not in v[1]: return None,{}
        prefix,suffix=v[1].rsplit(':',1)
        return 'colon',{'text_segment':['str',prefix],'acc_suffix':['str',suffix]}
    raise ValueError(typ)

dataset=read(args.dataset,'c791e38c29d36a43fbac8ce00412e4c77d533665e0b8cb9eef8fa12fb918ac1d')
refs={r['family_id']:canonical(ast.literal_eval(r['reference_repr'])) for r in dataset}
un=read(args.unsteered_scores,'30dd57131b3f0823df1642e2dabb0d511e10c8fe8acf49e0e98c53100df7b0b0')
ch=[r for r in read(args.historical_scores,'c3b4ab47cf2422afb311fa978496e2abfbe5485ac76040ee3dcead2986ace533') if r['condition']=='V4_DIRECTION_02_MEDIUM']
assert len(un)==len(ch)==600
result={}
for condition,rows in [('unsteered',un),('champion',ch)]:
    result[condition]={}
    for typ in ('tuple','dict','list','str'):
        subset=[r for r in rows if refs[r['family_id']][0]==typ]
        numer=Counter();denom=Counter();rollouts={};family_bits={}
        structural=full=0
        for row in subset:
            expected=refs[row['family_id']]
            actual=json.loads(row['canonical_value']) if row['canonical_value'] is not None else None
            es,ep=parts(expected,typ);s,p=parts(actual,typ)
            structural+=s==es
            full+=actual==expected
            family_bits.setdefault(row['family_id'],{})[row['rollout_index']]={}
            for k,x in ep.items():
                passed=s==es and p.get(k)==x
                denom[k]+=1;numer[k]+=passed
                family_bits[row['family_id']][row['rollout_index']][k]=passed
                rc=rollouts.setdefault(str(row['rollout_index']),{}).setdefault(k,{'correct':0,'denominator':0})
                rc['correct']+=passed;rc['denominator']+=1
        both={k:{'both_rollouts_correct':sum(all(bits[r].get(k,False) for r in (0,1)) for bits in family_bits.values() if k in bits[0]),'families':sum(k in bits[0] for bits in family_bits.values())} for k in denom}
        result[condition][typ]={'rows':len(subset),'structure_correct':structural,'full_exact':full,'components':{k:{'correct':numer[k],'denominator':denom[k]} for k in denom},'by_rollout':rollouts,'both_rollouts':both}
metadata={r['family_id']:r for r in dataset}
copy_result={}
for condition,rows in [('unsteered',un),('champion',ch)]:
    groups={}
    for row in rows:
        f=row['family_id']; expected=refs[f]; typ=expected[0]
        if typ not in ('tuple','dict','list','str'): continue
        es,ep=parts(expected,typ)
        actual=json.loads(row['canonical_value']) if row['canonical_value'] is not None else None
        ps,pp=parts(actual,typ)
        data=metadata[f]['input_value']
        if typ=='str': projections={'text_segment':canonical(data['text'])}
        elif typ=='dict': projections={'text':canonical(data['text'][:4])}
        elif typ=='tuple': projections={'sum_xs_mod997':canonical(sum(data['values']) % 997)}
        else: projections={f'xs_{i}_mod101':canonical(x % 101) for i,x in enumerate(data['values'][:4])}
        for component,projected in projections.items():
            assert component in ep
            stratum='reference_equals_input_projection' if ep[component]==projected else 'reference_differs_from_input_projection'
            name=f'{typ}.{component}'
            g=groups.setdefault(name,{}).setdefault(stratum,{'rows':0,'families':{},'structure_valid':0,'correct':0,'matches_copy':0,'correct_and_copy':0,'correct_not_copy':0,'wrong_copy':0})
            correct=ps==es and pp.get(component)==ep[component]
            copy=ps==es and pp.get(component)==projected
            g['rows']+=1;g['structure_valid']+=ps==es;g['correct']+=correct;g['matches_copy']+=copy
            g['correct_and_copy']+=correct and copy;g['correct_not_copy']+=correct and not copy;g['wrong_copy']+=copy and not correct
            g['families'].setdefault(f,[]).append((correct,copy))
    for strata in groups.values():
        for g in strata.values():
            fs=g.pop('families'); assert all(len(v)==2 for v in fs.values())
            g['families']=len(fs)
            g['families_correct_both']=sum(all(x[0] for x in v) for v in fs.values())
            g['families_copy_both']=sum(all(x[1] for x in v) for v in fs.values())
            g['families_correct_at_least_once']=sum(any(x[0] for x in v) for v in fs.values())
    copy_result[condition]=groups
print(json.dumps({'evidence':'POST_HOC_COMPONENT_DIAGNOSTIC_NOT_ACCURACY','sources_sha256':['c791e38c29d36a43fbac8ce00412e4c77d533665e0b8cb9eef8fa12fb918ac1d','30dd57131b3f0823df1642e2dabb0d511e10c8fe8acf49e0e98c53100df7b0b0','c3b4ab47cf2422afb311fa978496e2abfbe5485ac76040ee3dcead2986ace533'],'results':result,'input_projection_control':copy_result},indent=2))
