"""Long-history U.S. growth and value portfolios (Kenneth R. French Data Library, via the
FFresearch R package snapshot, data through April 2021).

Growth = value-weighted bottom 30% book-to-market portfolio ('Lo 30'), value = top 30%
('Hi 30'); market = total market return (the snapshot's 'market' series equals Mkt-RF + RF; verified for Oct 1987 and Mar 2020).  Daily returns include dividends; monthly returns are
available with and without dividends.
"""
import os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'revision_data')

def _load():
    bm = pd.read_csv(os.path.join(SRC, 'ff_bm_terciles.csv'), dtype={'period': str})
    fa = pd.read_csv(os.path.join(SRC, 'ff_market_rf_us.csv'), dtype={'period': str})
    return bm, fa

def daily_tr():
    bm, fa = _load()
    d = bm[(bm.frequency == 'day') & (bm.dividend == 'Y')]
    w = d.pivot_table(index='period', columns='portfolio', values='value')/100
    f = fa[fa.frequency == 'day'].pivot_table(index='period', columns='factor', values='value')/100
    r = pd.DataFrame({'G': w['Lo 30'], 'V': w['Hi 30'], 'M': f['market'], 'RF': f['risk free rate']})
    r.index = pd.to_datetime(r.index.astype(int).astype(str), format='%Y%m%d')
    return r.dropna()

def monthly(div):
    bm, fa = _load()
    d = bm[(bm.frequency == 'month') & (bm.dividend == div)]
    w = d.pivot_table(index='period', columns='portfolio', values='value')/100
    f = fa[fa.frequency == 'month'].pivot_table(index='period', columns='factor', values='value')/100
    r = pd.DataFrame({'G': w['Lo 30'], 'V': w['Hi 30'], 'M': f['market'], 'RF': f['risk free rate']})
    r.index = pd.to_datetime(r.index.astype(int).astype(str), format='%Y%m')+pd.offsets.MonthEnd(0)
    return r.dropna()

def to_index(r, cols=('M', 'G', 'V')):
    P = (1+r[list(cols)]).cumprod()*100
    first = P.index[0]-pd.Timedelta(days=1)
    P = pd.concat([pd.DataFrame({c: [100.0] for c in cols}, index=[first]), P])
    return P
