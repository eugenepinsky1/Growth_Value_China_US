import pickle, numpy as np, sys
OUTD = sys.argv[1]
A = pickle.load(open('rev_a.pkl', 'rb')); B = pickle.load(open('rev_b.pkl', 'rb')); C = pickle.load(open('rev_c2.pkl', 'rb')); C0 = pickle.load(open('rev_c.pkl', 'rb'))
Dd = pickle.load(open('rev_d.pkl', 'rb')); E = pickle.load(open('rev_e.pkl', 'rb')); F = pickle.load(open('rev_f2.pkl', 'rb'))
FR = ['D', 'W', 'M', 'Q', 'H', 'A']
HDR = r'& \textbf{Daily} & \textbf{Weekly} & \textbf{Monthly} & \textbf{Quarterly} & \textbf{Semiann.} & \textbf{Annual} \\'
def n(v, fmt='{:.1f}'):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))): return '--'
    s = fmt.format(v); return s.replace('-', '$-$', 1) if s.startswith('-') else s
def row(lbl, vals, fmt='{:.1f}'): return lbl+' & '+' & '.join(n(v, fmt) for v in vals)+r' \\'
def mrow(lbl, v, fmt='{:.1f}'): return lbl+r' & \multicolumn{6}{c}{'+n(v, fmt)+r'} \\'
def wrap(cap, lab, body, note, cols='lrrrrrr'):
    return (f"\\begin{{table*}}[!htbp]\n\\caption{{\\{MAC}{{{cap}}}}}\\label{{{lab}}}\n\\begin{{adjustwidth}}{{-\\extralength}}{{0cm}}\\centering\n"
            f"\\small\\{MAC}{{\\begin{{tabular}}{{{cols}}}\n\\toprule\n{body}\n\\bottomrule\n\\end{{tabular}}}}\n\\end{{adjustwidth}}\n"
            f"\\begin{{adjustwidth}}{{-\\extralength}}{{0cm}}\\noindent{{\\footnotesize{{\\{MAC}{{{note}}}}}}}\\end{{adjustwidth}}\n\\end{{table*}}\n")
T = {}
# ---------------- U.S. total returns
MAC = 'XRev'
b = HDR+'\n\\midrule\n'
for lab, title in [('PR/PR', 'Original: price-return signal, price returns'), ('PR/TR', 'Price-return signal, total returns realized'), ('TR/TR', 'Total-return signal, total returns realized')]:
    o = {f: A[('US', lab, f)] for f in FR}
    b += r'\multicolumn{7}{l}{\textit{'+title+r'}} \\'+'\n'
    if lab != 'PR/PR':
        b += mrow('Buy-and-hold SPY', o['M']['perf']['M']['W'])+'\n'+mrow('Buy-and-hold SPYG / SPYV', None).replace('--', f"{o['M']['perf']['G']['W']:.1f} / {o['M']['perf']['V']['W']:.1f}")+'\n'
    b += row('50/50 growth--value', [o[f]['perf']['EW']['W'] for f in FR])+'\n'
    b += row('Strong', [o[f]['perf']['Strong']['W'] for f in FR])+'\n'
    b += row('Weak', [o[f]['perf']['Weak']['W'] for f in FR])+'\n'
    b += row('Newey--West $t$ (Strong$-$Weak)', [o[f]['t'] for f in FR], '{:.2f}')+'\n'
    if lab != 'PR/PR':
        b += row('Bootstrap $p$, $\\Delta$ARTV Strong$-$50/50', [o[f]['pSE'] for f in FR], '{:.3f}')+'\n'
    b += row('Break-even cost vs. SPY (bp)', [o[f]['beM'] for f in FR])+'\n'
    if lab != 'TR/TR': b += '\\midrule\n'
T['us_tr'] = wrap('U.S. results with dividends: terminal wealth (initial 100, gross of costs) and inference.', 'tab:us_tr', b.rstrip('\n'),
  'Notes: Total returns reinvest each SPY, SPYG and SPYV cash distribution (income and capital gains, as reported by State Street~\\cite{SSGA_Dist}) at the closing price of its ex-dividend date. In the original price-return case, buy-and-hold wealth is 273.9 (SPY), 331.3 (SPYG) and 205.8 (SPYV). ``--\'\' in the break-even row means that Strong does not beat SPY even at zero cost. Bootstrap $p$-values as in Table~\\ref{tab:inf}.')
# ---------------- China dividend scenarios
MAC = 'XRev'
b = HDR+'\n\\midrule\n'
for sc, title in [('none', 'No dividends (original)'), ('low', 'Low: growth 1.0\\%, value 2.0\\%, market 2.0\\%'), ('base', 'Base: growth 1.0\\%, value 3.0\\%, market 2.5\\%'), ('high', 'High: growth 1.0\\%, value 4.5\\%, market 3.0\\%')]:
    lab = 'PR/TR' if sc == 'none' else 'TR/TR'
    o = {f: A[('CN', sc, lab, f)] for f in FR}
    b += r'\multicolumn{7}{l}{\textit{'+title+r'}} \\'+'\n'
    b += mrow('Buy-and-hold SSEC', o['M']['perf']['M']['W'])+'\n'
    b += row('50/50 growth--value', [o[f]['perf']['EW']['W'] for f in FR])+'\n'
    b += row('Strong', [o[f]['perf']['Strong']['W'] for f in FR])+'\n'
    b += row('Newey--West $t$ (Strong$-$Weak)', [o[f]['t'] for f in FR], '{:.2f}')+'\n'
    if sc == 'base': b += row('Bootstrap $p$, $\\Delta$ARTV Strong$-$50/50', [o[f]['pSE'] for f in FR], '{:.3f}')+'\n'
    if sc != 'high': b += '\\midrule\n'
T['cn_div'] = wrap('China: sensitivity of terminal wealth (initial 100, gross of costs) to assumed dividend yields.', 'tab:cn_div', b.rstrip('\n'),
  'Notes: Total-return series add a constant dividend accrual at the stated annual yields to the price indexes; signals use the resulting total-return series. Using price-return signals with total returns realized gives very similar results (monthly Strong 205.3, 215.5 and 231.5 in the three scenarios). Bootstrap $p$-values as in Table~\\ref{tab:inf}.')
# ---------------- China sub-period anatomy
MAC = 'XRev'
b = r'& \multicolumn{2}{c}{\textbf{China}} & \multicolumn{2}{c}{\textbf{U.S.}} \\ \cmidrule(lr){2-3}\cmidrule(lr){4-5}'+'\n'
b += r'& \textbf{2016--2019} & \textbf{2020--2025} & \textbf{2016--2019} & \textbf{2020--2025} \\'+'\n\\midrule\n'
def g(m, sp, k): return B[m]['mom'][sp][k]
items = [('Months', 'n', '{:.0f}', 1), ('Strong minus 50/50, log points p.a. (\\%)', 'logx_pa', '{:.2f}', 100),
         ('\\quad Newey--West $t$', 't', '{:.2f}', 1), ('Volatility of G$-$V spread, annualized (\\%)', 'sigma', '{:.1f}', 100),
         ('First-order autocorrelation of spread', 'rho', '{:.2f}', 1), ('Hit rate of signal (\\%)', 'hit', '{:.1f}', 100),
         ('Months with $|s_k|>5\\%$', 'big', '{:.0f}', 1), ('AR(1) prediction $\\tfrac12\\rho\\sigma_s\\sqrt{2/\\pi}$, p.a. (\\%)', 'pred_x', '{:.2f}', 100),
         ('Realized mean of $\\tfrac12\\operatorname{sgn}(f_k)s_k$, p.a. (\\%)', 'mean_x', '{:.2f}', 100)]
for lbl, k, fmt, sc in items:
    b += lbl+' & '+' & '.join(n(g(m, sp, k)*sc, fmt) for m in ['CN', 'US'] for sp in ['2016-2019', '2020-2025'])+r' \\'+'\n'
T['sub'] = wrap('Anatomy of the monthly rotation advantage by sub-period.', 'tab:subanat', b.rstrip('\n'),
  'Notes: Monthly rebalancing, look-back of one month, price returns as in Table~\\ref{tab:sub}. Strong minus 50/50 is the sum of $\\log(1+r^S_k)-\\log(1+m_k)$ divided by the number of years. By Proposition~\\ref{prop:decomp}, $r^S_k-m_k=\\tfrac12\\operatorname{sgn}(f_k)s_k$; under an AR(1) spread its mean is $\\tfrac12\\rho\\sigma_s\\sqrt{2/\\pi}$ (Equation~\\eqref{eq:ar1}).', cols='lrrrr')
# ---------------- long U.S. history (monthly data 1928-2026)
MAC = 'XRev'
F4 = ['M', 'Q', 'H', 'A']
HDR4 = r'& \textbf{Monthly} & \textbf{Quarterly} & \textbf{Semiann.} & \textbf{Annual} \\'
def row4(lbl, vals, fmt='{:.2f}'): return lbl+' & '+' & '.join(n(v, fmt) for v in vals)+r' \\'
fu = C['full']
b = HDR4+'\n\\midrule\n'
b += r'\multicolumn{5}{l}{\textit{Compound annual return (\%), total returns, January 1928--September 2026}} \\'+'\n'
b += r'Buy-and-hold market / growth / value & \multicolumn{4}{c}{'+f"{fu['M']['p']['M']*100:.2f} / {fu['M']['p']['G']*100:.2f} / {fu['M']['p']['V']*100:.2f}"+r'} \\'+'\n'
b += row4('50/50 growth--value', [fu[f]['p']['E']*100 for f in F4])+'\n'
b += row4('Strong', [fu[f]['p']['S']*100 for f in F4])+'\n'
b += row4('Weak', [fu[f]['p']['W']*100 for f in F4])+'\n'
b += row4('Newey--West $t$ (Strong$-$Weak)', [fu[f]['t'] for f in F4])+'\n'
b += row4('First-order autocorr. of $s_k$', [fu[f]['rho'] for f in F4])+'\n'
b += row4('Hit rate of signal (\\%)', [fu[f]['hit']*100 for f in F4], '{:.1f}')+'\n'
b += row4('Number of holding periods', [fu[f]['periods'] for f in F4], '{:.0f}')+'\n'
b += row4('Break-even cost vs. 50/50 (bp)', [fu[f]['beE'] for f in F4], '{:.1f}')+'\n'
b += '\\midrule\n'+r'\multicolumn{5}{l}{\textit{Strong minus 50/50, CAGR difference (pp) [Newey--West $t$], by sub-period}} \\'+'\n'
for lab in ['1928-1970', '1971-2015', '2016-2026']:
    b += lab.replace('-', '--')+' & '+' & '.join(n((C['sub'][(f, lab)]['p']['S']-C['sub'][(f, lab)]['p']['E'])*100, '{:.2f}')+' ['+n(C['sub'][(f, lab)]['t'], '{:.2f}')+']' for f in F4)+r' \\'+'\n'
b += '\\midrule\n'+r'\multicolumn{5}{l}{\textit{Effect of dividends on the signal: Strong minus 50/50, CAGR difference (pp)}} \\'+'\n'
for lab, t in [('PR/PR', 'Price-return signal and returns'), ('PR/TR', 'Price-return signal, total returns'), ('TR/TR', 'Total-return signal and returns')]:
    b += row4(t, [(C['div'][(f, lab)]['p']['S']-C['div'][(f, lab)]['p']['E'])*100 for f in F4])+'\n'
b += row4('Same holding with PR and TR signal (\\% of periods)', [C['div'][(f, 'agree')]*100 for f in F4], '{:.1f}')+'\n'
b += '\\midrule\n'+r'\multicolumn{5}{l}{\textit{All '+str(len(C['win']))+r' rolling windows of 111 months (the length of the China sample)}} \\'+'\n'
aw = C['allwin']
b += row4('Median Strong minus 50/50 (log, \\% p.a.)', [aw[f]['med']*100 for f in F4])+'\n'
b += row4('Windows with Strong above 50/50 (\\%)', [aw[f]['share']*100 for f in F4], '{:.1f}')+'\n'
b += row4('Maximum across windows (log, \\% p.a.)', [aw[f]['mx']*100 for f in F4])+'\n'
b += row4('Spearman corr. with market return', [aw[f]['corr_mkt'] for f in F4])+'\n'
b += row4('Median in weak-market windows (C1)', [aw[f]['weak_med']*100 for f in F4])+'\n'
b += row4('Median in other windows', [aw[f]['nonweak_med']*100 for f in F4])+'\n'
T['longus'] = wrap('U.S. growth--value rotation, 1928--2026, with value-weighted book-to-market portfolios.', 'tab:longus', b.rstrip('\n'),
  'Notes: Growth and value are the value-weighted bottom and top 30\\% book-to-market portfolios of NYSE, AMEX and NASDAQ stocks (NYSE breakpoints) and the market is the value-weighted market portfolio (Mkt$-$RF + RF), from the Kenneth R. French Data Library (CRSP 202609 vintage). Monthly returns with and without dividends; the market is a total return throughout. Evaluation starts on 31 December 1927; earlier months are used for the first signals. The 2016--2026 sub-period runs to September 2026. Daily and weekly frequencies are not shown: they require daily portfolio returns, which are affected by nonsynchronous trading (see text). Weak-market windows are defined in Table~\\ref{tab:weak}.', cols='lrrrr')
# ---------------- weak-market episodes
MAC = 'XRev'
b = r'\textbf{Crit.} & \textbf{Window starts} & \textbf{$N$} & \textbf{Mkt. CAGR (\%)} & \textbf{Vol. (\%)} & \textbf{G$-$V (\% p.a.)} & \textbf{Monthly} & \textbf{Quarterly} & \textbf{Semiann.} & \textbf{Annual} \\'+'\n\\midrule\n'
for cname in ['C1', 'C2']:
    clab = cname
    for d in C['episodes'][cname]:
        rng = f"{d['first_start']:%b %Y}" if d['n'] == 1 else f"{d['first_start']:%b %Y}--{d['last_start']:%b %Y}"
        cells = [rng, f"{d['n']}", (n(d['mkt'][0]*100) if d['n'] == 1 else n(d['mkt'][0]*100)+' to '+n(d['mkt'][1]*100)), f"{d['vol']*100:.1f}", n(d['gv']*100)]
        for f in ['M', 'Q', 'H', 'A']:
            med, lo, hi, sh = d[f]; cells.append(n(med*100) if d['n'] == 1 else f"{n(med*100)} [{n(lo*100)}, {n(hi*100)}]")
        b += clab+' & '+' & '.join(cells)+r' \\'+'\n'; clab = ''
    b += '\\midrule\n'
b += r'China & Dec 2015 & 1 & $-$0.6$^{a}$ & 17.2$^{b}$ & $-$2.1 & 5.3 & 0.2 & 4.2 & 2.3 \\'
T['weak'] = wrap('Rotation in all U.S. weak-market windows of the same length as the China sample (111 months), 1928--2026.', 'tab:weak', b,
  'Notes: Windows are all '+str(len(C['win']))+' 111-month periods starting at a month end between December 1927 and the end of the data, selected only by the market criterion: C1 requires the annualized market return to be no higher than the Treasury-bill rate (no equity premium), and C2 a total-return CAGR of at most 3\\% (roughly flat in price terms). Consecutive qualifying start dates are grouped into episodes; $N$ is the number of windows. Vol.\\ is the median annualized volatility of monthly market returns and G$-$V the median annualized growth-minus-value log return. The last four columns give the median [min, max] across windows of Strong minus 50/50 in annualized log points (\\%). The last row reports China over 2016--2025 with the same metric. $^{a}$ Price return of the Shanghai Composite. $^{b}$ Volatility of daily returns.', cols='llrrrrrrrr')
# ---------------- costs
MAC = 'YRev'
sc = Dd['scen']
b = r'& \multicolumn{3}{c}{\textbf{U.S. (ETFs)}} & \multicolumn{4}{c}{\textbf{China}} \\ \cmidrule(lr){2-4}\cmidrule(lr){5-8}'+'\n'
b += r'\textbf{Component (bp unless stated)} & \textbf{Low} & \textbf{Base} & \textbf{High} & \textbf{Low} & \textbf{Base} & \textbf{High} & \textbf{Stocks} \\'+'\n\\midrule\n'
comp = [('Commission (per side)', 'comm'), ('Half bid--ask spread', 'half_spread'), ('Regulatory/exchange fees (per side)', 'reg'), ('Stamp duty, impact, other (per side)', 'other')]
for lbl, k in comp:
    b += lbl+' & '+' & '.join(n(sc[m][s][k], '{:.2f}') for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'+'\n'
b += 'Total one-way cost'+' & '+' & '.join(n(sum(sc[m][s][k] for _, k in comp), '{:.1f}') for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'+'\n'
b += 'Annual fund fee (\\% p.a., all strategies)'+' & '+' & '.join(n(sc[m][s]['fee'], '{:.2f}') for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'+'\n\\midrule\n'
R = Dd['res']
for f, fl in [('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly'), ('Q', 'Quarterly'), ('H', 'Semiannual'), ('A', 'Annual')]:
    b += f'{fl}: Strong net wealth'+' & '+' & '.join(n(R[(m, f, s)]['WS']) for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'+'\n'
b += '\\midrule\n'
b += 'Benchmark: market, net'+' & '+' & '.join(n(R[(m, 'M', s)]['WM']) for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'+'\n'
b += 'Benchmark: monthly 50/50, net'+' & '+' & '.join(n(R[(m, 'M', s)]['WE']) for m, ss in [('US', ['Low', 'Base', 'High']), ('CN', ['Low', 'Base', 'High', 'Stocks'])] for s in ss)+r' \\'
T['cost'] = wrap('Itemized implementation costs and net terminal wealth (initial 100, total returns).', 'tab:costmodel', b,
  'Notes: All values except the fund fee are in basis points of traded value per one-way trade; a switch is one sale plus one purchase. U.S. ETF prices are already net of fund expenses (0.04\\% p.a. for SPYG and SPYV and 0.0945\\% for SPY), so no additional fee is charged; the U.S. regulatory fee is the SEC Section~31 fee on sales averaged over both sides. The Chinese style series are indexes, so a tracking-fund fee (management plus custody) is charged to every strategy, the market benchmark included: 0.60\\% p.a. corresponds to the traditional 0.50\\% + 0.10\\% fee schedule of index ETFs and 0.20\\% to the reduced schedules introduced since 2023. ETF trades are assumed to be exempt from stamp duty. ``Stocks\'\' replicates the indexes with A-shares, paying the stamp duty on sales (0.1\\% before 28 August 2023 and 0.05\\% after) and an assumed 10 bp price impact, with no fund fee. U.S. results use total-return signals; China results use the base dividend scenario of Table~\\ref{tab:cn_div}. The 50/50 benchmark pays costs on its rebalancing trades.', cols='lrrrrrrr')
# ---------------- out-of-sample
MAC = 'YRev'
def p(x): return n(x*100, '{:.1f}')
b = r'& \textbf{China} & \textbf{U.S.} \\'+'\n\\midrule\n'
b += r'\multicolumn{3}{l}{\textit{(1) Select on 2016--2019, evaluate on 2020--2025 (net of base costs)}} \\'+'\n'
sp = {m: E[(m, 'split')] for m in ['CN', 'US']}
nm = lambda k: {'D': 'daily', 'W': 'weekly', 'M': 'monthly', 'Q': 'quarterly', 'H': 'semiannual', 'A': 'annual'}[k[1]]+' '+k[0]
b += 'Rule selected in 2016--2019 & '+nm(sp['CN']['best'])+' & '+nm(sp['US']['best'])+r' \\'+'\n'
b += 'CAGR of selected rule, 2020--2025 (\\%) & '+p(sp['CN']['test_cagr'])+' & '+p(sp['US']['test_cagr'])+r' \\'+'\n'
b += 'CAGR of monthly Strong, 2020--2025 (\\%) & '+p(sp['CN']['test_Mstrong'])+' & '+p(sp['US']['test_Mstrong'])+r' \\'+'\n'
b += 'CAGR of market / 50/50, 2020--2025 (\\%) & '+p(sp['CN']['test_M'])+' / '+p(sp['CN']['test_EW'])+' & '+p(sp['US']['test_M'])+' / '+p(sp['US']['test_EW'])+r' \\'+'\n\\midrule\n'
b += r'\multicolumn{3}{l}{\textit{(2) Walk-forward: each year choose the best Strong frequency or 50/50 so far, 2018--2025}} \\'+'\n'
wf = {m: E[(m, 'wf')] for m in ['CN', 'US']}
def ch(m):
    out = []
    for y, k in wf[m]['chosen']:
        out.append(('50/50' if k[0] == 'EW' else {'D': 'D', 'W': 'W', 'M': 'M', 'Q': 'Q', 'H': 'H', 'A': 'A'}[k[1]]))
    return ', '.join(out)
b += 'Choices 2018, \\dots, 2025 & '+ch('CN')+' & '+ch('US')+r' \\'+'\n'
b += 'Walk-forward CAGR / ARTV & '+p(wf['CN']['cagr'])+' / '+n(wf['CN']['artv'], '{:.2f}')+' & '+p(wf['US']['cagr'])+' / '+n(wf['US']['artv'], '{:.2f}')+r' \\'+'\n'
b += 'Market CAGR / ARTV & '+p(wf['CN']['M'])+' / '+n(wf['CN']['artvM'], '{:.2f}')+' & '+p(wf['US']['M'])+' / '+n(wf['US']['artvM'], '{:.2f}')+r' \\'+'\n'
b += '50/50 CAGR / ARTV & '+p(wf['CN']['EW'])+' / '+n(wf['CN']['artvEW'], '{:.2f}')+' & '+p(wf['US']['EW'])+' / '+n(wf['US']['artvEW'], '{:.2f}')+r' \\'+'\n'
b += 'Monthly Strong (hindsight) CAGR & '+p(wf['CN']['Mstrong'])+' & '+p(wf['US']['Mstrong'])+r' \\'+'\n\\midrule\n'
lt = E[('US', 'longtrain')]
b += r'\multicolumn{3}{l}{\textit{(3) U.S.: select on 1928--2015 book-to-market portfolios, evaluate on 2016--2025 ETFs}} \\'+'\n'
b += 'Rule selected in 1928--2015 & -- & '+nm(lt['best'])+r' \\'+'\n'
b += 'Net terminal wealth of selected rule / SPY / 50/50 & -- & '+f"{Dd['res'][('US','M','Base')]['WS']:.1f} / {Dd['res'][('US','M','Base')]['WM']:.1f} / {Dd['res'][('US','M','Base')]['WE']:.1f}"+r' \\'
T['oos'] = wrap('Pseudo out-of-sample evaluation.', 'tab:oos', b,
  'Notes: All returns and wealth values are net of the base-case costs of Table~\\ref{tab:costmodel} and use total returns (base dividend scenario for China). In (1), the rule (Strong or Weak) and frequency with the highest ARTV over 2016--2019 is selected and evaluated over 2020--2025. In (2), at each year-end from 2017 the strategy with the highest ARTV since 2016 among the six Strong frequencies and the 50/50 mix is held for the following calendar year; D, W, M, Q, H and A denote the Strong frequency chosen.', cols='lrr')
# ---------------- ETF vs index (full window, monthly data)
MAC = 'YRev'
F4 = ['M', 'Q', 'H', 'A']
b = r'& \textbf{Monthly} & \textbf{Quarterly} & \textbf{Semiann.} & \textbf{Annual} \\'+'\n\\midrule\n'
for lab, t in [('ETF', 'SPYG/SPYV ETFs (total return)'), ('Index', 'Book-to-market portfolios (non-investable indexes)')]:
    b += r'\multicolumn{5}{l}{\textit{'+t+r'}} \\'+'\n'
    b += ' 50/50 / Strong CAGR (\\%) & '+' & '.join(n(F[f][lab]['E']*100)+' / '+n(F[f][lab]['S']*100) for f in F4)+r' \\'+'\n'
    b += 'Strong minus 50/50 (pp) & '+' & '.join(n((F[f][lab]['S']-F[f][lab]['E'])*100, '{:.2f}') for f in F4)+r' \\'+'\n'
    b += 'Newey--West $t$ (Strong$-$Weak) & '+' & '.join(n(F[f][lab]['t'], '{:.2f}') for f in F4)+r' \\'+'\n'
    b += 'First-order autocorr. of $s_k$ & '+' & '.join(n(F[f][lab]['rho'], '{:.2f}') for f in F4)+r' \\'+'\n'
b += '\\midrule\nCorrelation of ETF and index spreads & '+' & '.join(n(F[f]['corr'], '{:.2f}') for f in F4)+r' \\'+'\n'
b += 'Same holding in both (\\% of periods) & '+' & '.join(n(F[f]['agree']*100) for f in F4)+r' \\'
T['etf'] = wrap('U.S. rotation with ETFs versus non-investable style indexes over the same window (31 December 2015 to 30 April 2025).', 'tab:etfidx', b,
  'Notes: Monthly data; ETF total-return indexes are sampled at month-ends. The index pair is the value-weighted bottom and top 30\\% book-to-market portfolios of Table~\\ref{tab:longus}. Daily and weekly frequencies are omitted because daily portfolio returns are affected by nonsynchronous trading.', cols='lrrrr')
for k, v in T.items(): open(f'{OUTD}/tab_{k}.tex', 'w').write(v)
print('\n'.join(T.keys()))
