#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from functools import partial
from datetime import datetime
from .OkexSpot import OkexSpot, INSTRUMENT, print_error_or_get_order_id
from .Blaze import Blaze

RETRY = 5
TIME_PRECISION = 1000


def place_buy_order(spot, bid_price, size):
    """place 5 times, return order when success
    """
    for i in range(RETRY):
        r = spot.place_order('buy', INSTRUMENT, bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def place_sell_order(spot, bid_price, size):
    """place 5 times, return order when success
    """
    for i in range(RETRY):
        r = spot.place_order('sell', INSTRUMENT, bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def get_high_low(spot):
    for i in range(RETRY):
        r = spot.ticker(INSTRUMENT)
        if r:
            return float(r['high_24h']), float(r['low_24h'])


def pickup_leak_place_buy(low_24h, capital, spot, tradeinfo):
    low_precent = [low_24h * 0.01 * i for i in range(100, 70, -1)]
    pick_idx_by_hand = [2, 4, 6, 8, 10]
    for i in pick_idx_by_hand:
        size = round(capital / low_precent[i], 8)
        order_id = place_buy_order(spot, low_precent[i], size)
        tradeinfo.append([int(time.time() * TIME_PRECISION), low_precent[i], size, INSTRUMENT, order_id])


def get_high_low_half_hour(begin_time, iterator):
    idx = -1
    high_hh, low_hh = 0, 100000000
    for i, data in iterator:
        timestamp, price = data
        if begin_time - timestamp < 1800 * TIME_PRECISION:
            if price > high_hh:
                high_hh = price
            if price < low_hh:
                low_hh = price
            idx = i
        else:
            break
    if idx > 0:
        return high_hh, low_hh, idx


def r20210219(capital=200):
    spot = OkexSpot(trade=True)
    tradeinfo = Blaze('TRADE.py', 5)
    tradeinfo.load()

    high_24h, low_24h = get_high_low(spot)

    begin_time = int(time.time() * TIME_PRECISION)
    last_half_hour_idx = -1
    trend = Blaze('TREND.txt', 2)
    r = trend.reload(partial(get_high_low_half_hour, begin_time))
    high_hh, low_hh, last_half_hour_idx = r if r else (high_24h, low_24h, last_half_hour_idx)
    # high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5    # high_precent_index = {}

    pickup_leak_place_buy(low_24h, capital, spot, tradeinfo)
    while True:
        r = spot.ticker(INSTRUMENT)
        if r:
            timestamp = int(datetime.strptime(r['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * TIME_PRECISION)
            last_price = float(r['last'])
            trend.append((timestamp, last_price))

            if last_price > high_hh:
                high_hh = last_price
            if last_price < low_hh:
                low_hh = last_price

            if last_price < low_24h:
                pass
            elif last_price > high_24h:
                pass
            else:
                pass
