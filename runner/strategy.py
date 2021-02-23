#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from .OkexSpot import INSTRUMENT, print_error_or_get_order_id
from .Tool import Tool
from .const import VALUTA_IDX, TIME_PRECISION, RETRY


def place_buy_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY - 5):
        r = spot.place_order('buy', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id
        time.sleep(0.01)


def place_sell_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY - 1):
        r = spot.place_order('sell', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id
        time.sleep(0.01)


def get_open_buy_orders(spot):
    """place RETRY times, return open orders when success
    """
    for i in range(RETRY - 2):
        r = spot.open_orders(INSTRUMENT[VALUTA_IDX])
        if 'error_code' not in r and len(r) > 0:
            return {i['order_id']: float(i['price']) for i in r if i['side'] == 'buy'}
        time.sleep(0.01)


def get_filled_buy_orders(spot, before=None):
    """ TODO !!! The maximum result is 100
    """
    for i in range(RETRY - 3):
        r = spot.orders(2, INSTRUMENT[VALUTA_IDX], before)
        if 'error_code' not in r and len(r) > 0:
            return [(i['order_id'], float(i['price']), i['size']) for i in r if i['side'] == 'buy']
        time.sleep(0.01)


def place_buy_order_saveinfo(spot, tradeinfo, capital, last_price):
    """8 is ok system precision
       0 stands for open state
    """
    size = round(capital / last_price, 8)
    buy_order_id = place_buy_order(spot, last_price, size)
    if buy_order_id is not None:  # if no enough balance(usdt)
        tradeinfo.append([int(time.time() * TIME_PRECISION), last_price, size, buy_order_id, 0, 0])
        return True
    return False


def get_high_low_lastest(spot):
    for i in range(RETRY - 4):
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
