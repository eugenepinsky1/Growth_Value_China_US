import pandas as pd, numpy as np
import os
D=os.environ.get('DATA_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))+os.sep
def load(mkt,freq):
    fn={'US':{'D':'SPY_D','W':'SPY_W','M':'SPY_M','Q':'SPY_Q','H':'SPY_H','A':'SPY_A'},
        'CN':{'D':'SSE_VG','W':'SSE_W','M':'SSE_M','Q':'SSE_Q','H':'SSE_H','A':'SSE_A'}}[mkt][freq]
    df=pd.read_csv(D+fn+'.csv',encoding='utf-8-sig')
    df['Date']=pd.to_datetime(df['Date'],format='%m/%d/%y')
    if mkt=='US': df=df.rename(columns={'SPY':'MP','SPYG':'GP','SPYV':'VP','Y':'rM','G':'rG','V':'rV'})
    else: df=df.rename(columns={'SSEC':'MP','GPrice':'GP','VPrice':'VP','SS':'rM','G':'rG','V':'rV'})
    return df.sort_values('Date').reset_index(drop=True)
