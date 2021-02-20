#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from functools import partial
from .OkexSpot import OkexSpot, INSTRUMENT, print_error_or_get_order_id
from .Blaze import Blaze
from .Tool import Tool

RETRY = 5
TIME_PRECISION = 1000
HALF_HOUR = 1800000


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


def get_high_low_last(spot):
    for i in range(RETRY):
        r = spot.ticker(INSTRUMENT)
        if r:
            return (float(r['high_24h']),
                    float(r['low_24h']),
                    float(r['last']),
                    Tool.convert_time_str(r['timestamp'], TIME_PRECISION))


def pickup_leak_place_buy(low_24h, capital, spot, tradeinfo):
    low_precent = [low_24h * 0.01 * i for i in range(100, 70, -1)]
    pick_idx_by_hand = [2, 4, 6, 8, 10]
    for i in pick_idx_by_hand:
        size = round(capital / low_precent[i], 8)
        order_id = place_buy_order(spot, low_precent[i], size)
        print([int(time.time() * TIME_PRECISION), low_precent[i], size, INSTRUMENT, order_id])
        tradeinfo.append([int(time.time() * TIME_PRECISION), low_precent[i], size, INSTRUMENT, order_id])


def get_high_low_half_hour(begin_time, iterator):
    idx = -1
    high_hh, low_hh = 0, 100000000
    for i, data in iterator:
        timestamp, price = data
        if begin_time - timestamp < HALF_HOUR:
            if price > high_hh:
                high_hh = price
            if price < low_hh:
                low_hh = price
            idx = i
        else:
            break
    if idx > 0:
        return high_hh, low_hh, idx


def first_half_hour_no_bid(spot, trend, last_price_init):
    high_hh, low_hh = last_price_init, last_price_init
    last_half_hour_idx = 0

    while True:
        r = trace_trend(spot, trend, last_half_hour_idx, high_hh, low_hh)
        if r is not None:
            last_half_hour_idx, high_hh, low_hh = r
            if last_half_hour_idx > 0:
                break


def trace_trend(spot, trend, last_half_hour_idx, high_hh, low_hh):
    r = spot.ticker(INSTRUMENT)
    if r:
        timestamp = Tool.convert_time_str(r['timestamp'], TIME_PRECISION)
        last_price = float(r['last'])

        print((timestamp, last_price))
        trend.append((timestamp, last_price))
        if last_price > high_hh:
            high_hh = last_price
        if last_price < low_hh:
            low_hh = last_price

        high_need_sort, low_need_sort = False, False
        print(timestamp, trend.get_idx(last_half_hour_idx), last_half_hour_idx)
        while timestamp - trend.get_idx(last_half_hour_idx)[0] > HALF_HOUR:
            if Tool.float_close(high_hh, trend.get_idx(last_half_hour_idx)[1]):
                high_need_sort = True
            elif Tool.float_close(low_hh, trend.get_idx(last_half_hour_idx)[1]):
                low_need_sort = True
            last_half_hour_idx += 1

        if high_need_sort:
            high_hh = sorted([i[1] for i in trend.get_range(last_half_hour_idx)])[-1]
        if low_need_sort:
            low_hh = sorted([i[1] for i in trend.get_range(last_half_hour_idx)])[0]
        return last_half_hour_idx, high_hh, low_hh


def r20210219(capital=200):
    spot = OkexSpot(use_trade_key=True)
    tradeinfo = Blaze('TRADE.py', 5)
    tradeinfo.load()

    high_24h, low_24h, last_price_init, begin_time = get_high_low_last(spot)
    pickup_leak_place_buy(low_24h, capital, spot, tradeinfo)

    trend = Blaze('TREND.txt', 2)
    r = trend.custom_reload(partial(get_high_low_half_hour, begin_time))
    if r:
        high_hh, low_hh, last_half_hour_idx = r
    else:  # empty trend file or expired trend file
        print('init append', begin_time, last_price_init)
        trend.append((begin_time, last_price_init))
        high_hh, low_hh, last_half_hour_idx = last_price_init, last_price_init, 0
        first_half_hour_no_bid(spot, trend, last_price_init)

    # high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5    # high_precent_index = {}
    while True:
        while True:
            r = trace_trend(spot, trend, last_half_hour_idx, high_hh, low_hh)
            if r is not None:
                last_half_hour_idx, high_hh, low_hh = r

                timestamp, last_price = trend.last()
                if low_24h < last_price < high_24h:
                    pass
