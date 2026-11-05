"""Kenneth R. French Data Library files (CRSP 202609 vintage) as downloaded by the authors:
Portfolios_Formed_on_BE-ME(_Wout_Div).csv and F-F_Research_Data_Factors(_daily).csv.
Growth = value-weighted 'Lo 30', value = value-weighted 'Hi 30' book-to-market portfolio;
market = Mkt-RF + RF (total return)."""
import os, io, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('FF_DIR', os.path.join(HERE, 'revision_data', 'french'))

def _block(fname, title):
    lines = open(os.path.join(SRC, fname), encoding='latin-1').read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.strip().startswith(title))
    hdr = i+1; rows = []
    for l in lines[hdr+1:]:
        t = l.strip()
        if not t or not t[0].isdigit(): break
        rows.append(l)
    df = pd.read_csv(io.StringIO('\n'.join([lines[hdr]]+rows)))
    df = df.rename(columns={df.columns[0]: 'period'})
    df.columns = [c.strip() for c in df.columns]
    return df

def monthly_bm(div=True):
    f = 'Portfolios_Formed_on_BE-ME.csv' if div else 'Portfolios_Formed_on_BE-ME_Wout_Div.csv'
    d = _block(f, 'Value Weight Returns -- Monthly')
    d.index = pd.to_datetime(d.period.astype(int).astype(str), format='%Y%m')+pd.offsets.MonthEnd(0)
    return d[['Lo 30', 'Med 40', 'Hi 30']].replace([-99.99, -999], np.nan)/100

def monthly_factors():
    d = _block('F-F_Research_Data_Factors.csv', ',Mkt-RF') if False else None
    lines = open(os.path.join(SRC, 'F-F_Research_Data_Factors.csv'), encoding='latin-1').read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(',Mkt-RF')); rows = []
    for l in lines[i+1:]:
        t = l.strip()
        if not t or not t[0].isdigit() or len(t.split(',')[0]) != 6: break
        rows.append(l)
    d = pd.read_csv(io.StringIO('\n'.join(['period'+lines[i]]+rows)))
    d.columns = [c.strip() for c in d.columns]
    d.index = pd.to_datetime(d.period.astype(int).astype(str), format='%Y%m')+pd.offsets.MonthEnd(0)
    return d[['Mkt-RF', 'RF']]/100

def monthly(div=True):
    b = monthly_bm(div); f = monthly_factors()
    r = pd.DataFrame({'G': b['Lo 30'], 'V': b['Hi 30'], 'M': f['Mkt-RF']+f['RF'], 'RF': f['RF']}).dropna()
    return r

def to_index(r, cols=('M', 'G', 'V')):
    P = (1+r[list(cols)]).cumprod()*100
    first = P.index[0]-pd.offsets.MonthEnd(1)
    return pd.concat([pd.DataFrame({c: [100.0] for c in cols}, index=[first]), P])
