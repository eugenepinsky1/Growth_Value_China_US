"""Revision analysis D: itemised implementation costs (Reviewer 2 point 6).

Per-switch costs are one-way, in bp of traded value; each switch is a sale and a purchase.
Annual fund fees are charged as a continuous drag on every strategy that holds a fund.
U.S. ETF prices are already net of fund expenses, so no extra fee drag is applied there.
The Chinese series are indexes, so a hypothetical tracking-ETF fee is charged to every
strategy (the market benchmark included).
"""
import pickle, numpy as np, pandas as pd
from engine import prices, FREQS
from engine2 import *
from data2 import us_tr, cn_tr

SCEN = {
 'US': {  # components: commission, half-spread, regulatory fee (sales only, averaged per side)
   'Low':  dict(comm=0.0, half_spread=0.5, reg=0.14, other=0.0, fee=0.0),
   'Base': dict(comm=0.0, half_spread=1.5, reg=0.14, other=0.5, fee=0.0),
   'High': dict(comm=2.0, half_spread=5.0, reg=0.14, other=3.0, fee=0.0)},
 'CN': {  # ETF implementation; 'stock' = replicating the index with A-shares (stamp duty on sales)
   'Low':  dict(comm=1.0, half_spread=2.0, reg=0.4, other=0.0, fee=0.20),
   'Base': dict(comm=2.5, half_spread=5.0, reg=0.4, other=2.0, fee=0.60),
   'High': dict(comm=5.0, half_spread=10.0, reg=0.4, other=5.0, fee=0.60),
   'Stocks': dict(comm=2.5, half_spread=10.0, reg=0.4, other=15.0, fee=0.0)},   # other = stamp duty (10 bp on sales, i.e. 5 bp per side) + 10 bp impact
}
OUT = {'scen': SCEN, 'res': {}}
for m in ['CN', 'US']:
    if m == 'US':
        P, TR = us_tr(); Ps, Pr = TR, TR            # total-return signal and returns
    else:
        P, TR = cn_tr(0.01, 0.03, 0.025); Ps, Pr = P, TR   # base dividend scenario
    for f in FREQS:
        T, D = backtest2(Ps, Pr, f); n = switches(T); yrs = years(D)
        W = {c: perf(D, c)['W'] for c in ['M', 'EW', 'Strong', 'G', 'V']}
        for sc, c in SCEN[m].items():
            oneway = (c['comm']+c['half_spread']+c['reg']+c['other'])/1e4
            drag = (1-c['fee']/100)**yrs
            # 50/50 rebalancing trades: traded fraction per rebalance = |w_G - 0.5| summed over both legs
            sh = 0.0
            for _, rr in T.iterrows():
                gG, gV = 0.5*(1+rr.rG), 0.5*(1+rr.rV); sh += abs(gG/(gG+gV)-0.5)*2
            WS = W['Strong']*(1-oneway)**(2*n)*drag
            WE = W['EW']*(1-oneway)**sh*drag
            WM = W['M']*drag
            OUT['res'][(m, f, sc)] = dict(oneway_bp=oneway*1e4, WS=WS, WE=WE, WM=WM, n=n,
                                          cagrS=(WS/100)**(1/yrs)-1, cagrE=(WE/100)**(1/yrs)-1, cagrM=(WM/100)**(1/yrs)-1)
        print(m, f, {sc: (round(OUT['res'][(m, f, sc)]['oneway_bp'], 1), round(OUT['res'][(m, f, sc)]['WS'], 1),
                          round(OUT['res'][(m, f, sc)]['WE'], 1), round(OUT['res'][(m, f, sc)]['WM'], 1)) for sc in SCEN[m]})
pickle.dump(OUT, open('rev_d.pkl', 'wb'))
