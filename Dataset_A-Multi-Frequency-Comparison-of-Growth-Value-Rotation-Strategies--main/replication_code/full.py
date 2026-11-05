from engine import *
import json, pickle
from scipy import stats
rng=np.random.default_rng(20261001)
STR=['M','G','V','EW','Strong','Weak']
out={}
def nw_t(x,lags=None):
    x=np.asarray(x); n=len(x); mu=x.mean(); e=x-mu
    if lags is None: lags=int(np.floor(4*(n/100)**(2/9)))
    g0=(e@e)/n; s=g0
    for l in range(1,lags+1):
        g=(e[l:]@e[:-l])/n; s+=2*(1-l/(lags+1))*g
    se=np.sqrt(s/n); return mu/se, lags
def stat_boot_idx(n,L,rng):
    p=1/L; idx=np.empty(n,dtype=int); idx[0]=rng.integers(n)
    for i in range(1,n):
        idx[i]=rng.integers(n) if rng.random()<p else (idx[i-1]+1)%n
    return idx
for m in ['US','CN']:
    P=prices(m)
    for f in FREQS:
        T,D=backtest(m,f,P)
        r={c:metrics(D,c) for c in STR}
        sw=int((T.strong!=T.strong.shift()).iloc[1:].sum())
        s=T.rG-T.rV; d=np.sign(T.fG-T.fV)*s   # Strong minus Weak per period
        # note sign uses formation spread; ties -> 0 (none expected)
        t,lags=nw_t(d)
        rho1=np.corrcoef(s[1:],s[:-1])[0,1] if len(s)>3 else np.nan
        # sign persistence: P(sign(s_k)=sign(f_k))
        hit=float((np.sign(T.fG-T.fV)==np.sign(s)).mean())
        binom_p=stats.binomtest(int((np.sign(T.fG-T.fV)==np.sign(s)).sum()),len(T),0.5).pvalue
        nG=int((s>0).sum()); nV=int((s<0).sum())
        # random switching monte carlo: terminal wealth of random G/V choice each period
        N=20000
        pick=rng.random((N,len(T)))<0.5
        Wr=100*np.prod(np.where(pick,1+T.rG.values,1+T.rV.values),axis=1)
        pct=float((Wr<r['Strong']['W']).mean()); pctW=float((Wr<r['Weak']['W']).mean())
        # stationary bootstrap of daily ARTV difference Strong - M and Strong - EW
        X=D[['Strong','M','EW']].values; n=len(X); nyr,yrs=ann_factor(D)
        def artv(x):
            W=np.prod(1+x,axis=0); cagr=W**(1/yrs)-1; return cagr/(x.std(axis=0,ddof=1)*np.sqrt(nyr))
        base=artv(X); dSM=base[0]-base[1]; dSE=base[0]-base[2]
        B=1000; bs=np.empty((B,2))
        for b in range(B):
            ii=stat_boot_idx(n,21,rng); a=artv(X[ii]); bs[b]=[a[0]-a[1],a[0]-a[2]]
        # two-sided p-value via centred bootstrap distribution
        pSM=float((np.abs(bs[:,0]-bs[:,0].mean())>=abs(dSM)).mean()); pSE=float((np.abs(bs[:,1]-bs[:,1].mean())>=abs(dSE)).mean())
        out[(m,f)]=dict(metrics=r,periods=len(T),switches=sw,dmean=float(d.mean()),dt=float(t),nwlags=lags,rho1=float(rho1),
            hit=hit,binom_p=float(binom_p),nG=nG,nV=nV,mc_pct_strong=pct,mc_pct_weak=pctW,mc_median=float(np.median(Wr)),
            dARTV_SM=float(dSM),p_SM=pSM,dARTV_SE=float(dSE),p_SE=pSE,ciSM=np.percentile(bs[:,0]-bs[:,0].mean()+dSM,[2.5,97.5]).tolist())
        print(m,f,len(T),sw,f"W S {r['Strong']['W']:.1f} M {r['M']['W']:.1f} EW {r['EW']['W']:.1f} | ARTV S {r['Strong']['ARTV']:.2f} M {r['M']['ARTV']:.2f} EW {r['EW']['ARTV']:.2f} W {r['Weak']['ARTV']:.2f}",
              f"| d {d.mean()*100:.3f}% t {t:.2f} rho1 {rho1:.3f} hit {hit:.3f} p {binom_p:.3f} | MC pct {pct:.3f} | dSM {dSM:.2f} p {pSM:.3f} dSE {dSE:.2f} p {pSE:.3f}")
pickle.dump(out,open('results.pkl','wb'))
