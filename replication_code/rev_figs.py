import pickle, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import sys
OUTD = sys.argv[1]
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'DejaVu Sans'})
INK, MUT, GRID = '#1f1f1e', '#6b6a64', '#e4e3dd'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
b = pickle.load(open('rev_b.pkl', 'rb')); c = pickle.load(open('rev_c2.pkl', 'rb'))
# ---- Figure 6: China sub-period anatomy
yr = b['CN']['yr']; roll = b['CN']['roll']
fig, ax = plt.subplots(1, 2, figsize=(10, 3.3))
a = ax[0]
cols = [BLUE if y <= 2019 else ORANGE for y in yr.year]
a.bar(yr.year, 100*yr.lx, color=cols, width=0.7)
a.axhline(0, color=MUT, lw=0.8)
a.set_ylabel('Strong minus 50/50 (log points, %)')
a.set_title('(a) Annual contribution, monthly rotation', loc='left', fontsize=9)
a2 = a.twinx(); a2.plot(yr.year, 100*yr.sig, color=INK, marker='o', ms=3.5, lw=1.2)
a2.set_ylabel('Volatility of monthly G$-$V spread\n(annualized, %, line)', color=INK); a2.spines['top'].set_visible(False)
a.set_xticks(yr.year); a.set_xticklabels([str(y) if y < 2025 else "2025*" for y in yr.year], rotation=45)
a.text(2016.2, 100*yr.lx.max()*0.5, '2016–2019', color=BLUE, fontsize=8); a.text(2021.0, 100*yr.lx.max()*1.03, '2020–2025', color=ORANGE, fontsize=8)
a.yaxis.grid(True, color=GRID); a.set_axisbelow(True)
a = ax[1]
a.plot(roll.index, 100*roll.values, color=BLUE, lw=1.5)
a.axhline(0, color=MUT, lw=0.8)
a.set_ylabel('Annualized log excess over 50/50 (%)')
a.set_title('(b) Rolling 36-month advantage of monthly Strong', loc='left', fontsize=9)
a.yaxis.grid(True, color=GRID); a.set_axisbelow(True)
fig.tight_layout(); fig.savefig(f'{OUTD}/Figure6.png', dpi=300)
# ---- Figure 7: U.S. long-history rolling windows (same length as the China sample)
W = c['win']
fig, ax = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
for a, f, lab in [(ax[0], 'M', 'monthly'), (ax[1], 'Q', 'quarterly')]:
    a.plot(W.end, 100*W[f+'_gap'], color=BLUE, lw=1.3, label='U.S. 111-month windows (1928–2026)')
    for flag, colr, nm in [('C1', '#f2c6a8', 'weak market: no equity premium (C1)')]:
        m = W[flag].values
        a.fill_between(W.end, -8, 12, where=m, color=colr, alpha=0.6, lw=0, label=nm)
    a.axhline(0, color=MUT, lw=0.8)
    a.axhline(100*b['CN']['tot_pa'] if f == 'M' else np.nan, color=ORANGE, ls='--', lw=1.2, label='China 2016–2025 (monthly)')
    a.axhline(100*b['US']['tot_pa'] if f == 'M' else np.nan, color=INK, ls=':', lw=1.2, label='U.S. ETFs 2016–2025 (monthly)')
    a.set_ylim(-7, 11); a.set_title(f'({"a" if f=="M" else "b"}) Strong minus 50/50, {lab} rebalancing', loc='left', fontsize=9)
    a.set_xlabel('Window end'); a.yaxis.grid(True, color=GRID); a.set_axisbelow(True)
ax[0].set_ylabel('Annualized log excess (%)')
h, l = ax[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=7.5, frameon=False, loc='lower center', ncol=4)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(f'{OUTD}/Figure7.png', dpi=300)
print('ok')
