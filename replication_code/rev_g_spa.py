"""Minor revision: data-snooping-robust inference (White 2000 Reality Check; Hansen 2005 SPA).

Universe = every rotation specification reported in the paper for a market: Strong and Weak
at the six frequencies with a one-period look-back (12) plus the look-back variants of
Table 11 (weekly L=4,13,26; monthly L=3,6,12) for both rules (12), i.e. 24 strategies.
Benchmarks: the 50/50 growth-value mix (rebalanced monthly) and buy-and-hold of the market.
Performance = daily return differential (strategy minus benchmark); tests use the stationary
bootstrap.  Gross returns (price returns, as in Section 5) and returns net of base-case
costs (total returns, as in Section 7) are both reported.
"""
import pickle, sys, numpy as np, pandas as pd
from arch.bootstrap import SPA, StepM
from engine import prices, FREQS
from engine2 import *
from data2 import us_tr, cn_tr
BASE = {'US': 2.14, 'CN': 9.9}
LB = [('W', 4), ('W', 13), ('W', 26), ('M', 3), ('M', 6), ('M', 12)]
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 10000

def strat_series(Ps, Pr, f, L, cost_bp):
    T, D = backtest2(Ps, Pr, f, lookback=L)
    out = {'Strong': D.Strong.copy(), 'Weak': D.Weak.copy()}
    if cost_bp:
        c = cost_bp/1e4
        sw = (T.strong != T.strong.shift()); sw.iloc[0] = False
        for t0 in T.t0[sw.values]:
            for col in out:
                x = out[col]; nxt = x.index[x.index > t0]
                if len(nxt): x[nxt[0]] = (1+x[nxt[0]])*(1-c)**2-1
    return out, D

OUT = {}
for m in ['CN', 'US']:
    for variant in ['gross', 'net']:
        if variant == 'gross':
            P = prices(m); Ps = Pr = P; cost = 0
        else:
            if m == 'US': _, TR = us_tr(); Ps = Pr = TR
            else: P0, TR = cn_tr(0.01, 0.03, 0.025); Ps, Pr = P0, TR
            cost = BASE[m]
        S = {}; bench = None
        for f in FREQS:
            o, D = strat_series(Ps, Pr, f, 1, cost)
            for r in o: S[f'{r} {f} L1'] = o[r]
            if f == 'M': bench = {'50/50': D.EW, 'Market': D.M}
        for f, L in LB:
            o, _ = strat_series(Ps, Pr, f, L, cost)
            for r in o: S[f'{r} {f} L{L}'] = o[r]
        X = pd.DataFrame(S).dropna()
        for bname, b in bench.items():
            b = b.reindex(X.index)
            # arch uses losses: lower is better
            res = {}
            for bl in (5, 21, 63):
                spa = SPA(-b.values, -X.values, block_size=bl, reps=REPS, bootstrap='stationary', seed=20261111)
                spa.compute()
                res[bl] = dict(lower=float(spa.pvalues['lower']), consistent=float(spa.pvalues['consistent']), upper=float(spa.pvalues['upper']))
            sm = StepM(-b.values, -X.values, size=0.05, block_size=21, reps=REPS, bootstrap='stationary', seed=20261111)
            sm.compute()
            sup = [X.columns[i] for i in range(X.shape[1]) if i in list(sm.superior_models)] if len(sm.superior_models) else []
            best = (X.sub(b, axis=0)).mean().idxmax()
            OUT[(m, variant, bname)] = dict(res=res, best=best, superior=sup, K=X.shape[1], n=len(X),
                                            best_mean_pa=float((X[best]-b).mean()*252))
            print(m, variant, 'vs', bname, 'K', X.shape[1], 'best', best, round(OUT[(m, variant, bname)]['best_mean_pa']*100, 2),
                  {bl: {k: round(v, 3) for k, v in r.items()} for bl, r in res.items()}, 'StepM superior', sup)
pickle.dump(OUT, open('rev_g.pkl', 'wb'))
