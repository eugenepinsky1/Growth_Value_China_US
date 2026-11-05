"""Revision analysis C: long U.S. history and weak-market windows (Reviewer 1 points 2-3)."""
import pickle, numpy as np, pandas as pd
from scipy import stats
from engine import FREQS
from engine2 import *
from data_ff import daily_tr, monthly, to_index
rng = np.random.default_rng(20261001)
r = daily_tr()
P = to_index(r)                          # daily total-return indexes, base 100
RF = r.RF
EVAL0 = pd.Timestamp('1971-12-31')
OUT = {'full': {}, 'win': {}, 'div': {}}

# ---- full-sample results 1972-2021 (total returns)
Tf = {}
for f in FREQS:
    T, D = backtest2(P, P, f, start=EVAL0)
    Tf[f] = T
    s = T.rG-T.rV; sg = np.sign(T.fG-T.fV)
    pr = {c: perf(D, c) for c in ['M', 'G', 'V', 'EW', 'Strong', 'Weak']}
    n = switches(T)
    OUT['full'][f] = dict(perf=pr, n=n, periods=len(T), t=nw_t(T.d), hit=float((sg == np.sign(s)).mean()),
                          rho=float(np.corrcoef(s[1:], s[:-1])[0, 1]),
                          beM=breakeven(pr['Strong']['W'], pr['M']['W'], n), beE=breakeven(pr['Strong']['W'], pr['EW']['W'], n))
    o = OUT['full'][f]
    print('FULL', f, {k: round(v['CAGR']*100, 2) for k, v in pr.items()}, 't', round(o['t'], 2), 'rho', round(o['rho'], 3),
          'hit', round(o['hit'], 3), 'beE', o['beE'])

# ---- dividends over the long sample: price-return vs total-return signals (monthly data)
mN, mY = monthly('N'), monthly('Y')
PN, PY = to_index(mN), to_index(mY)
PN = PN.reindex(PY.index)
for f in ['M', 'Q', 'H', 'A']:
    for lab, (ps, pr_) in {'PR/PR': (PN, PN), 'PR/TR': (PN, PY), 'TR/TR': (PY, PY)}.items():
        if lab == 'PR/PR':
            ps = ps.copy(); pr_ = ps.copy(); pr_['M'] = PY['M']   # market only available as total return
        T, D = backtest2(ps, pr_, f, start=EVAL0)
        yrs = (T.t1.iloc[-1]-T.t0.iloc[0]).days/365.25
        g = lambda x: np.prod(1+x)**(1/yrs)-1
        OUT['div'][(f, lab)] = dict(S=g(T.rS), W=g(T.rW), E=g(T.rEW), G=g(T.rG), V=g(T.rV), t=nw_t(T.d),
                                     agree=None, timeV=float((T.strong == 'V').mean()))
    # signal agreement PR vs TR
    Ta, _ = backtest2(PN, PY, f, start=EVAL0); Tb, _ = backtest2(PY, PY, f, start=EVAL0)
    OUT['div'][(f, 'agree')] = float((Ta.strong.values == Tb.strong.values).mean())
    print('DIV', f, {k: {a: round(b*100, 2) if isinstance(b, float) and a != 't' else b for a, b in v.items()} for k, v in OUT['div'].items() if k[0] == f and k[1] != 'agree'}, 'agree', OUT['div'][(f, 'agree')])

# ---- rolling windows of the same length as the China sample (111 months)
L = 111
me = pd.date_range(EVAL0, r.index[-1], freq='ME')
me = pd.DatetimeIndex([r.index[r.index <= d][-1] for d in me])   # last trading day of month
logm = np.log1p(r.M); logrf = np.log1p(RF)
cum = lambda s: s.cumsum()
cM, cRF = cum(logm), cum(logrf)
cG, cV = cum(np.log1p(r.G)), cum(np.log1p(r.V))
sdM = r.M
rows = []
TT = {}
for f in FREQS:
    T = Tf[f].copy()
    T['lS'] = np.log1p(T.rS); T['lE'] = np.log1p(T.rEW); T['lW'] = np.log1p(T.rW)
    TT[f] = T
for i in range(len(me)-L):
    a, b = me[i], me[i+L]; yrs = (b-a).days/365.25
    mk = (cM[b]-cM[a])/yrs; rf = (cRF[b]-cRF[a])/yrs
    vol = sdM[(sdM.index > a) & (sdM.index <= b)].std()*np.sqrt(252)
    gv = ((cG[b]-cG[a])-(cV[b]-cV[a]))/yrs
    row = dict(start=a, end=b, mkt=np.expm1(mk), exc=mk-rf, vol=vol, gv=gv)
    for f in FREQS:
        T = TT[f]; sel = (T.t0 >= a) & (T.t1 <= b)
        g = T[sel]
        row[f+'_S'] = g.lS.sum()/yrs; row[f+'_E'] = g.lE.sum()/yrs; row[f+'_W'] = g.lW.sum()/yrs
        row[f+'_gap'] = row[f+'_S']-row[f+'_E']
        s = (g.rG-g.rV).values
        row[f+'_sig'] = s.std(ddof=1)*np.sqrt(len(g)/yrs) if len(g) > 2 else np.nan
    rows.append(row)
W = pd.DataFrame(rows)
OUT['win'] = W
# weak-market criteria, fixed before looking at strategy results
W['C1'] = W.exc <= 0            # no equity premium over T-bills
W['C2'] = W.mkt <= 0.03         # total-return CAGR at most 3% (roughly flat in price terms)
def episodes(mask):
    idx = np.where(mask)[0]; eps = []
    if len(idx) == 0: return eps
    st = idx[0]; pv = idx[0]
    for k in idx[1:]:
        if k != pv+1: eps.append((st, pv)); st = k
        pv = k
    eps.append((st, pv)); return eps
summ = {}
for c in ['C1', 'C2']:
    eps = episodes(W[c].values); summ[c] = []
    for st, en in eps:
        g = W.iloc[st:en+1]
        d = dict(first_start=g.start.iloc[0], last_start=g.start.iloc[-1], first_end=g.end.iloc[0], last_end=g.end.iloc[-1],
                 n=len(g), mkt=(g.mkt.min(), g.mkt.max()), exc=(g.exc.min(), g.exc.max()), vol=g.vol.median(), gv=g.gv.median())
        for f in FREQS:
            d[f] = (g[f+'_gap'].median(), g[f+'_gap'].min(), g[f+'_gap'].max(), float((g[f+'_gap'] > 0).mean()))
            d[f+'_sig'] = g[f+'_sig'].median()
        summ[c].append(d)
        print(c, d['first_start'].date(), d['last_start'].date(), 'n', d['n'], 'mkt', np.round(d['mkt'], 3), 'vol', round(d['vol'], 3), 'gv', round(d['gv'], 3),
              {f: np.round(d[f], 3) for f in FREQS})
OUT['episodes'] = summ
# all windows
allw = {f: dict(med=W[f+'_gap'].median(), share=float((W[f+'_gap'] > 0).mean()),
                corr_mkt=float(stats.spearmanr(W[f+'_gap'], W.mkt)[0]), corr_sig=float(stats.spearmanr(W[f+'_gap'], W[f+'_sig'])[0]),
                p90=W[f+'_gap'].quantile(0.9), p10=W[f+'_gap'].quantile(0.1)) for f in FREQS}
OUT['allwin'] = allw
print('ALL windows', {f: {k: round(v, 3) for k, v in d.items()} for f, d in allw.items()})
# non-overlapping blocks
blocks = W.iloc[::L].copy(); OUT['blocks'] = blocks
print(blocks[['start', 'end', 'mkt', 'exc', 'vol', 'gv'] + [f+'_gap' for f in FREQS]].round(4).to_string())
pickle.dump(OUT, open('rev_c.pkl', 'wb'))
