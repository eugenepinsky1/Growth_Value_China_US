from engine import *
import pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
o=pickle.load(open('results.pkl','rb')); R=pickle.load(open('robust.pkl','rb'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
  'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e','axes.grid':True,
  'grid.color':'#e6e5e0','grid.linewidth':0.6,'axes.axisbelow':True,'legend.frameon':False})
BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'; VIO='#4a3aa7'; YEL='#eda100'; MAG='#e87ba4'
G1='#0b0b0b'; G2='#52514e'; G3='#8f8e88'
FL=['Daily','Weekly','Monthly','Quarterly','Semi-\nannual','Annual']; x=np.arange(6)
NM={'US':('SPY','SPYG','SPYV'),'CN':('SSEC','SSECG','SSECV')}
TT={'US':'U.S. market','CN':'Chinese market'}
def barfig(key,fname,ylabel,pct=False):
    fig,axs=plt.subplots(1,2,figsize=(10,4.2))
    for ax,m in zip(axs,['CN','US']):
        k=-100 if pct else 1
        S=np.array([o[(m,f)]['metrics']['Strong'][key] for f in FREQS])*k; W=np.array([o[(m,f)]['metrics']['Weak'][key] for f in FREQS])*k
        mk,gk,vk=NM[m]
        lines=[(o[(m,'D')]['metrics']['M'][key]*k,G1,'-',f'Buy & hold market ({mk} {{:.1f}} / {{:.1f}})'),]
        ref={'M':o[(m,'D')]['metrics']['M'][key]*k,'G':o[(m,'D')]['metrics']['G'][key]*k,'V':o[(m,'D')]['metrics']['V'][key]*k}
        top=max(S.max(),W.max(),*ref.values())*1.12; ax.set_ylim(0,top)
        bS=ax.bar(x-0.19,S,0.36,color=BLUE,label='Strong (trend-following)',edgecolor='white',linewidth=1)
        bW=ax.bar(x+0.19,W,0.36,color=ORANGE,label='Weak (contrarian)',edgecolor='white',linewidth=1)
        for bb,v in list(zip(bS,S))+list(zip(bW,W)):
            ax.text(bb.get_x()+bb.get_width()/2, v+0.01*top, f'{v:.1f}',ha='center',va='bottom',fontsize=6.5,color=G2,bbox=dict(boxstyle='square,pad=0.1',fc='white',ec='none',alpha=0.85))
        ax.axhline(ref['M'],color=G1,ls='-',lw=1.4,label=f'Buy & hold {mk} ({ref["M"]:.1f})')
        ax.axhline(ref['G'],color=G2,ls='--',lw=1.4,label=f'Buy & hold {gk} ({ref["G"]:.1f})')
        ax.axhline(ref['V'],color=G3,ls=':',lw=1.6,label=f'Buy & hold {vk} ({ref["V"]:.1f})')
        ax.set_xlim(-0.6,5.6)
        ax.set_xticks(x); ax.set_xticklabels(FL); ax.set_title(TT[m],fontsize=10,loc='left',color=G1)
        ax.set_ylabel(ylabel); ax.grid(axis='x',visible=False)
        ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.16),ncol=3,fontsize=7)
    fig.tight_layout(); fig.savefig(fname,dpi=300); plt.close(fig)
barfig('W','Figure1.png','Terminal wealth (initial = 100)')
barfig('AvgMDD','Figure3.png','Average annual max. drawdown depth (%)',pct=True)
# Fig3 wealth paths at monthly
fig,axs=plt.subplots(1,2,figsize=(10,3.6))
for ax,m in zip(axs,['CN','US']):
    T,D=backtest(m,'M')
    mk,gk,vk=NM[m]
    for c,col,ls,l in [('Strong',BLUE,'-','Strong (monthly)'),('Weak',ORANGE,'-','Weak (monthly)'),('M',G1,'-',f'Buy & hold {mk}'),
                       ('G',G2,'--',f'Buy & hold {gk}'),('V',G3,':',f'Buy & hold {vk}')]:
        w=100*(1+D[c]).cumprod(); w=pd.concat([pd.Series([100.0],index=[D.attrs['start']]),w])
        ax.plot(w.index,w.values,color=col,ls=ls,lw=1.6 if c in('Strong','Weak') else 1.2,label=l)
    ax.set_title(TT[m],fontsize=10,loc='left'); ax.set_ylabel('Wealth (initial = 100)'); ax.legend(fontsize=7,loc='upper left',ncol=2)
fig.tight_layout(); fig.savefig('Figure2.png',dpi=300); plt.close(fig)
# Fig4 cost
COL=[VIO,BLUE,AQUA,YEL,MAG,ORANGE]
fig,axs=plt.subplots(1,2,figsize=(10,4.4))
cs=np.linspace(0,30,61)
for ax,m in zip(axs,['CN','US']):
    for f,c in zip(FREQS,COL):
        W0=o[(m,f)]['metrics']['Strong']['W']; sw=o[(m,f)]['switches']
        ax.plot(cs,W0*(1-cs/1e4)**(2*sw),color=c,lw=1.6,label=f'Strong, {FNAME[f].lower()} ({sw} switches)')
    WM=o[(m,'D')]['metrics']['M']['W']
    ax.axhline(WM,color=G1,lw=1.2,ls='--',label=f'Buy & hold {NM[m][0]} ({WM:.1f})')
    ax.set_xlabel('One-way transaction cost (basis points)'); ax.set_ylabel('Net terminal wealth'); ax.set_title(TT[m],fontsize=10,loc='left')
    ax.set_ylim(0,None); ax.legend(fontsize=6.8,loc='upper center',bbox_to_anchor=(0.5,-0.2),ncol=2)
fig.tight_layout(); fig.savefig('Figure5.png',dpi=300); plt.close(fig)
# Fig5 mechanism: annualised mean Strong-Weak with 95% CI
fig,ax=plt.subplots(figsize=(7,3.4))
ppy={'D':None}
for j,(m,c) in enumerate([('CN',BLUE),('US',ORANGE)]):
    mu=[];ci=[]
    for f in FREQS:
        d=o[(m,f)]; n=d['periods']; 
        T,D=backtest(m,f); yrs=(D.index[-1]-D.attrs['start']).days/365.25; py=n/yrs
        se=abs(d['dmean']/d['dt']) if d['dt']!=0 else 0
        mu.append(d['dmean']*py*100); ci.append(1.96*se*py*100)
    ax.bar(x+(-0.19 if j==0 else 0.19),mu,0.36,yerr=ci,color=c,capsize=3,error_kw=dict(ecolor=G2,lw=1),label=TT[m],edgecolor='white')
ax.axhline(0,color=G2,lw=0.8); ax.set_xticks(x); ax.set_xticklabels(FL); ax.grid(axis='x',visible=False)
ax.set_ylabel('Mean Strong − Weak return\n(% per year, arithmetic)'); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig('Figure4.png',dpi=300); plt.close(fig)
print('ok')
