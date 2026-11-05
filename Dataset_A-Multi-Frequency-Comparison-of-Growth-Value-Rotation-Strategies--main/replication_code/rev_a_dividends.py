"""Revision analysis A: dividends (Reviewer 1 point 1, Reviewer 2 point 5)."""
import pickle, numpy as np, pandas as pd
from scipy import stats
from engine import prices, FREQS
from engine2 import *
from data2 import us_tr, cn_tr
rng = np.random.default_rng(20261001)
OUT = {}

def full(Psig, Pret, f, boot=True):
    T, D = backtest2(Psig, Pret, f)
    r = {c: perf(D, c) for c in ['M', 'G', 'V', 'EW', 'Strong', 'Weak']}
    n = switches(T)
    s = T.rG-T.rV; sg = np.sign(T.fG-T.fV)
    hit = float((sg == np.sign(s)).mean())
    N = 20000; pick = rng.random((N, len(T))) < 0.5
    Wr = 100*np.prod(np.where(pick, 1+T.rG.values, 1+T.rV.values), axis=1)
    out = dict(perf=r, n=n, periods=len(T), dmean=float(T.d.mean()), t=float(nw_t(T.d)), hit=hit,
               binp=float(stats.binomtest(int((sg == np.sign(s)).sum()), len(T), 0.5).pvalue),
               rr=float((Wr < r['Strong']['W']).mean()),
               beM=breakeven(r['Strong']['W'], r['M']['W'], n), beE=breakeven(r['Strong']['W'], r['EW']['W'], n),
               timeV=float((D.held == 'V').mean()))
    if boot:
        d0, p = boot_artv_p(D, B=1000, rng=rng)
        out.update(dSM=d0[0], pSM=p[0], dSE=d0[1], pSE=p[1])
    return out

# ---------------- U.S.: actual ETF distributions
P, TR = us_tr()
for lab, (ps, pr) in {'PR/PR': (P, P), 'PR/TR': (P, TR), 'TR/TR': (TR, TR)}.items():
    for f in FREQS:
        OUT[('US', lab, f)] = full(ps, pr, f, boot=(lab != 'PR/PR'))
        o = OUT[('US', lab, f)]
        print('US', lab, f, {k: round(v['W'], 1) for k, v in o['perf'].items()}, 't', round(o['t'], 2),
              'beM', o['beM'], 'pSE', o.get('pSE'), 'timeV', round(o['timeV'], 2))

# ---------------- China: assumed dividend yields (growth, value, market)
SCEN = {'none': (0, 0, 0), 'low': (0.010, 0.020, 0.020), 'base': (0.010, 0.030, 0.025), 'high': (0.010, 0.045, 0.030)}
Pc = prices('CN')
for sc, (yg, yv, ym) in SCEN.items():
    _, TRc = cn_tr(yg, yv, ym)
    for f in FREQS:
        for lab, ps in [('PR/TR', Pc), ('TR/TR', TRc)]:
            if sc == 'none' and lab == 'TR/TR': continue
            OUT[('CN', sc, lab, f)] = full(ps, TRc, f, boot=(sc == 'base'))
            o = OUT[('CN', sc, lab, f)]
            print('CN', sc, lab, f, {k: round(v['W'], 1) for k, v in o['perf'].items()}, 't', round(o['t'], 2), 'pSE', o.get('pSE'))
# break-even value-minus-growth yield spread for the China Strong-vs-50/50 comparison (PR signal, TR realised)
be = {}
for f in FREQS:
    lo, hi = 0.0, 0.30
    def gap(dy):
        _, TRc = cn_tr(0.01, 0.01+dy, 0.025)
        T, D = backtest2(Pc, TRc, f); return perf(D, 'Strong')['W']-perf(D, 'EW')['W']
    if gap(hi) > 0: be[f] = np.inf; continue
    for _ in range(30):
        mid = (lo+hi)/2
        if gap(mid) > 0: lo = mid
        else: hi = mid
    be[f] = (lo+hi)/2
OUT['CN_be_spread'] = be
print('break-even yield spread', {f: round(v*100, 2) for f, v in be.items()})
pickle.dump(OUT, open('rev_a.pkl', 'wb'))
