from engine import *
import pickle
R={}
for m in ['US','CN']:
    P=prices(m)
    # descriptive stats daily over eval window
    dr=P.pct_change(); dr=dr[(dr.index>START)]
    n=len(dr); yrs=(dr.index[-1]-START).days/365.25; nyr=n/yrs
    desc={}
    for c in ['M','G','V']:
        x=dr[c]; W=np.prod(1+x)
        desc[c]=dict(n=n,cagr=W**(1/yrs)-1,vol=x.std()*np.sqrt(nyr),skew=x.skew(),kurt=x.kurt(),mn=x.min(),mx=x.max())
    desc['corrGV']=dr.G.corr(dr.V); desc['corrGM']=dr.G.corr(dr.M); desc['corrVM']=dr.V.corr(dr.M)
    desc['nyr']=nyr; desc['start']=str(dr.index[0].date()); desc['end']=str(dr.index[-1].date())
    # calendar-year returns
    yr={}
    for y in range(2016,2026):
        x=dr[dr.index.year==y]; yr[y]={c:np.prod(1+x[c])-1 for c in ['M','G','V']}
    # costs
    cost={}
    for f in FREQS:
        T,D=backtest(m,f,P)
        sw=int((T.strong!=T.strong.shift()).iloc[1:].sum())
        # initial purchase cost ignored for all (BH also buys once)
        WS=100*np.prod(1+T.rS); WW=100*np.prod(1+T.rW); WM=100*np.prod(1+T.rM); WE=100*np.prod(1+T.rEW)
        net={c:(WS*(1-c/1e4)**(2*sw), WW*(1-c/1e4)**(2*sw)) for c in [0,5,10,25]}
        be_M=(1-(WM/WS)**(1/(2*sw)))*1e4 if WS>WM else np.nan
        be_E=(1-(WE/WS)**(1/(2*sw)))*1e4 if WS>WE else np.nan
        cost[f]=dict(sw=sw,swpy=sw/yrs,net=net,be_M=be_M,be_E=be_E,WM=WM,WE=WE)
    # subperiods
    sub={}
    for lab,(a,b) in {'2016-2019':('2015-12-31','2019-12-31'),'2020-2025':('2019-12-31',None)}.items():
        for f in FREQS:
            T,D=backtest(m,f,P,start=a,end=b)
            yy=(D.index[-1]-D.attrs['start']).days/365.25
            g=lambda r: (np.prod(1+r))**(1/yy)-1
            sub[(lab,f)]=dict(S=g(T.rS),W=g(T.rW),M=g(T.rM),E=g(T.rEW),n=len(T),
                 artvS=metrics(D,'Strong')['ARTV'],artvM=metrics(D,'M')['ARTV'],artvE=metrics(D,'EW')['ARTV'])
    # lookback grid at monthly and weekly holding
    lb={}
    for f,Ls in [('M',[1,3,6,12]),('W',[1,4,13,26])]:
        for L in Ls:
            T,D=backtest(m,f,P,lookback=L)
            mS=metrics(D,'Strong'); mW=metrics(D,'Weak')
            sw=int((T.strong!=T.strong.shift()).iloc[1:].sum())
            lb[(f,L)]=dict(WS=mS['W'],WW=mW['W'],artvS=mS['ARTV'],artvW=mW['ARTV'],ddS=mS['AvgMDD'],sw=sw)
    R[m]=dict(desc=desc,yr=yr,cost=cost,sub=sub,lb=lb)
    print(m,'DESC',{k:(v if not isinstance(v,dict) else {kk:round(vv,4) for kk,vv in v.items()}) for k,v in desc.items()})
    print('YEARS'); [print(y,{c:round(v*100,1) for c,v in d.items()}) for y,d in yr.items()]
    print('COST'); [print(f,v['sw'],round(v['swpy'],1),{c:(round(a,1),round(b,1)) for c,(a,b) in v['net'].items()},'beM',round(v['be_M'],1) if v['be_M']==v['be_M'] else None,'beE',round(v['be_E'],1) if v['be_E']==v['be_E'] else None) for f,v in cost.items()]
    print('SUB'); [print(k,{kk:round(vv*100,1) if kk!='n' and not kk.startswith('artv') else round(vv,2) for kk,vv in v.items()}) for k,v in sub.items()]
    print('LB'); [print(k,{kk:round(vv,2) for kk,vv in v.items()}) for k,v in lb.items()]
pickle.dump(R,open('robust.pkl','wb'))
