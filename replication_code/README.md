# Replication code

Reproduces every table and figure in "Momentum-Driven Growth–Value Style Rotation Across Multiple Rebalancing Frequencies".

Place this folder inside the dataset repository (so `SPY_D.csv` and `SSE_VG.csv` sit one level up), or set `DATA_DIR` to the folder holding them. Only the daily files' price columns are used.

```
pip install pandas numpy scipy matplotlib
python full.py      # main metrics + inference (writes results.pkl; about 5 min, bootstrap)
python robust.py    # costs, sub-periods, look-back, descriptive stats (writes robust.pkl)
python tables.py    # LaTeX tables tab_*.tex
python figs.py      # Figure1.png ... Figure5.png
```

Random seeds are fixed (numpy default_rng(20261001)), so bootstrap and random-rotation results are reproducible.

## Revision (round 1) analyses

Additional data in `revision_data/`:

* `spdr-etf-historical-distributions.xlsx` — State Street's official SPDR distribution workbook (downloaded 4 Nov 2026).
* `US_dividends.csv` — SPY, SPYG and SPYV distributions extracted from it (income + capital gains; amounts before the Oct 2017 4-for-1 split of SPYG/SPYV divided by 4).
* `french/` — Kenneth R. French Data Library files (CRSP 202609 vintage): `Portfolios_Formed_on_BE-ME.csv`, `Portfolios_Formed_on_BE-ME_Wout_Div.csv`, `F-F_Research_Data_Factors.csv`, `F-F_Research_Data_Factors_daily.csv`.
* `ff_bm_terciles.csv`, `ff_market_rf_us.csv` — 1971–2021 daily snapshot (FFresearch R package), used only for the remark on daily portfolio data (`rev_c_longus.py`).

```
python rev_a_dividends.py      # total returns: U.S. distributions, China yield scenarios
python rev_b_subperiods.py     # anatomy of the sub-period variation (Table 13, Figure 6)
python rev_c2_longus.py        # U.S. 1928-2026, rolling 111-month windows, weak-market episodes (Tables 14-15, Figure 7)
python rev_c_longus.py         # 1971-2021 daily snapshot (daily/weekly remark only)
python rev_d_costs.py          # itemized cost model (Table 17)
python rev_e_oos.py            # split-sample, walk-forward and long-history training (Table 18)
python rev_f2_instruments.py   # ETFs vs. book-to-market indexes, 2016-2025 (Table 16)
python rev_tables.py <outdir>  # LaTeX tables of the revision
python rev_figs.py <outdir>    # Figure6.png, Figure7.png
```
The scripts expect `SPY_D.csv` and `SSE_VG.csv` one level up (or `DATA_DIR`), as for the original scripts.
