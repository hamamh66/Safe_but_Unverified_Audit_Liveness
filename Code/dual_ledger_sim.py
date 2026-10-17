import numpy as np, json, sys
EPS, B, THR, T = 0.10, 20.0, 0.80, 3000
def data(seed, env):
    rng = np.random.default_rng(seed)
    sig = lambda z: 1/(1+np.exp(-z))
    beta = np.array([3., -2., .5])
    X = rng.standard_normal((1800,3)); y = (rng.random(1800) < sig(X@beta)).astype(float)
    w = np.zeros(3)
    for _ in range(200):
        g = X.T@(sig(X@w)-y)/len(y) + 0.002*w; w -= 0.15*g
    Xs = rng.standard_normal((T,3)); ys = (rng.random(T) < sig(Xs@beta)).astype(int)
    if env != 'benign':
        flip = (rng.random(T) < 0.55) & (np.arange(T) >= 1500); ys = np.where(flip, 1-ys, ys)
    p = sig(Xs@w); yh = (p >= .5).astype(int); s = np.maximum(p, 1-p)
    loss = (yh != ys).astype(int)
    return s, loss

def feasible(now, act_rem, waiting, rel, smax, D, extra=None, first=None):
    """worst-case EDF (release order) completion check"""
    c = now + act_rem
    order = list(waiting)
    if first is not None:
        c += smax
        if c > rel[first] + D: return False
        order.remove(first)
    if extra is not None: order.append(extra)
    for j in order:
        c += smax
        if c > rel[j] + D: return False
    return True

def run(seed, env, policy, D):
    s, loss = data(seed, env)
    serv = lambda i: (50 if (env=='errdep' and loss[i]) else 5)
    smax = 50 if env=='errdep' else 5
    dual = policy.startswith('DL')
    N=E=P=0; L=0; excess=0.0
    rel = {}; waiting = []  # release-ordered list of ids
    active=None; a_start=a_end=0
    resolved_age = []; viol=0
    for t in range(T):
        if active is not None and t >= a_end:
            i = active; P -= 1; E += loss[i]; resolved_age.append(t-rel[i]); active=None
        # admission
        if s[t] >= THR and E+P+1 <= EPS*(N+1)+B:
            ok = True
            if dual:
                rem = max(0, a_start+smax-t) if active is not None else 0
                rel[t] = t
                ok = feasible(t, rem, waiting, rel, smax, D, extra=t)
            if ok:
                rel[t]=t; waiting.append(t); N+=1; P+=1; L+=loss[t]
        excess = max(excess, L-EPS*N-B)
        if active is None and waiting:
            if policy.endswith('FIFO'): j = waiting[0]
            elif policy=='R-HighConf': j = max(waiting, key=lambda k:(s[k],-k))
            elif policy=='R-AgeCap':
                j = waiting[0] if t-rel[waiting[0]] >= 200 else max(waiting, key=lambda k:(s[k],-k))
            elif policy=='DL-Slack':
                j = waiting[0]
                for k in sorted(waiting, key=lambda k:(-s[k],k)):
                    if feasible(t, 0, waiting, rel, smax, D, first=k): j=k; break
            waiting.remove(j); active=j; a_start=t; a_end=t+serv(j)
    pend_ages = [T-1-rel[i] for i in waiting] + ([T-1-rel[active]] if active is not None else [])
    ages = resolved_age + pend_ages
    viol = sum(a > D for a in resolved_age) + sum(a > D for a in pend_ages)
    return dict(seed=seed, env=env, policy=policy, D=D, cov=100*N/T, maxage=max(ages) if ages else 0,
                dviol=int(viol), env_excess=float(excess), pending=len(pend_ages),
                meanage=float(np.mean(resolved_age)) if resolved_age else 0.0)

if __name__=='__main__':
    out=[]
    pols=['R-FIFO','R-HighConf','R-AgeCap','DL-FIFO','DL-Slack']
    for env,D in [('benign',200),('indep',200),('errdep',1000)]:
        for pol in pols:
            for sd in range(30): out.append(run(sd,env,pol,D))
    for D in [50,100,400]:
        for pol in ['DL-FIFO','DL-Slack']:
            for sd in range(30): out.append(run(sd,'benign',pol,D))
    json.dump(out, open(sys.argv[1],'w'))
