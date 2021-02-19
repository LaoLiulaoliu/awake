#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from .OkexSpot import OkexSpot, INSTRUMENT, print_error_or_get_order_id
from .TradeInfo import TradeInfo


def place_buy_order(bid_price, size):
    """place 5 times, return order when success
    """
    order_id = None
    for i in range(5):
        r = spot.place_order('buy', INSTRUMENT, bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id

def get_high_low():
    for i in range(5):
        r = spot.ticker(INSTRUMENT)
        if r:    
            return float(r['high_24h']), float(r['low_24h'])

def 20210219(capital=200):
    spot = OkexSpot()
    tradeinfo = TradeInfo('TRADE.py')
    tradeinfo.load()

    trendinfo = {}
    begin_time = round(time.time() * 10)
    high_24h, low_24h = get_high_low()

    high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)] # math.log2(30) = 5
    low_precent = [low_24h * 0.01 * i for i in range(100, 70, -1)]
    low_precent_index = {}


    r = spot.ticker(INSTRUMENT)
    if r:
        timestamp = round(datetime.strptime(r['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * 10)
        last_price = float(r['last']
        trendinfo[timestamp] = {'last': last_price)}

        if last_price <= low_24h:
            for i in range(len(low_precent) - 1):
                if low_precent[i] < last_price < low_precent[i+1]:
                    if i not in low_precent_index or timestamp - low_precent_index[i] > 36000:
                        low_precent_index[i] = timestamp

                        order_id = place_buy_order(last_price, round(capital / last_price, 8))
                        tradeinfo.append([timestamp, last_price, INSTRUMENT, order_id])
                        break
        elif last_price > high_24h:
            pass
        else:
            pass