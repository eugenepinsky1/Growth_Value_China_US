"""Revision analysis E: pseudo out-of-sample evaluation (Reviewer 2 point 7).

(1) Split sample: select the rule (Strong or Weak) and frequency with the highest ARTV in
    2016-2019; report its 2020-2025 performance.
(2) U.S. long-history training: select on 1972-2015 (French portfolios), test on the
    2016-2025 ETF sample.
(3) Walk-forward: at each year-end from 2017, choose among the six Strong frequencies and
    the 50/50 mix the strategy with the best ARTV since 2016 (net of base-case costs),
    and hold it for the next calendar year.
"""
import pickle, numpy as np, pandas as pd
from engine import prices, FREQS
from engine2 import *
from data2 import us_tr, cn_tr
from data_ff2 import monthly, to_index
BASE = {'US': 2.14, 'CN': 9.9}      # one-way bp, base scenario of rev_d
OUT = {}

def artv_of(x):
    if len(x) < 20: return np.nan
    yrs = len(x)/252; W = np.prod(1+x); return (W**(1/yrs)-1)/(x.std()*np.sqrt(252))

def series(Ps, Pr, f, cost_bp):
    T, D = backtest2(Ps, Pr, f)
    c = cost_bp/1e4
    sw = (T.strong != T.strong.shift()).astype(int); sw.iloc[0] = 0
    out = {}
    for col in ['Strong', 'Weak']:
        x = D[col].copy()
        # charge the round trip on the first day of each holding period that starts with a switch
        for t0, s in zip(T.t0[sw.values == 1], [1]*int(sw.sum())):
            nxt = x.index[x.index > t0]
            if len(nxt): x[nxt[0]] = (1+x[nxt[0]])*(1-c)**2-1
        out[col] = x
    out['EW'] = D.EW; out['M'] = D.M
    return out

for m in ['CN', 'US']:
    if m == 'US':
        P, TR = us_tr(); Ps, Pr = TR, TR
    else:
        P, TR = cn_tr(0.01, 0.03, 0.025); Ps, Pr = P, TR
    S = {f: series(Ps, Pr, f, BASE[m]) for f in FREQS}
    # (1) split sample
    cand = {(rule, f): S[f][rule] for f in FREQS for rule in ['Strong', 'Weak']}
    tr = {k: artv_of(v[v.index <= '2019-12-31']) for k, v in cand.items()}
    best = max(tr, key=tr.get)
    te = lambda x: x[x.index > '2019-12-31']
    g = lambda x: (np.prod(1+x))**(252/len(x))-1
    OUT[(m, 'split')] = dict(best=best, train_artv=tr[best], test_cagr=g(te(cand[best])), test_artv=artv_of(te(cand[best])),
                             test_M=g(te(S['M']['M'])), test_EW=g(te(S['M']['EW'])),
                             test_Mstrong=g(te(S['M']['Strong'])), ranks={str(k): v for k, v in tr.items()})
    print(m, 'split', OUT[(m, 'split')]['best'], {k: round(v, 4) for k, v in OUT[(m, 'split')].items() if isinstance(v, float)})
    # (3) walk-forward over calendar years
    pool = {('Strong', f): S[f]['Strong'] for f in FREQS}; pool[('EW', 'M')] = S['M']['EW']
    yrs = sorted(set(S['D']['M'].index.year)); chosen = []; wf = []
    for y in yrs:
        if y < 2018: continue
        hist = {k: artv_of(v[v.index.year < y]) for k, v in pool.items()}
        k = max(hist, key=hist.get); chosen.append((y, k))
        wf.append(pool[k][pool[k].index.year == y])
    wfx = pd.concat(wf)
    seg = lambda x: x[x.index.year >= 2018]
    OUT[(m, 'wf')] = dict(chosen=chosen, cagr=g(wfx), artv=artv_of(wfx), M=g(seg(S['M']['M'])), EW=g(seg(S['M']['EW'])),
                          Mstrong=g(seg(S['M']['Strong'])), artvM=artv_of(seg(S['M']['M'])), artvEW=artv_of(seg(S['M']['EW'])))
    print(m, 'walk-forward', chosen, {k: round(v, 4) for k, v in OUT[(m, 'wf')].items() if isinstance(v, float)})

# (2) U.S.: train on the long history (1928-2015, monthly book-to-market portfolios), test on 2016-2025 ETFs
PF = to_index(monthly(True))
tr = {}
for f in ['M', 'Q', 'H', 'A']:
    T, D = backtest2(PF, PF, f, start='1927-12-31', end='2015-12-31')
    yrs = (T.t1.iloc[-1]-T.t0.iloc[0]).days/365.25
    for rule, col in [('Strong', 'rS'), ('Weak', 'rW')]:
        tr[(rule, f)] = (np.log1p(T[col]).sum()-np.log1p(T.rEW).sum())/yrs
best = max(tr, key=tr.get)
OUT[('US', 'longtrain')] = dict(ranks={str(k): v for k, v in tr.items()}, best=best)
print('US long-train (log excess over 50/50, 1928-2015)', {k: round(v, 4) for k, v in tr.items()}, 'best', best)
pickle.dump(OUT, open('rev_e.pkl', 'wb'))
