# d for coin futures, f for usd s futures
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import requests as re
import pandas as pd
import numpy as np
import os
from functools import reduce
import statsmodels as stm
import multiprocess as mp
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm

COIN_API = 'https://dapi.binance.com'
USD_API = 'https://fapi.binance.com'
SPOT_API = 'https://api.binance.com'
g_api_key='eJBYUpKfnUCA5wXDfJTKGPNaOoyLtnXIb9D6GKFbnABLCndVRRYJrdyI9rMi6D54'
g_secret_key='970sbCiGtH1W4rPW56I4MBbD9brKZegyveedljt3U3D5hry7zMbxa4sxacA80kUv'
headers = {"Accept": "application/json"}

fpath = './data/spot'
files = os.listdir(fpath)
files = list(filter(lambda x: ('BULL' not in x) and ('BEAR' not in x) and ('UP' not in x) and ('DOWN' not in x), files))

dfs = [pd.read_csv(fpath+'/'+x).set_index('Time') for x in files]
df = reduce(lambda x,y: x.join(y, how='outer'), dfs)
returns = df.pct_change(1)
coins = returns.columns

coins1 = coins
#coins1 = ['BTCUSDT','ETHUSDT','LTCUSDT','BCHUSDT','BNBUSDT','XRPUSDT','DOTUSDT','ADAUSDT','LINKUSDT','THETAUSDT']
sample_n = 90

def pairs_trading_calc(coiny, coinx):
    pairs_df = {'Coin1':[],'Coin2':[],'Beta':[],'R2':[],'Tstat':[],'ADF':[],'ADFPValue':[],'Lags':[],'Results':[]}
    regData = df[[coiny, coinx]].dropna().tail(sample_n*24)
    if regData.empty:
        return None
    y = regData[[coiny]]
    x = regData[[coinx]]
    model = sm.OLS(y,x)
    results = model.fit()
    beta = results.params[coinx]
    r2 = results.rsquared
    tstat = results.tvalues[coinx]
    (adf, pvalue, lags, ) = stm.tsa.stattools.adfuller(results.resid)[0:3]
    pairs_df['Coin1'].append(coiny)
    pairs_df['Coin2'].append(coinx)
    pairs_df['Beta'].append(beta)
    pairs_df['R2'].append(r2)
    pairs_df['Tstat'].append(tstat)
    pairs_df['ADF'].append(adf)
    pairs_df['ADFPValue'].append(pvalue)
    pairs_df['Lags'].append(lags)
    pairs_df['Results'].append(results)
    pairs_df = pd.DataFrame(pairs_df)
    pairs_df.to_csv('./results/pairs/'+coiny+'-'+coinx+'.csv')

def get_pairs():
    coin_pairs = []
    for i in range(len(coins1)):
        for j in range(i+1,len(coins1)):
            coin_pairs.append((coins1[i],coins1[j]))
    return coin_pairs

if __name__ == '__main__':
	coin_pairs = get_pairs()
	with mp.Pool(4) as pool:
		pool.starmap(pairs_trading_calc, coin_pairs)
