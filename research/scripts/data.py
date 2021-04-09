# d for coin futures, f for usd s futures
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import requests as re
import pandas as pd
import numpy as np

import multiprocessing

COIN_API = 'https://dapi.binance.com'
USD_API = 'https://fapi.binance.com'
SPOT_API = 'https://api.binance.com'
g_api_key='eJBYUpKfnUCA5wXDfJTKGPNaOoyLtnXIb9D6GKFbnABLCndVRRYJrdyI9rMi6D54'
g_secret_key='970sbCiGtH1W4rPW56I4MBbD9brKZegyveedljt3U3D5hry7zMbxa4sxacA80kUv'
headers = {"Accept": "application/json"}

epoch = datetime.utcfromtimestamp(0)
def dt_from_ms(ms):
    return datetime.utcfromtimestamp(int(ms / 1000.0))

def dt_to_ms(dt):
    delta = dt - epoch
    return int(delta.total_seconds() * 1000)

def get_pairs(isCoin, isSpot=False):
    if isSpot:
        suff = '/api/v3/exchangeInfo'
        url = SPOT_API
        result = re.get(url+suff, headers=headers)
        symbolObjs = result.json()['symbols']
        symbolObjs = list(filter(lambda x: x['symbol'][-4:] == 'USDT', symbolObjs))
        symbolObjs = [x['symbol'] for x in symbolObjs]
        return {'spot': symbolObjs}
    else:
        suff = '/dapi/v1/exchangeInfo' if isCoin else '/fapi/v1/exchangeInfo'
        url = COIN_API if isCoin else USD_API
        result = re.get(url+suff, headers=headers)
        symbolObjs = result.json()['symbols']
        symbols = [x['symbol'] for x in symbolObjs]
        perpetuals = list(filter(lambda x: 'PERP' in x, symbols))
        futures = list(filter(lambda x: 'PERP' not in x, symbols))
        return {'perpetuals': perpetuals, 'futures': futures}

def get_funding_rate(isCoin, pair, start_date, end_date, limit=1000):
    start_year, start_month, start_day = int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8])
    end_year, end_month, end_day = int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8])
    start_date = dt_to_ms(datetime(start_year, start_month, start_day))
    end_date = dt_to_ms(datetime(end_year, end_month, end_day))
    suff = '/dapi/v1/fundingRate' if isCoin else '/fapi/v1/fundingRate'
    suff += '?symbol='+pair+'&startTime='+str(start_date)+'&endTime='+str(end_date)+'&limit='+str(limit)
    url = COIN_API if isCoin else USD_API
    result = re.get(url+suff, headers=headers)
    data = result.json()
    funding_rate, funding_time = [], []
    for funding in data:
        funding_rate.append(float(funding['fundingRate'])*100)
        funding_time.append(dt_from_ms(funding['fundingTime']))
    df = pd.DataFrame({'Time':funding_time,'Rate':funding_rate})
    df['Time'] = pd.to_datetime(df['Time'])
    df.set_index('Time',inplace=True)
    return df

def get_kline_data(isCoin, pair, start_date, end_date, limit=1500, interval='1h', isSpot=False, save=False, fpath=""):
    start_year, start_month, start_day = int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8])
    end_year, end_month, end_day = int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8])
    start_date = dt_to_ms(datetime(start_year, start_month, start_day))
    end = dt_to_ms(datetime(end_year, end_month, end_day))
    # query from start_date to end_date
    dfs = []
    if interval == '1h':
        time_step = 1*60*60*1000
    elif interval == '1m':
        time_step = 1*60*1000
    elif interval == '1d':
        time_step = 1*24*60*60*1000
    end_date = start_date-time_step
    while (end_date < end):
        start_date = end_date + time_step
        end_date = start_date + (limit-500)*time_step
        if end_date >= end:
            end_date = end
        suff = '/dapi/v1/klines' if isCoin else '/fapi/v1/klines'
        suff = suff if not isSpot else '/api/v3/klines'
        suff += '?symbol='+pair+'&startTime='+str(start_date)+'&endTime='+str(end_date)+'&limit='+str(limit)+'&interval='+interval
        url = COIN_API if isCoin else USD_API
        url = url if not isSpot else SPOT_API
        result = re.get(url+suff, headers=headers)
        data = result.json()
        closePrice, time = [], []
        for ohlc in data:
            closePrice.append(float(ohlc[4]))
            time.append(dt_from_ms(ohlc[0]))
        df = pd.DataFrame({'Time':time,pair:closePrice})
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index('Time',inplace=True)
        dfs.append(df)
    df_i = dfs[0]
    for df in dfs[1:]:
        df_i = df_i.append(df)
    if save:
        df_i.to_csv(fpath+pair+'.csv')
    return df_i

if __name__ == '__main__':
    coins = get_pairs(False, isSpot=True)['spot']
    start_date, end_date = '20180101','20210408'
    args = []
    for coin in coins:
        args.append((False, coin, start_date, end_date, 1500, '1h', True, True, '../data/spot/'))

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(get_kline_data, args)
    #for coin in coins[:5]:
    #    f = get_kline_data(False, coin, start_date, end_date, 1500, '1h',True)