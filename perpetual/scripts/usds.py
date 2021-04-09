
# d for coin futures, f for usd s futures
from binance_d import RequestClient
from binance_d.constant.test import *
from binance_d.base.printobject import *
from datetime import datetime, timedelta

g_api_key='eJBYUpKfnUCA5wXDfJTKGPNaOoyLtnXIb9D6GKFbnABLCndVRRYJrdyI9rMi6D54'
g_secret_key='970sbCiGtH1W4rPW56I4MBbD9brKZegyveedljt3U3D5hry7zMbxa4sxacA80kUv'
request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)

epoch = datetime.utcfromtimestamp(0)
def dt_from_ms(ms):
    return datetime.utcfromtimestamp(ms / 1000.0)

def dt_to_ms(dt):
    delta = dt - epoch
    return int(delta.total_seconds() * 1000)

def get_pairs():
	result = request_client.get_exchange_information()
	symbols = list(map(lambda x: x.symbol, result.symbols))



def get_funding_rate(pair, start_date, end_date, limit=1000):

	start_year, start_month, start_day = int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8])
	end_year, end_month, end_day = int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8])
	start_date = dt_to_ms(datetime(start_year, start_month, start_day))
	end_date = dt_to_ms(datetime(end_year, end_month, end_day))
	result = request_client.get_funding_rate(symbol=pair, startTime=start_date, endTime=end_date, limit=limit)