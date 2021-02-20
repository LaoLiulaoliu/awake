#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from .OkexSpot import INSTRUMENT, print_error_or_get_order_id
from .Tool import Tool

RETRY = 10
TIME_PRECISION = 1000
HALF_HOUR = 1800000
VALUTA_IDX = 0


def place_buy_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY-5):
        r = spot.place_order('buy', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def place_sell_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY-1):
        r = spot.place_order('sell', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def get_open_buy_orders(spot):
    """place RETRY times, return open orders when success
    """
    for i in range(RETRY-2):
        r = spot.open_orders(INSTRUMENT[VALUTA_IDX])
        if 'error_code' not in r and len(r) > 0:
            return {i['order_id']: float(i['price']) for i in r if i['side'] == 'buy'}


def get_filled_buy_orders(spot, before=None):
    """ TODO !!! The maximum result is 100
    """
    for i in range(RETRY-3):
        r = spot.orders(2, INSTRUMENT[VALUTA_IDX], before)
        if 'error_code' not in r and len(r) > 0:
            return [(i['order_id'], float(i['price']), i['size']) for i in r if i['side'] == 'buy']


def place_buy_order_saveinfo(spot, tradeinfo, capital, last_price):
    """8 is ok system precision
       0 stands for open state
    """
    size = round(capital / last_price, 8)
    order_id = place_buy_order(spot, last_price, size)
    if order_id is not None:  # if no enough balance(usdt)
        tradeinfo.append([int(time.time() * TIME_PRECISION), last_price, size, order_id, 0])
        return True
    return False


def get_high_low_last(spot):
    for i in range(RETRY-4):
        r = spot.ticker(INSTRUMENT[VALUTA_IDX])
        if r:
            return (float(r['high_24h']),
                    float(r['low_24h']),
                    float(r['last']),
                    Tool.convert_time_str(r['timestamp'], TIME_PRECISION))


def pickup_leak_place_buy(low_24h, capital, spot, tradeinfo):
    low_precent = [low_24h * 0.01 * i for i in range(100, 70, -1)]
    pick_idx_by_hand = [2, 4, 6, 8, 10]
    for i in pick_idx_by_hand:
        place_buy_order_saveinfo(spot, tradeinfo, capital, low_precent[i])
    tradeinfo.flush()


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
    r = spot.ticker(INSTRUMENT[VALUTA_IDX])
    time.sleep(0.1)
    if r:
        if 'timestamp' not in r:
            print('timestamp not in r:', r)
            return
        timestamp = Tool.convert_time_str(r['timestamp'], TIME_PRECISION)
        last_price = float(r['last'])

        trend.append((timestamp, last_price))
        if last_price > high_hh:
            high_hh = last_price
        if last_price < low_hh:
            low_hh = last_price

        high_need_sort, low_need_sort = False, False
        # print(timestamp, trend.get_idx(last_half_hour_idx), last_half_hour_idx)
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


def have_around_open_orders(low, high, prices):
    print(low, high, prices)
    for p in prices:
        if low < p < high:
            return True
    return False

def have_around_filled_orders(low, high, trade):
    for trade_id, value in trade.items():
        if value[0] == 2 and value[3] == 0:  # filled, not pocket
            if low < value[1] < high:
                return True
    return False