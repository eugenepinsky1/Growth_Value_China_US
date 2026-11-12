"""Writes the rows of the data-snooping table (Table 8) from rev_g.pkl (produced by rev_g_spa.py)."""
import pickle, sys
OUT = pickle.load(open('rev_g.pkl', 'rb'))
FN = {'D': 'daily', 'W': 'weekly', 'M': 'monthly', 'Q': 'quarterly', 'H': 'semiannual', 'A': 'annual'}
def name(s):
    r, f, L = s.split(); x = f'{r} {FN[f]}'
    return x if L == 'L1' else x + f' ($L={L[1:]}$)'
rows = []
for m, mk in [('CN', 'China'), ('US', 'U.S.')]:
    for v, vl in [('gross', 'Gross, price returns'), ('net', 'Net of base costs, total returns')]:
        for b, bl in [('50/50', '50/50 mix'), ('Market', 'market')]:
            o = OUT[(m, v, b)]; r = o['res']; c = [r[k]['consistent'] for k in (5, 21, 63)]
            sup = ', '.join(name(s).replace('Strong ', '').replace('Weak ', '') + (' Strong' if 'Strong' in s else ' Weak') for s in o['superior']) or 'none'
            rows.append(f"{mk} & {vl} & {bl} & {name(o['best'])} & {100*o['best_mean_pa']:.1f} & {r[21]['upper']:.3f} & {r[21]['consistent']:.3f} & {min(c):.3f}--{max(c):.3f} & {sup} \\\\")
out = '\n'.join(rows); print(out)
if len(sys.argv) > 1: open(sys.argv[1], 'w').write(out + '\n')
