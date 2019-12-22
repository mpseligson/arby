#
# Copywrite 2017 Matthew Seligson
#

from bitstampy import api
from decimal import *
from pprint import pprint
from bittrex.bittrex import Bittrex, API_V2_0
from poloniex import Poloniex
from binance.client import Client
import datetime
import time
import pusherclient
import sys
import json
import krakenex
import json

#
# For each cryptocurrency exchange, build a Pricer class with an update()
# function that returns a dictionary of 'COIN' --> price pairs. 
#

sys.path.append('..')

class BitstampPricer:

    # coins of interest on Bitstamp
    coins = ['BTC','ETH','LTC','XRP','BCH']
    v = dict.fromkeys(coins)

    def __init__(self):
        self.init_pusher()

    # load secret key from bitstamp.key file
    def load_keys(self):
        keys = {}
        with open('bitstamp.key') as file:
            lines = file.read().splitlines() 
            for line in lines:
                key, value = line.partition(" = ")[::2]
                keys[key.strip()] = value
        return keys

    # initiliaze pusher client
    def init_pusher(self):
        keys = self.load_keys()
        self.pusher = pusherclient.Pusher(keys['PusherKey'])
        self.pusher.connection.bind('pusher:connection_established', self.connect_handler)
        self.pusher.connect()

    def store(self,price,coin):
        self.v[coin] = price

    # update price of coin in dictionary on new trade event
    def connect_handler(self,data):
        for c in self.coins:
            str = ''
            if (c != 'BTC'):
                str = '_' + c.lower() + 'usd'
            channel = self.pusher.subscribe("live_trades" + str)
            def channel_callback(data, j=c):
                data = json.loads(data)
                price = Decimal(data['price_str'].strip())
                self.store(price,j)
            channel.bind('trade', channel_callback)

    # return dictionary of coin --> price pairs
    def update(self):
        return self.v

class KrakenPricer:

    # coins of interest on Kraken
    coins = ['BTC','ETH','XRP','LTC','ETC','BCH','DASH','XMR','ZEC','USDT']
    v = dict.fromkeys(coins)
    k = krakenex.API()

    # return dictionary of coin --> price pairs
    def update(self):
        def match(x):
            return {
                'XBTUSD':'BTC',
                'ETHUSD':'ETH',
                'XRPUSD':'XRP',
                'LTCUSD':'LTC',
                'ETCUSD':'ETC',
                'BCHUSD':'BCH',
                'DASHUSD':'DASH',
                'XMRUSD':'XMR',
                'ZECUSD':'ZEC',
                'USDTZUSD':'USDT',
                'XETCZUSD':'ETC',
                'XETHZUSD':'ETH',
                'XLTCZUSD':'LTC',
                'XXBTZUSD':'BTC',
                'XXMRZUSD':'XMR',
                'XXRPZUSD':'XRP',
                'XZECZUSD':'ZEC'
            }[x]

        response = self.k.query_public('Ticker', {'pair': 'XBTUSD,ETHUSD,XRPUSD,LTCUSD,ETCUSD,BCHUSD,DASHUSD,XMRUSD,ZECUSD,USDTUSD'})
        retval = {}
        for key in response['result'].keys():
            price = Decimal(response['result'][key]['c'][0])
            retval[match(key)] = price
        return retval

class BittrexPricer:

    # return dictionary of coin --> price pairs
    def update(self):
        b = Bittrex(None, None, api_version='v1.1')  # or defaulting to v1.1 as Bittrex(None, None)
        dat = b.get_market_summaries()['result']
        btcusd = 0
        v = {}
        for market in dat:
            name = market['MarketName']
            if (name == 'USDT-BTC'):
                btcusd = market['Last']

        for market in dat:
            name = market['MarketName']
            if (name[0:3] == 'BTC' and name[4:] != '1ST' and name[4:] != '2GIVE'):
                if (name[4:] == 'BCC'):
                    v['BCH'] = market['Last']*btcusd
                else:
                    v[name[4:]] = market['Last']*btcusd

        retval = {}
        for key in v:
            price = v[key]
            retval[key] = Decimal(price)

        return retval

class PoloniexPricer:

    # return dictionary of coin --> price pairs
    def update(self):
        polo = Poloniex()
        dat = polo.returnTicker()
        btcusd = 0
        v = {}
        for market in dat:
            if (market == 'USDT_BTC'):
                btcusd = Decimal(dat[market]['last'].strip())

        for market in dat:
            name = market
            if (name[0:3] == 'BTC' and name[4:] != '1ST' and name[4:] != '2GIVE'):
                if (name[4:] == 'BCC'):
                    v['BCH'] = Decimal(dat[market]['last'].strip())*btcusd
                else:
                    v[name[4:]] = Decimal(dat[market]['last'].strip())*btcusd
            
        retval = {}
        for key in v:
            price = v[key]
            retval[key] = price
        
        return retval

class BinancePricer:

    def __init__(self):
        keys = self.load_keys()
        self.client = Client(keys['Key'], keys['Secret'])

    def load_keys(self):
        keys = {}
        with open('binance.key') as file:
            lines = file.read().splitlines() 
            for line in lines:
                key, value = line.partition(" = ")[::2]
                keys[key.strip()] = value
        return keys

    # return dictionary of coin --> price pairs
    def update(self):
        btcusd = 0
        v = {}
        dat = self.client.get_all_tickers()
        for market in dat:
            if (market['symbol'] == 'BTCUSDT'):
                btcusd = Decimal(market['price'].strip())

        for market in dat:
            name = market['symbol']
            if (name[-3:] == 'BTC'):
                name = name[:-3]
                if (name == 'BCC'):
                    v['BCH'] = Decimal(market['price'].strip())*btcusd
                else:
                    v[name] = Decimal(market['price'].strip())*btcusd

        retval = {}

        for key in v:
            price = v[key]
            retval[key] = price

        return retval
































