"""Revision analysis C (updated): U.S. growth-value rotation 1927-2026 with the French Data
Library book-to-market portfolios (monthly, CRSP 202609 vintage), all rolling windows of the
China sample's length (111 months) and weak-market episodes.  Monthly data support the
monthly, quarterly, semiannual and annual frequencies; daily and weekly results use the
1971-2021 daily snapshot (rev_c_longus.py) and are affected by nonsynchronous trading."""
import pickle, numpy as np, pandas as pd
from scipy import stats
from engine2 import *
from data_ff2 import monthly, to_index
FR = ['M', 'Q', 'H', 'A']
rY, rN = monthly(True), monthly(False)
PY, PN = to_index(rY), to_index(rN)
PN['M'] = PY['M']                       # the market is available as a total return only
EVAL0 = pd.Timestamp('1927-12-31')
OUT = {'full': {}, 'div': {}, 'sub': {}}
def mperf(T):
    yrs = (T.t1.iloc[-1]-T.t0.iloc[0]).days/365.25
    g = lambda x: np.prod(1+x)**(1/yrs)-1
    return dict(S=g(T.rS), W=g(T.rW), E=g(T.rEW), M=g(T.rM), G=g(T.rG), V=g(T.rV), yrs=yrs)
Tf = {}
for f in FR:
    T, D = backtest2(PY, PY, f, start=EVAL0); Tf[f] = T
    s = T.rG-T.rV; sg = np.sign(T.fG-T.fV); p = mperf(T); n = switches(T)
    WS, WE, WM = [100*np.prod(1+T[c]) for c in ('rS', 'rEW', 'rM')]
    OUT['full'][f] = dict(p=p, t=nw_t(T.d), rho=float(np.corrcoef(s[1:], s[:-1])[0, 1]), hit=float((sg == np.sign(s)).mean()),
                          periods=len(T), n=n, beE=breakeven(WS, WE, n), beM=breakeven(WS, WM, n))
    o = OUT['full'][f]; print('FULL', f, {k: round(v*100, 2) for k, v in p.items() if k != 'yrs'}, 't', round(o['t'], 2), 'rho', round(o['rho'], 3), 'hit', round(o['hit'], 3), 'beE', round(o['beE'], 1), 'n', len(T))
    # sub-periods: pre-1971, 1971-2015, 2016-2026
    for lab, (a, b) in {'1928-1970': ('1927-12-31', '1970-12-31'), '1971-2015': ('1970-12-31', '2015-12-31'), '2016-2026': ('2015-12-31', None)}.items():
        T2, _ = backtest2(PY, PY, f, start=a, end=b)
        OUT['sub'][(f, lab)] = dict(p=mperf(T2), t=nw_t(T2.d))
    for lab, (ps, pr) in {'PR/PR': (PN, PN), 'PR/TR': (PN, PY), 'TR/TR': (PY, PY)}.items():
        T3, _ = backtest2(ps, pr, f, start=EVAL0); OUT['div'][(f, lab)] = dict(p=mperf(T3), t=nw_t(T3.d), timeV=float((T3.strong == 'V').mean()))
    Ta, _ = backtest2(PN, PY, f, start=EVAL0)
    OUT['div'][(f, 'agree')] = float((Ta.strong.values == T.strong.values).mean())
for k, v in OUT['sub'].items(): print('SUB', k, round((v['p']['S']-v['p']['E'])*100, 2), round(v['t'], 2))
for f in FR: print('DIV', f, {lab: round((OUT['div'][(f, lab)]['p']['S']-OUT['div'][(f, lab)]['p']['E'])*100, 2) for lab in ['PR/PR', 'PR/TR', 'TR/TR']}, 'agree', round(OUT['div'][(f, 'agree')], 3))
# ---- rolling 111-month windows
L = 111
me = PY.index[PY.index >= EVAL0]
cM = np.log1p(rY.M).cumsum(); cRF = np.log1p(rY.RF).cumsum(); cG = np.log1p(rY.G).cumsum(); cV = np.log1p(rY.V).cumsum()
for c in (cM, cRF, cG, cV): c.loc[EVAL0] = c[c.index <= EVAL0].iloc[-1]
TT = {}
for f in FR:
    T = Tf[f].copy(); T['lS'] = np.log1p(T.rS); T['lE'] = np.log1p(T.rEW); T['lW'] = np.log1p(T.rW); TT[f] = T
rows = []
for i in range(len(me)-L):
    a, b = me[i], me[i+L]; yrs = (b-a).days/365.25
    mk = (cM[b]-cM[a])/yrs; rf = (cRF[b]-cRF[a])/yrs
    vol = rY.M[(rY.index > a) & (rY.index <= b)].std()*np.sqrt(12)
    row = dict(start=a, end=b, mkt=np.expm1(mk), exc=mk-rf, vol=vol, gv=((cG[b]-cG[a])-(cV[b]-cV[a]))/yrs)
    for f in FR:
        g = TT[f][(TT[f].t0 >= a) & (TT[f].t1 <= b)]
        row[f+'_gap'] = (g.lS.sum()-g.lE.sum())/yrs
    rows.append(row)
W = pd.DataFrame(rows)
W['C1'] = W.exc <= 0; W['C2'] = W.mkt <= 0.03
OUT['win'] = W
def episodes(mask):
    idx = np.where(mask)[0]; eps = []
    if len(idx) == 0: return eps
    st = pv = idx[0]
    for k in idx[1:]:
        if k != pv+1: eps.append((st, pv)); st = k
        pv = k
    eps.append((st, pv)); return eps
OUT['episodes'] = {}
for c in ['C1', 'C2']:
    OUT['episodes'][c] = []
    for st, en in episodes(W[c].values):
        g = W.iloc[st:en+1]
        d = dict(first_start=g.start.iloc[0], last_start=g.start.iloc[-1], n=len(g), mkt=(g.mkt.min(), g.mkt.max()),
                 vol=g.vol.median(), gv=g.gv.median())
        for f in FR: d[f] = (g[f+'_gap'].median(), g[f+'_gap'].min(), g[f+'_gap'].max(), float((g[f+'_gap'] > 0).mean()))
        OUT['episodes'][c].append(d)
        print(c, d['first_start'].date(), d['last_start'].date(), d['n'], np.round(d['mkt'], 3), round(d['vol'], 3), round(d['gv'], 3), {f: np.round(d[f], 3) for f in FR})
OUT['allwin'] = {f: dict(med=W[f+'_gap'].median(), share=float((W[f+'_gap'] > 0).mean()),
                         corr_mkt=float(stats.spearmanr(W[f+'_gap'], W.mkt)[0]), mx=W[f+'_gap'].max(),
                         weak_med=W.loc[W.C1, f+'_gap'].median(), weak_share=float((W.loc[W.C1, f+'_gap'] > 0).mean()),
                         nonweak_med=W.loc[~W.C1, f+'_gap'].median()) for f in FR}
print('nwin', len(W), 'C1', int(W.C1.sum()), 'C2', int(W.C2.sum()))
print({f: {k: round(v, 3) for k, v in d.items()} for f, d in OUT['allwin'].items()})
pickle.dump(OUT, open('rev_c2.pkl', 'wb'))
