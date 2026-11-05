"""Price and total-return indexes for the revision."""
import numpy as np, pandas as pd, os
from engine import prices
HERE = os.path.dirname(os.path.abspath(__file__))

def us_tr():
    """Total-return indexes of SPY, SPYG, SPYV: dividends reinvested at the ex-date close."""
    P = prices('US')
    dv = pd.read_csv(os.path.join(HERE, 'revision_data', 'US_dividends.csv'), parse_dates=['ex_date'])
    TR = pd.DataFrame(index=P.index)
    for col, tk in [('M', 'SPY'), ('G', 'SPYG'), ('V', 'SPYV')]:
        d = dv[dv.ticker == tk].set_index('ex_date').amount.reindex(P.index).fillna(0.0)
        r = (P[col]+d)/P[col].shift(1)-1
        r.iloc[0] = 0.0
        TR[col] = P[col].iloc[0]*np.cumprod(1+r)
    return P, TR

def cn_tr(yG, yV, yM):
    """China: price indexes plus a constant continuous dividend accrual (annual yields)."""
    P = prices('CN')
    dt = P.index.to_series().diff().dt.days.fillna(0).values/365.25
    TR = pd.DataFrame(index=P.index)
    for col, y in [('G', yG), ('V', yV), ('M', yM)]:
        r = P[col].pct_change().fillna(0).values
        acc = (1+y)**dt-1
        TR[col] = P[col].iloc[0]*np.cumprod((1+r)*(1+acc))
    return P, TR
