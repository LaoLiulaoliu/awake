#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from .OkexSpot import OkexSpot, INSTRUMENT, print_error_or_get_order_id
from .TradeInfo import TradeInfo


def place_order(bid_price, size):
    """place 5 times, return order when success
    """
    order_id = None
    for i in range(5):
        r = spot.place_order('buy', INSTRUMENT, bid_price, 1)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id

def get_high_low():
    for i in range(5):
        r = spot.ticker(INSTRUMENT)
        if r:    
            return float(r['high_24h']), float(r['low_24h'])

def 20210219():
    spot = OkexSpot()
    tradeinfo = TradeInfo('TRADE.py')
    tradeinfo.load()

    trendinfo = {}
    begin_time = round(time.time() * 10)
    high_24h, low_24h = get_high_low()
    high_precent, low_precent = high * 0.01, low * 0.01

    r = spot.ticker(INSTRUMENT)
    if r:
        timestamp = round(datetime.strptime(r['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * 10)
        last_price = float(r['last']
        trendinfo[timestamp] = {'last': last_price)}

        if last_price < low_24h:
            pass
        elif last_price > high_24h:
            pass
        else:
            pass