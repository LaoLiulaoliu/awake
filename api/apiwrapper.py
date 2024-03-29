#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
from .OkexSpotV3 import print_error_or_get_order_id, OkexSpotV3
from ruler.Tool import Tool
from const import VALUTA_IDX, TIME_PRECISION, RETRY, INSTRUMENT

OK_SPOT = OkexSpotV3(use_trade_key=True)


def place_buy_order(bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY - 5):
        r = OK_SPOT.place_order('buy', bid_price, size, INSTRUMENT[VALUTA_IDX])
        order_id = print_error_or_get_order_id(r)
        if order_id != 0:
            return order_id
    return 0


def place_sell_order(ask_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY - 1):
        r = OK_SPOT.place_order('sell', ask_price, size, INSTRUMENT[VALUTA_IDX])
        order_id = print_error_or_get_order_id(r)
        if order_id != 0:
            return order_id
    return 0


def place_batch_orders(orders):
    for i in range(RETRY - 1):
        r = OK_SPOT.batch_orders(orders)
        if 'error_code' in r:  # buy: not enough money; sell: not enough coin
            print(r['error_message'])
            return []
        return [print_error_or_get_order_id(order) for order in r[INSTRUMENT[VALUTA_IDX]]]


def cancel_order(order_id):
    for i in range(RETRY - 1):
        r = OK_SPOT.cancel_order(order_id, INSTRUMENT[VALUTA_IDX])
        order_id = print_error_or_get_order_id(r)
        if order_id != 0:
            return order_id


def cancel_batch_orders(order_ids):
    order_ids_return = []
    r = OK_SPOT.cancel_batch_orders(order_ids, INSTRUMENT[VALUTA_IDX])
    for o in r[INSTRUMENT[VALUTA_IDX]]:
        order_id = print_error_or_get_order_id(o)
        order_ids_return.append(order_id if order_id != 0 else cancel_order(o['order_id']))
    return order_ids_return


def modify_order(order_id, new_price, size):
    for i in range(RETRY - 4):
        r = OK_SPOT.modify_order(order_id, new_price, size, INSTRUMENT[VALUTA_IDX])
        order_id = print_error_or_get_order_id(r)
        if order_id != 0:
            return order_id
    return 0


def get_open_orders(side):
    """place RETRY times, return open orders when success
    param side: 'buy' or 'sell'
    """
    for i in range(RETRY - 2):
        r = OK_SPOT.open_orders(INSTRUMENT[VALUTA_IDX])
        if len(r) == 0:
            return {}
        if 'error_code' not in r and len(r) > 0:
            return {int(i['order_id']): np.float64(i['price']) for i in r if i['side'] == side}
    return {}


def get_open_buy_orders():
    return get_open_orders('buy')


def get_open_sell_orders():
    return get_open_orders('sell')


def get_ticker():
    return OK_SPOT.ticker(INSTRUMENT[VALUTA_IDX])


def get_account(currency=None):
    if currency is None:
        coin_unit, money_unit = INSTRUMENT[VALUTA_IDX].split('-')
        return (OK_SPOT.account(coin_unit), OK_SPOT.account(money_unit))
    return OK_SPOT.account(currency)


def get_filled_buy_orders(before=None):
    """ TODO !!! Deprecate, The maximum result is 100
    """
    for i in range(RETRY - 3):
        r = OK_SPOT.orders(2, INSTRUMENT[VALUTA_IDX], before)
        if 'error_code' not in r and len(r) > 0:
            return [(int(i['order_id']), np.float64(i['price']), i['size']) for i in r if i['side'] == 'buy']
        time.sleep(0.01)


def place_buy_order_saveinfo(trade, capital, last_price):
    """8 is ok system precision
       0 stands for open state
    """
    size = round(capital / last_price, 8)
    buy_order_id = place_buy_order(last_price, size)
    if buy_order_id != 0:  # if no enough balance(usdt)
        trade.append([int(time.time() * TIME_PRECISION), last_price, size, 0, buy_order_id, 0, 0])
        return True
    return False


def get_high_low_lastest():
    for i in range(RETRY - 4):
        r = OK_SPOT.ticker(INSTRUMENT[VALUTA_IDX])
        if r:
            return (np.float64(r['high_24h']),
                    np.float64(r['low_24h']),
                    np.float64(r['last']),
                    Tool.convert_time_str(r['timestamp'], TIME_PRECISION))


def pickup_leak_place_buy(low_24h, capital, trade):
    low_precent = [low_24h * 0.01 * i for i in range(100, 70, -1)]
    pick_idx_by_hand = [2, 4, 6, 8, 10]
    for i in pick_idx_by_hand:
        place_buy_order_saveinfo(trade, capital, low_precent[i])
