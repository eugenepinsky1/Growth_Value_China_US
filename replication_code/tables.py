from engine import *
import pickle
o=pickle.load(open('results.pkl','rb')); R=pickle.load(open('robust.pkl','rb'))
NM={'US':('SPY','SPYG','SPYV'),'CN':('SSEC','SSECG','SSECV')}
MK={'CN':'China','US':'U.S.'}
HDR=r'& \textbf{Daily} & \textbf{Weekly} & \textbf{Monthly} & \textbf{Quarterly} & \textbf{Semiann.} & \textbf{Annual} \\'
def row(lbl,vals,fmt='{:.1f}',bold=None):
    cells=[]
    for i,v in enumerate(vals):
        s=fmt.format(v) if v==v else '--'
        s=s.replace('-','$-$') if s.startswith('-') else s
        if bold is not None and bold[i]: s=r'\textbf{'+s+'}'
        cells.append(s)
    return lbl+' & '+' & '.join(cells)+r' \\'
def mrow(lbl,v,fmt='{:.1f}'):
    s=fmt.format(v); s=s.replace('-','$-$',1) if s.startswith('-') else s
    return lbl+r' & \multicolumn{6}{c}{'+s+r'} \\'
def table(cap,label,body,note,cols='lrrrrrr',wide=True):
    env='table*' if wide else 'table'
    return (f"\\begin{{{env}}}[!htbp]\n\\caption{{{cap}}}\\label{{{label}}}\n\\begin{{adjustwidth}}{{-\\extralength}}{{0cm}}\\centering\n"
            f"\\small\\begin{{tabular}}{{{cols}}}\n\\toprule\n{body}\n\\bottomrule\n\\end{{tabular}}\n\\end{{adjustwidth}}\n"
            f"\\begin{{adjustwidth}}{{-\\extralength}}{{0cm}}\\noindent{{\\footnotesize{{{note}}}}}\\end{{adjustwidth}}\n\\end{{{env}}}\n")
T={}
# Table: descriptive
b=r'& \textbf{Instrument} & \textbf{CAGR (\%)} & \textbf{Vol. (\%)} & \textbf{Skew.} & \textbf{Ex. kurt.} & \textbf{Min (\%)} & \textbf{Max (\%)} \\'+'\n\\midrule\n'
for m in ['CN','US']:
    d=R[m]['desc']; nm=NM[m]
    b+=r'\multicolumn{8}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+f" ({d['start']} to {d['end']}, {d['M']['n']:,} trading days)"+r'}} \\'+'\n'
    for k,role in zip(['M','G','V'],['Market','Growth','Value']):
        x=d[k]
        b+=f"{role} & {nm['MGV'.index(k)]} & {x['cagr']*100:.2f} & {x['vol']*100:.2f} & {x['skew']:.2f} & {x['kurt']:.2f} & {x['mn']*100:.2f} & {x['mx']*100:.2f} \\\\\n".replace(' -',' $-$')
    b+=f"\\multicolumn{{8}}{{l}}{{Correlations of daily returns: growth--value {d['corrGV']:.2f}; growth--market {d['corrGM']:.2f}; value--market {d['corrVM']:.2f}}} \\\\\n"
    if m=='CN': b+='\\midrule\n'
T['desc']=table('Descriptive statistics of daily returns over the evaluation window.','tab:desc',b.rstrip('\n'),
  'Notes: CAGR is the compound annual growth rate of the price index (split-adjusted closing prices; dividends are not included). Volatility is the annualized standard deviation of daily returns. Skewness and excess kurtosis are computed from daily returns. Min and Max are the smallest and largest one-day returns.',cols='llrrrrrr')
# calendar-year returns
b=r'& \multicolumn{4}{c}{\textbf{China}} & \multicolumn{4}{c}{\textbf{U.S.}} \\ \cmidrule(lr){2-5}\cmidrule(lr){6-9}'+'\n'
b+=r'\textbf{Year} & \textbf{SSEC} & \textbf{SSECG} & \textbf{SSECV} & \textbf{G$-$V} & \textbf{SPY} & \textbf{SPYG} & \textbf{SPYV} & \textbf{G$-$V} \\'+'\n\\midrule\n'
for y in range(2016,2026):
    c=R['CN']['yr'][y]; u=R['US']['yr'][y]
    vals=[c['M'],c['G'],c['V'],c['G']-c['V'],u['M'],u['G'],u['V'],u['G']-u['V']]
    b+=(f"{y}{'$^{a}$' if y==2025 else ''} & "+' & '.join(f'{v*100:.1f}' for v in vals)+r' \\'+'\n').replace(' -',' $-$')
T['years']=table('Calendar-year price returns (\\%) of the market, growth and value instruments.','tab:years',b.rstrip('\n'),
  '$^{a}$ 2025 is a partial year (through 31 March 2025 for China and 1 May 2025 for the U.S.). G$-$V is the growth return minus the value return.',cols='lrrrrrrrr')
# wealth
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    nm=NM[m]
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r'}} \\'+'\n'
    for k,l in zip('MGV',nm): b+=mrow(f'Buy-and-hold {l}',o[(m,'D')]['metrics'][k]['W'])+'\n'
    b+=row('50/50 growth--value',[o[(m,f)]['metrics']['EW']['W'] for f in FREQS])+'\n'
    S=[o[(m,f)]['metrics']['Strong']['W'] for f in FREQS]; Wk=[o[(m,f)]['metrics']['Weak']['W'] for f in FREQS]
    b+=row('Strong (trend-following)',S,bold=[s==max(S) for s in S])+'\n'
    b+=row('Weak (contrarian)',Wk,bold=[s==max(Wk) for s in Wk])+'\n'
    if m=='CN': b+='\\midrule\n'
T['wealth']=table('Terminal wealth of an initial investment of 100 by strategy and rebalancing frequency (gross of transaction costs).','tab:wealth',b.rstrip('\n'),
  'Notes: All strategies are evaluated over the same window (31 December 2015 to 31 March 2025 for China; 31 December 2015 to 1 May 2025 for the U.S.), so buy-and-hold values do not depend on the rebalancing frequency. The 50/50 portfolio holds equal weights in growth and value and is rebalanced at the stated frequency. The highest value in each Strong/Weak row is in bold.')
# win counts
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r'}} \\'+'\n'
    b+=row('Periods',[o[(m,f)]['periods'] for f in FREQS],'{:,}')+'\n'
    b+=row('Growth outperforms',[o[(m,f)]['nG'] for f in FREQS],'{:,}')+'\n'
    b+=row('Value outperforms',[o[(m,f)]['nV'] for f in FREQS],'{:,}')+'\n'
    b+=row('Growth share (\\%)',[100*o[(m,f)]['nG']/o[(m,f)]['periods'] for f in FREQS])+'\n'
    b+=row('Switches by Strong',[o[(m,f)]['switches'] for f in FREQS],'{:,}')+'\n'
    if m=='CN': b+='\\midrule\n'
T['wins']=table('Number of rebalancing periods in which growth or value outperforms, and number of style switches.','tab:wins',b.rstrip('\n'),
  'Notes: A period is counted for growth (value) when the growth (value) instrument has the higher return over that holding period. A switch occurs when the Strong strategy changes its holding; the Weak strategy switches on the same dates.')
# risk
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    nm=NM[m]
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r' --- average annual maximum drawdown (\%)}} \\'+'\n'
    for k,l in zip('MGV',nm): b+=mrow(f'Buy-and-hold {l}',100*o[(m,'D')]['metrics'][k]['AvgMDD'])+'\n'
    for k,l in [('EW','50/50 growth--value'),('Strong','Strong'),('Weak','Weak')]:
        b+=row(l,[100*o[(m,f)]['metrics'][k]['AvgMDD'] for f in FREQS])+'\n'
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r' --- full-sample maximum drawdown (\%)}} \\'+'\n'
    for k,l in zip('MGV',nm): b+=mrow(f'Buy-and-hold {l}',100*o[(m,'D')]['metrics'][k]['MaxDD'])+'\n'
    for k,l in [('Strong','Strong'),('Weak','Weak')]:
        b+=row(l,[100*o[(m,f)]['metrics'][k]['MaxDD'] for f in FREQS])+'\n'
    if m=='CN': b+='\\midrule\n'
T['risk']=table('Drawdown risk by strategy and rebalancing frequency.','tab:risk',b.rstrip('\n'),
  'Notes: The average annual maximum drawdown is the mean, over the nine full calendar years 2016--2024, of the largest peak-to-trough decline of the daily wealth path within each year. The full-sample maximum drawdown is the largest peak-to-trough decline over the whole evaluation window. Both are computed from compounded daily returns of the instrument actually held.')
# risk-adjusted
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    nm=NM[m]
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r'}} \\'+'\n'
    for k,l in zip('MGV',nm):
        x=o[(m,'D')]['metrics'][k]
        b+=mrow(f'B\\&H {l}: ARTV',x['ARTV'],'{:.2f}')+'\n'
    for key,lab,fmt,mult in [('CAGR','CAGR (\\%)','{:.2f}',100),('Vol','Volatility (\\%)','{:.2f}',100),('ARTV','ARTV','{:.2f}',1),('Sortino','Sortino','{:.2f}',1),('Calmar','Calmar','{:.2f}',1)]:
        for k,l in [('Strong','Strong'),('Weak','Weak')]:
            b+=row(f'{l}: {lab}',[mult*o[(m,f)]['metrics'][k][key] for f in FREQS],fmt)+'\n'
    b+=row('50/50: ARTV',[o[(m,f)]['metrics']['EW']['ARTV'] for f in FREQS],'{:.2f}')+'\n'
    if m=='CN': b+='\\midrule\n'
T['radj']=table('Return and risk-adjusted performance by strategy and rebalancing frequency.','tab:radj',b.rstrip('\n'),
  'Notes: CAGR is the compound annual growth rate. Volatility is the annualized standard deviation of daily returns. ARTV (annualized return-to-volatility) is CAGR divided by volatility. Sortino is CAGR divided by annualized downside deviation (target 0). Calmar is CAGR divided by the absolute full-sample maximum drawdown. Buy-and-hold (B\\&H) values do not depend on the frequency. CAGR and volatility of the B\\&H instruments are reported in Table~\\ref{tab:desc}.')
# inference
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+r'}} \\'+'\n'
    q=[o[(m,f)] for f in FREQS]
    b+=row('Mean Strong$-$Weak per period (\\%)',[x['dmean']*100 for x in q],'{:.3f}')+'\n'
    b+=row('Newey--West $t$-statistic',[x['dt'] for x in q],'{:.2f}')+'\n'
    b+=row('First-order autocorr. of $s_k$',[x['rho1'] for x in q],'{:.2f}')+'\n'
    b+=row('Hit rate of signal (\\%)',[x['hit']*100 for x in q])+'\n'
    b+=row('Binomial $p$-value (hit rate $=$ 50\\%)',[x['binom_p'] for x in q],'{:.3f}')+'\n'
    b+=row('Random-rotation percentile of Strong (\\%)',[x['mc_pct_strong']*100 for x in q])+'\n'
    b+=row('$\\Delta$ARTV, Strong $-$ market',[x['dARTV_SM'] for x in q],'{:.2f}')+'\n'
    b+=row('\\quad bootstrap $p$-value',[x['p_SM'] for x in q],'{:.3f}')+'\n'
    b+=row('$\\Delta$ARTV, Strong $-$ 50/50',[x['dARTV_SE'] for x in q],'{:.2f}')+'\n'
    b+=row('\\quad bootstrap $p$-value',[x['p_SE'] for x in q],'{:.3f}')+'\n'
    if m=='CN': b+='\\midrule\n'
T['inf']=table('Statistical evidence on the rotation signal.','tab:inf',b.rstrip('\n'),
  'Notes: $s_k$ is the growth-minus-value return in holding period $k$. By Proposition~\\ref{prop:decomp}, the Strong$-$Weak return in period $k$ equals $\\operatorname{sgn}(f_k)\\,s_k$. The Newey--West $t$-statistic uses the Bartlett kernel with the automatic lag $\\lfloor 4(n/100)^{2/9}\\rfloor$. The hit rate is the share of holding periods in which the formation-period winner also wins the holding period; the first holding period is compared with its pre-window formation period. The autocorrelation is computed from the in-window holding-period spreads. The random-rotation percentile is the share of 20,000 simulated strategies, each choosing growth or value by a fair coin flip every period, whose terminal wealth is below that of the Strong strategy. Bootstrap $p$-values are two-sided and come from 1000 stationary-bootstrap resamples of paired daily returns (mean block length 21 days). They test whether the ARTV difference is zero.',cols='lrrrrrr')
# costs
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    nm=NM[m]; c=R[m]['cost']
    b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+f" (buy-and-hold {nm[0]} = {c['D']['WM']:.1f})"+r'}} \\'+'\n'
    b+=row('Switches per year',[c[f]['swpy'] for f in FREQS])+'\n'
    for bp in [5,10,25]:
        b+=row(f'Strong, net wealth at {bp} bp',[c[f]['net'][bp][0] for f in FREQS])+'\n'
    b+=row('Break-even cost vs. market (bp)',[c[f]['be_M'] for f in FREQS])+'\n'
    b+=row('Break-even cost vs. 50/50 (bp)',[c[f]['be_E'] for f in FREQS])+'\n'
    if m=='CN': b+='\\midrule\n'
T['cost']=table('Sensitivity of the Strong strategy to transaction costs.','tab:cost',b.rstrip('\n'),
  'Notes: Costs are one-way, in basis points (bp) of the traded value. Each switch sells the whole position and buys the other style, so it costs twice the one-way rate. Net wealth starts from 100. The break-even cost is the one-way cost at which the net terminal wealth of the Strong strategy equals that of the benchmark; ``--'' means the Strong strategy underperforms the benchmark even with zero costs. The 50/50 benchmark is treated as costless, which makes the comparison slightly conservative.')
# subperiods
b=HDR+'\n\\midrule\n'
for m in ['CN','US']:
    nm=NM[m]
    for sp in ['2016-2019','2020-2025']:
        s=R[m]['sub']
        b+=r'\multicolumn{7}{l}{\textit{'+('Chinese market' if m=='CN' else 'U.S. market')+', '+sp.replace('-','--')+f" (buy-and-hold {nm[0]} CAGR = {100*s[(sp,'M')]['M']:.1f}\\%)".replace('= -','= $-$')+r'}} \\'+'\n'
        b+=row('Strong',[100*s[(sp,f)]['S'] for f in FREQS])+'\n'
        b+=row('Weak',[100*s[(sp,f)]['W'] for f in FREQS])+'\n'
        b+=row('50/50 growth--value',[100*s[(sp,f)]['E'] for f in FREQS])+'\n'
    if m=='CN': b+='\\midrule\n'
T['sub']=table('Sub-period compound annual growth rates (\\%), gross of costs.','tab:sub',b.rstrip('\n'),
  'Notes: The first sub-period runs from 31 December 2015 to 31 December 2019 and the second from 31 December 2019 to the end of the sample. For weekly rebalancing the split is at the last trading day of the week containing 31 December 2019 (3 January 2020).')
# lookback
b=r'& \multicolumn{4}{c}{\textbf{China}} & \multicolumn{4}{c}{\textbf{U.S.}} \\ \cmidrule(lr){2-5}\cmidrule(lr){6-9}'+'\n'
b+=r'\textbf{Holding, look-back} & \textbf{Strong} & \textbf{Weak} & \textbf{ARTV$^{S}$} & \textbf{Switches} & \textbf{Strong} & \textbf{Weak} & \textbf{ARTV$^{S}$} & \textbf{Switches} \\'+'\n\\midrule\n'
for f,Ls,unit in [('W',[1,4,13,26],'wk'),('M',[1,3,6,12],'mo')]:
    for L in Ls:
        c=R['CN']['lb'][(f,L)]; u=R['US']['lb'][(f,L)]
        lab=('Weekly' if f=='W' else 'Monthly')+f', $L={L}$ {unit}'
        b+=(f"{lab} & {c['WS']:.1f} & {c['WW']:.1f} & {c['artvS']:.2f} & {c['sw']} & {u['WS']:.1f} & {u['WW']:.1f} & {u['artvS']:.2f} & {u['sw']} \\\\\n").replace(' -',' $-$')
    if f=='W': b+='\\midrule\n'
T['lb']=table('Robustness to the length of the look-back (formation) window.','tab:lb',b.rstrip('\n'),
  'Notes: Strong and Weak columns report terminal wealth $W_T$ from an initial 100, gross of costs; ARTV$^{S}$ is the ARTV of the Strong strategy. The holding period equals the rebalancing interval. The signal compares the cumulative growth and value returns over the last $L$ completed periods. The first row of each block ($L=1$) is the baseline specification. Where fewer than $L$ periods of history exist at the start of the window, the formation period begins on the first available date.',cols='lrrrrrrrr')
pickle.dump(T,open('tables.pkl','wb'))
for k,v in T.items(): open(f'tab_{k}.tex','w').write(v)
print(T['inf'])
