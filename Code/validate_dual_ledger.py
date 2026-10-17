"""Independent event-order audit and post-horizon verification of supplied runs.
Preserves the supplied in-horizon metrics. Records every accepted release through
completion, without new arrivals after T-1. Does not change the admission policy.
"""
import json,sys,hashlib,platform
from pathlib import Path
from functools import lru_cache
import numpy as np
from dual_ledger_sim import feasible, EPS, B, THR, T

@lru_cache(None)
def stream(seed,env):
    rng=np.random.default_rng(seed)
    sig=lambda z:1/(1+np.exp(-np.clip(z,-40,40)))
    beta=np.array([3.,-2.,.5]);X=rng.standard_normal((1800,3))
    y=(rng.random(1800)<sig(np.sum(X*beta,axis=1))).astype(float)
    w=np.zeros(3)
    for _ in range(200):
        w-=.15*(np.sum(X*(sig(np.sum(X*w,axis=1))-y)[:,None],axis=0)/len(y)+.002*w)
    Xs=rng.standard_normal((T,3));ys=(rng.random(T)<sig(np.sum(Xs*beta,axis=1))).astype(int)
    if env!='benign':
        flip=(rng.random(T)<.55)&(np.arange(T)>=1500);ys=np.where(flip,1-ys,ys)
    p=sig(np.sum(Xs*w,axis=1));return np.maximum(p,1-p),((p>=.5)!=ys).astype(int)

def verify(row):
    seed,env,policy,D=[row[k] for k in ['seed','env','policy','D']]
    s,loss=stream(seed,env);smax=50 if env=='errdep' else 5
    dual=policy.startswith('DL');N=E=P=L=0;active=None;start=end=0
    waiting=[];rel={};resolved=[];complete={};maxexcess=0.;t=0
    while t<T or active is not None or waiting:
        if active is not None and t>=end:
            i=active;P-=1;E+=int(loss[i]);resolved.append(t-rel[i]);complete[i]=t;active=None
        if t<T and s[t]>=THR and E+P+1<=EPS*(N+1)+B:
            rel[t]=t
            rem=max(0,start+smax-t) if active is not None else 0
            ok=not dual or feasible(t,rem,waiting,rel,smax,D,extra=t)
            if ok:
                waiting.append(t);N+=1;P+=1;L+=int(loss[t])
        assert L<=E+P and E+P<=EPS*N+B+1e-8
        maxexcess=max(maxexcess,L-EPS*N-B)
        if dual:
            rem=max(0,start+smax-t) if active is not None else 0
            assert feasible(t,rem,waiting,rel,smax,D)
        if active is None and waiting:
            if policy.endswith('FIFO'):j=waiting[0]
            elif policy=='R-HighConf':j=max(waiting,key=lambda k:(s[k],-k))
            elif policy=='R-AgeCap':j=waiting[0] if t-rel[waiting[0]]>=200 else max(waiting,key=lambda k:(s[k],-k))
            elif policy=='DL-Slack':
                j=waiting[0]
                for k in sorted(waiting,key=lambda k:(-s[k],k)):
                    if feasible(t,0,waiting,rel,smax,D,first=k):j=k;break
            else:raise ValueError(policy)
            if dual:assert feasible(t,0,waiting,rel,smax,D,first=j)
            waiting.remove(j);active=j;start=t;end=t+(50 if env=='errdep' and loss[j] else 5)
        if t==T-1:
            ages=resolved+[T-1-rel[i] for i in waiting]+([T-1-rel[active]] if active is not None else [])
            horizon=dict(cov=100*N/T,maxage=max(ages) if ages else 0,dviol=sum(x>D for x in ages),
                         env_excess=float(maxexcess),pending=len(waiting)+int(active is not None),
                         meanage=float(np.mean(resolved)) if resolved else 0.)
            for key,v in horizon.items():
                assert abs(v-row[key])<1e-9,(seed,env,policy,D,key,v,row[key])
            accepted_at_horizon=N;pending_at_horizon=P
        t+=1
        assert t<100000
    ages=[complete[i]-rel[i] for i in complete]
    assert len(ages)==accepted_at_horizon
    misses=sum(age>D for age in ages)
    if dual:assert misses==0 and max(ages,default=0)<=D
    return dict(seed=seed,env=env,policy=policy,D=D,accepted=accepted_at_horizon,
                pending_at_horizon=pending_at_horizon,all_resolved=True,
                final_completion_tick=max(complete.values(),default=-1),
                full_cohort_deadline_misses=misses,full_cohort_max_age=max(ages,default=0),
                horizon_metrics_match=True)

if __name__=='__main__':
    here=Path(__file__).resolve().parent
    src=here/'dual_ledger_results.json';rows=json.loads(src.read_text())
    results=[verify(row) for row in rows]
    dual=[r for r in results if r['policy'].startswith('DL')]
    summary=dict(total_runs=len(rows),dual_runs=len(dual),baseline_runs=len(rows)-len(dual),
                 matched_horizon_metrics_runs=sum(r['horizon_metrics_match'] for r in results),
                 dual_accepted_outputs=sum(r['accepted'] for r in dual),
                 dual_pending_outputs_followed=sum(r['pending_at_horizon'] for r in dual),
                 dual_full_cohort_deadline_misses=sum(r['full_cohort_deadline_misses'] for r in dual),
                 max_completion_tick=max(r['final_completion_tick'] for r in results),
                 source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                 python=platform.python_version(),numpy=np.__version__)
    target=Path(sys.argv[1]) if len(sys.argv)>1 else here/'validation_results.json'
    target.write_text(json.dumps(dict(summary=summary,runs=results),indent=2))
    print(json.dumps(summary,indent=2))
