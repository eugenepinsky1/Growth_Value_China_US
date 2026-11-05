"""Generalised back-test used in the revision.

backtest2(Psig, Pret, f, ...) forms the trading signal from the price (or total-return)
index Psig and realises returns from the index Pret.  With Psig = Pret = price index it
reproduces engine.backtest exactly (checked in revision_checks.py).
"""
import numpy as np, pandas as pd
from engine import FREQS, START, all_ends, mdd

def backtest2(Psig, Pret, f, lookback=1, start=START, end=None, append_last=True):
    A = all_ends(Pret, f)
    st = pd.Timestamp(start)
    ev = A[A >= st]
    if end is not None:
        A2 = A[A >= pd.Timestamp(end)]
        ev = ev[ev <= A2[0]]
    if append_last and end is None and ev[-1] != Pret.index[-1]:
        ev = ev.append(pd.DatetimeIndex([Pret.index[-1]]))
    rows = []; hold_prev = None
    for j in range(1, len(ev)):
        t0, t1 = ev[j-1], ev[j]
        pos = A.get_loc(t0); tf = A[max(pos-lookback, 0)]
        fG = Psig.G[t0]/Psig.G[tf]-1; fV = Psig.V[t0]/Psig.V[tf]-1
        rG = Pret.G[t1]/Pret.G[t0]-1; rV = Pret.V[t1]/Pret.V[t0]-1; rM = Pret.M[t1]/Pret.M[t0]-1
        s = 'G' if fG > fV else ('V' if fG < fV else (hold_prev or 'G'))
        hold_prev = s
        rows.append(dict(t0=t0, t1=t1, fG=fG, fV=fV, rG=rG, rV=rV, rM=rM, strong=s))
    T = pd.DataFrame(rows)
    T['rS'] = np.where(T.strong == 'G', T.rG, T.rV)
    T['rW'] = np.where(T.strong == 'G', T.rV, T.rG)
    T['rEW'] = 0.5*(T.rG+T.rV)
    T['d'] = T.rS - T.rW
    dr = Pret.pct_change(); dr = dr.loc[(dr.index > ev[0]) & (dr.index <= ev[-1])]
    held = pd.Series(index=dr.index, dtype=object)
    ewl = pd.Series(index=dr.index, dtype=float)
    for _, r in T.iterrows():
        m = (dr.index > r.t0) & (dr.index <= r.t1); held[m] = r.strong
        sub = Pret.loc[(Pret.index > r.t0) & (Pret.index <= r.t1)]
        w = 0.5*(sub.G/Pret.G[r.t0]) + 0.5*(sub.V/Pret.V[r.t0]); lev = np.r_[1.0, w.values]
        ewl[m] = lev[1:]/lev[:-1]-1
    D = pd.DataFrame(index=dr.index)
    D['M'] = dr.M; D['G'] = dr.G; D['V'] = dr.V
    D['Strong'] = np.where(held == 'G', dr.G, dr.V); D['Weak'] = np.where(held == 'G', dr.V, dr.G)
    D['EW'] = ewl; D['held'] = held
    D.attrs['start'] = ev[0]
    return T, D

def years(D):
    return (D.index[-1]-D.attrs['start']).days/365.25

def perf(D, col):
    x = D[col]; yrs = years(D); n = len(D)/yrs
    W = 100*np.prod(1+x); cagr = (W/100)**(1/yrs)-1; vol = x.std()*np.sqrt(n)
    return dict(W=W, CAGR=cagr, Vol=vol, ARTV=cagr/vol, MaxDD=mdd(x))

def switches(T):
    return int((T.strong != T.strong.shift()).iloc[1:].sum())

def nw_t(x, lags=None):
    x = np.asarray(x, float); n = len(x); mu = x.mean(); e = x-mu
    if lags is None: lags = int(np.floor(4*(n/100)**(2/9)))
    s = (e@e)/n
    for l in range(1, lags+1):
        s += 2*(1-l/(lags+1))*(e[l:]@e[:-l])/n
    return mu/np.sqrt(s/n)

def stat_boot_idx(n, L, rng):
    # vectorised stationary bootstrap indices
    p = 1/L
    starts = rng.integers(n, size=n); newblk = rng.random(n) < p; newblk[0] = True
    idx = np.empty(n, dtype=int); cur = 0
    for i in range(n):
        cur = starts[i] if newblk[i] else (cur+1) % n
        idx[i] = cur
    return idx

def boot_artv_p(D, cols=('Strong', 'M', 'EW'), B=1000, L=21, rng=None):
    X = D[list(cols)].values; n = len(X); yrs = years(D); nyr = n/yrs
    def artv(x):
        W = np.prod(1+x, axis=0); return (W**(1/yrs)-1)/(x.std(axis=0, ddof=1)*np.sqrt(nyr))
    b0 = artv(X); d0 = np.array([b0[0]-b0[1], b0[0]-b0[2]])
    bs = np.empty((B, 2))
    for b in range(B):
        a = artv(X[stat_boot_idx(n, L, rng)]); bs[b] = [a[0]-a[1], a[0]-a[2]]
    p = [(np.abs(bs[:, i]-bs[:, i].mean()) >= abs(d0[i])).mean() for i in range(2)]
    return d0, np.array(p)

def breakeven(WS, WB, n):
    return (1-(WB/WS)**(1/(2*n)))*1e4 if (WS > WB and n > 0) else np.nan
