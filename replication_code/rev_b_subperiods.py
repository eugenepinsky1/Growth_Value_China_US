"""Revision analysis B: why the China monthly advantage varies across sub-periods (Reviewer 1 point 2)."""
import pickle, numpy as np, pandas as pd
from engine import prices, FREQS
from engine2 import *
OUT = {}
for m in ['CN', 'US']:
    P = prices(m)
    T, D = backtest2(P, P, 'M')
    T['s'] = T.rG-T.rV; T['sgn'] = np.sign(T.fG-T.fV)
    T['x'] = 0.5*T.sgn*T.s                       # Strong minus 50/50 (Proposition 1)
    T['lx'] = np.log1p(T.rS)-np.log1p(T.rEW)     # log excess over 50/50
    T['year'] = T.t1.dt.year
    T['sub'] = np.where(T.t1 <= pd.Timestamp('2019-12-31'), '2016-2019', '2020-2025')
    # moments by sub-period: the AR(1) approximation E[x] = 0.5*rho*sigma*sqrt(2/pi)
    mom = {}
    for sp, g in T.groupby('sub'):
        s = g.s.values; rho = np.corrcoef(s[1:], s[:-1])[0, 1]; sig = s.std(ddof=1)
        yrs = (g.t1.iloc[-1]-g.t0.iloc[0]).days/365.25
        mom[sp] = dict(n=len(g), sigma=sig*np.sqrt(12), rho=rho, hit=float((g.sgn == np.sign(g.s)).mean()),
                       absmean=np.abs(s).mean(), mean_x=g.x.mean()*12, pred_x=0.5*rho*sig*np.sqrt(2/np.pi)*12,
                       t=nw_t(g.x.values), logx_pa=g.lx.sum()/yrs, timeV=float((g.strong == 'V').mean()),
                       big=int((np.abs(s) > 0.05).sum()))
    # yearly contributions (log points)
    yr = T.groupby('year').agg(lx=('lx', 'sum'), sig=('s', lambda v: v.std(ddof=1)*np.sqrt(12)),
                               hit=('sgn', lambda v: np.nan)).reset_index()
    yr['hit'] = [float((g.sgn == np.sign(g.s)).mean()) for _, g in T.groupby('year')]
    yr['spread'] = [float(np.prod(1+g.rG)/np.prod(1+g.rV)-1) for _, g in T.groupby('year')]
    # concentration: share of total log excess from the k best months
    tot = T.lx.sum(); srt = T.lx.sort_values(ascending=False)
    conc = {k: float(srt.iloc[:k].sum()/tot) for k in (3, 5, 10)}
    # result without the k best months
    drop = {}
    for k in (1, 3, 5):
        keep = T.drop(srt.index[:k]); drop[k] = float(np.expm1(keep.lx.sum()))
    # leave-one-year-out total log excess (annualised over remaining years)
    loyo = {}
    for y in sorted(T.year.unique()):
        g = T[T.year != y]; yrs = len(g)/12; loyo[y] = g.lx.sum()/yrs
    # rolling 36-month annualised log excess
    roll = (T.set_index('t1').lx.rolling(36).sum()/3).dropna()
    # top months table
    top = T.loc[srt.index[:5], ['t1', 'strong', 'rG', 'rV', 'lx']]
    OUT[m] = dict(T=T, mom=mom, yr=yr, conc=conc, drop=drop, loyo=loyo, roll=roll, top=top, tot_pa=tot/(len(T)/12))
    print(m, 'moments'); [print(' ', k, {a: round(b, 4) for a, b in v.items()}) for k, v in mom.items()]
    print(yr.round(4).to_string()); print('conc', conc, 'drop', drop); print('loyo', {k: round(v*100, 2) for k, v in loyo.items()})
    print(top.to_string()); print('roll min/max', roll.min(), roll.max(), (roll > 0).mean())
pickle.dump(OUT, open('rev_b.pkl', 'wb'))
