import pandas as pd, numpy as np
from load import load
FREQS=['D','W','M','Q','H','A']
FNAME={'D':'Daily','W':'Weekly','M':'Monthly','Q':'Quarterly','H':'Semiannual','A':'Annual'}
START=pd.Timestamp('2015-12-31')

def prices(mkt):
    d=load(mkt,'D').set_index('Date')[['MP','GP','VP']]
    d.columns=['M','G','V']
    return d

def period_key(idx,f):
    if f=='D': return pd.Series(np.arange(len(idx)),index=idx)
    if f=='W': return pd.Series(idx.to_period('W-FRI').astype(str),index=idx)
    if f=='M': return pd.Series(idx.year*100+idx.month,index=idx)
    if f=='Q': return pd.Series(idx.year*10+idx.quarter,index=idx)
    if f=='H': return pd.Series(idx.year*10+(idx.month>6),index=idx)
    if f=='A': return pd.Series(idx.year,index=idx)

def all_ends(P,f):
    k=period_key(P.index,f)
    e=P.index.to_series().groupby(k.values).max().sort_values()
    A=pd.DatetimeIndex(e.values)
    if A[0]!=P.index[0]: A=pd.DatetimeIndex([P.index[0]]).append(A)
    return A

def backtest(mkt,f,P=None,lookback=1,start=None,end=None):
    if P is None: P=prices(mkt)
    st=START if start is None else pd.Timestamp(start)
    A=all_ends(P,f)
    ev=A[A>=st]
    if end is not None:
        A2=A[A>=pd.Timestamp(end)]; ev=ev[ev<=A2[0]]
    if ev[0]!=st and start is None: raise ValueError('start not a period end')
    if end is None and ev[-1]!=P.index[-1]: ev=ev.append(pd.DatetimeIndex([P.index[-1]]))
    rows=[]; hold_prev=None
    for j in range(1,len(ev)):
        t0,t1=ev[j-1],ev[j]
        pos=A.get_loc(t0); tf=A[max(pos-lookback,0)]
        fG=P.G[t0]/P.G[tf]-1; fV=P.V[t0]/P.V[tf]-1
        rG=P.G[t1]/P.G[t0]-1; rV=P.V[t1]/P.V[t0]-1; rM=P.M[t1]/P.M[t0]-1
        s='G' if fG>fV else ('V' if fG<fV else (hold_prev or 'G'))
        hold_prev=s
        rows.append(dict(t0=t0,t1=t1,tf=tf,fG=fG,fV=fV,rG=rG,rV=rV,rM=rM,strong=s,weak='V' if s=='G' else 'G'))
    T=pd.DataFrame(rows)
    T['rS']=np.where(T.strong=='G',T.rG,T.rV); T['rW']=np.where(T.strong=='G',T.rV,T.rG)
    T['rEW']=0.5*(T.rG+T.rV)
    dr=P.pct_change(); dr=dr.loc[(dr.index>ev[0])&(dr.index<=ev[-1])]
    held=pd.Series(index=dr.index,dtype=object); ewl=pd.Series(index=dr.index,dtype=float)
    for _,r in T.iterrows():
        m=(dr.index>r.t0)&(dr.index<=r.t1); held[m]=r.strong
        sub=P.loc[(P.index>r.t0)&(P.index<=r.t1)]
        w=0.5*(sub.G/P.G[r.t0])+0.5*(sub.V/P.V[r.t0]); lev=np.r_[1.0,w.values]
        ewl[m]=lev[1:]/lev[:-1]-1
    D=pd.DataFrame(index=dr.index)
    D['M']=dr.M; D['G']=dr.G; D['V']=dr.V
    D['Strong']=np.where(held=='G',dr.G,dr.V); D['Weak']=np.where(held=='G',dr.V,dr.G)
    D['EW']=ewl; D['held']=held
    D.attrs['start']=ev[0]
    return T,D

_cache={}
def rebal_dates_all(P,f):
    key=(id(P),f)
    if key not in _cache:
        k=period_key(P.index,f); e=P.index.to_series().groupby(k.values).max().sort_values()
        _cache[key]=pd.DatetimeIndex(e.values)
    return _cache[key]

def ann_factor(D):
    yrs=(D.index[-1]-D.attrs['start']).days/365.25
    return len(D)/yrs, yrs

def mdd(x):
    w=(1+x).cumprod(); w=pd.concat([pd.Series([1.0]),w.reset_index(drop=True)])
    return (w/w.cummax()-1).min()

def metrics(D,col):
    x=D[col]; n,yrs=ann_factor(D)
    W=100*np.prod(1+x); cagr=(W/100)**(1/yrs)-1
    vol=x.std()*np.sqrt(n); down=np.sqrt((np.minimum(x,0)**2).mean())*np.sqrt(n)
    years=[y for y in range(2016,2025)]
    amdd=np.mean([mdd(x[x.index.year==y]) for y in years])
    MD=mdd(x)
    return dict(W=W,CAGR=cagr,Vol=vol,ARTV=cagr/vol,Sortino=cagr/down,MaxDD=MD,AvgMDD=amdd,Calmar=cagr/abs(MD),
                Skew=x.skew(),Kurt=x.kurt())
