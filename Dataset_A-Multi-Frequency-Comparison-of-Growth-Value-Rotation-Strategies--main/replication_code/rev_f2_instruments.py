"""Revision analysis F (updated): ETFs vs. non-investable book-to-market index portfolios over
the full U.S. window (31 Dec 2015 - 30 Apr 2025), monthly data, total returns."""
import pickle, numpy as np, pandas as pd
from engine2 import *
from data2 import us_tr
from data_ff2 import monthly, to_index
P, TR = us_tr()
me = pd.date_range('2015-12-31', '2025-04-30', freq='ME')
E = TR.reindex([TR.index[TR.index <= d][-1] for d in me]); E.index = me     # ETF month-end total-return indexes
I = to_index(monthly(True)).loc['2015-12-31':'2025-04-30']
OUT = {}
for f in ['M', 'Q', 'H', 'A']:
    row = {}
    for lab, X in [('ETF', E), ('Index', I)]:
        T, _ = backtest2(X, X, f, start='2015-12-31')
        y = (T.t1.iloc[-1]-T.t0.iloc[0]).days/365.25; g = lambda x: np.prod(1+x)**(1/y)-1
        s = T.rG-T.rV
        row[lab] = dict(S=g(T.rS), E=g(T.rEW), t=nw_t(T.d), rho=float(np.corrcoef(s[1:], s[:-1])[0, 1]), held=T.strong.values, s=s.values)
    OUT[f] = dict(ETF={k: v for k, v in row['ETF'].items() if k not in ('held', 's')}, Index={k: v for k, v in row['Index'].items() if k not in ('held', 's')},
                  agree=float(np.mean(row['ETF']['held'] == row['Index']['held'])), corr=float(np.corrcoef(row['ETF']['s'], row['Index']['s'])[0, 1]))
    print(f, {k: round(v, 4) for k, v in OUT[f]['ETF'].items()}, {k: round(v, 4) for k, v in OUT[f]['Index'].items()}, 'agree', round(OUT[f]['agree'], 3), 'corr', round(OUT[f]['corr'], 3))
pickle.dump(OUT, open('rev_f2.pkl', 'wb'))
