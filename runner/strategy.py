#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
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
        order_id = place_buy_order(spot, low_precent[i], round(capital / low_precent[i], 8))
        tradeinfo.append([round(time.time() * TIME_PRECISION), low_precent[i], INSTRUMENT, order_id])


def r20210219(capital=200):
    spot = OkexSpot(trade=True)
    tradeinfo = Blaze('TRADE.py')
    tradeinfo.load()

    trend = []
    begin_time = round(time.time() * TIME_PRECISION)
    high_24h, low_24h = get_high_low(spot)
    high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5
    high_precent_index = {}

    pickup_leak_place_buy(low_24h, capital, spot, tradeinfo)

    r = spot.ticker(INSTRUMENT)
    if r:
        timestamp = round(datetime.strptime(r['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * TIME_PRECISION)
        last_price = float(r['last'])
        trend.append((timestamp, last_price))

        if last_price <= low_24h:
            pass
        elif last_price > high_24h:
            pass
        else:
            pass
