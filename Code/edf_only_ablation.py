"""Deadline-only EDF admission ablation.

Uses the same streams, auditor and worst-case EDF feasibility test as
dual_ledger_sim.py, but removes the exposure-ledger condition from admission.
Compares it with the dual-ledger gate under identical deadlines.
Usage: python edf_only_ablation.py edf_only_results.json
"""
import json, sys
import numpy as np
from dual_ledger_sim import data, feasible, EPS, B, THR, T

def run(seed, env, policy, D):
    s, loss = data(seed, env)
    serv = lambda i: (50 if (env == 'errdep' and loss[i]) else 5)
    smax = 50 if env == 'errdep' else 5
    use_ledger = policy == 'DL-FIFO'
    N = E = P = L = 0; excess = 0.0
    rel = {}; waiting = []; active = None; a_start = a_end = 0; resolved = []
    for t in range(T):
        if active is not None and t >= a_end:
            i = active; P -= 1; E += loss[i]; resolved.append(t - rel[i]); active = None
        if s[t] >= THR and (not use_ledger or E + P + 1 <= EPS * (N + 1) + B):
            rem = max(0, a_start + smax - t) if active is not None else 0
            rel[t] = t
            if feasible(t, rem, waiting, rel, smax, D, extra=t):
                waiting.append(t); N += 1; P += 1; L += loss[t]
        excess = max(excess, L - EPS * N - B)
        if active is None and waiting:
            j = waiting[0]; waiting.remove(j); active = j; a_start = t; a_end = t + serv(j)
    pend = [T - 1 - rel[i] for i in waiting] + ([T - 1 - rel[active]] if active is not None else [])
    ages = resolved + pend
    return dict(seed=seed, env=env, policy=policy, D=D, cov=100 * N / T,
                risk=(L / N if N else float('nan')), env_excess=float(excess),
                maxage=max(ages) if ages else 0, dviol=int(sum(a > D for a in ages)))

if __name__ == '__main__':
    out = [run(sd, env, pol, D)
           for env, D in [('benign', 200), ('indep', 200), ('errdep', 1000)]
           for pol in ['EDF-only', 'DL-FIFO'] for sd in range(30)]
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'edf_only_results.json', 'w'), indent=1)
