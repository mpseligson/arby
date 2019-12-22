#
# Copywrite 2017 Matthew Seligson
#

from helpers import pricer
import time
from pprint import pprint

#
# Find arbitrage opportunities by getting pricing data from each exchange, then
# for each coin finding min and max price and computing percentage diff. 
#

exchanges = ['kraken', 'bittrex', 'binance', 'poloniex', 'bitstamp']

# init pricers for each exchange
bi = pricer.BinancePricer()
pl = pricer.PoloniexPricer()
b = pricer.BittrexPricer()
p = pricer.BitstampPricer()
k = pricer.KrakenPricer()

data = {}

# every 10 seconds compute new diffs
while True:
    data['kraken'] = k.update()
    data['bittrex'] = b.update()
    data['binance'] = bi.update()
    data['poloniex'] = pl.update()
    data['bitstamp'] = p.update()

    diffs = set()
    all_coins = set(data['kraken'].keys()).union(set(data['bittrex'].keys()), set(data['binance'].keys()), set(data['poloniex'].keys()), set(data['bitstamp'].keys()))
    
    # for each coin find the min and max price and the associated exchanges
    for coin in all_coins:
        minPrice = None
        maxPrice = None
        minPriceExchange = None
        maxPriceExchange = None
        for exchange in exchanges:
            if coin in data[exchange]:
                price = data[exchange][coin]

                # if price is 0 or None the coin is listed but not tradable
                if (price == 0 or price is None):
                    continue
                if (minPrice is None or price < minPrice):
                    minPrice = price
                    minPriceExchange = exchange
                if (maxPrice is None or price > maxPrice):
                    maxPrice = price
                    maxPriceExchange = exchange

            # if min and max come from different exchanges, we've found a price discrepancy
            if (minPriceExchange is not None and minPriceExchange is not maxPriceExchange):
                diffs.add(((maxPrice/minPrice - 1)*100, minPrice, maxPrice, minPriceExchange, maxPriceExchange, coin))
    
    diffs = list(diffs)

    diffs.sort(key=lambda tup: tup[0])
    for diff in diffs:
        print("Diff = %s%% for %s between %s and %s (minPrice = %s, maxPrice = %s)" % (str(diff[0])[0:7], diff[5], diff[3], diff[4], str(diff[1])[0:9], str(diff[2])[0:9]))

    time.sleep(10)