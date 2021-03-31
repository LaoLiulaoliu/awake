#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# demand: 1. stop loss and alarm; 2. web server for stop; 3.backtesting for more profit

import gevent
import time
from api.apiwrapper import cancel_order, place_batch_orders
from const import INSTRUMENT, VALUTA_IDX


INIT_MONEY = 1800
INIT_COIN = 1000
STOP_LOSS_RATIO = 0.4

low_price = 1
high_price = 2.5
SPACING_PRICE = 0.05
AVERAGE_ASK_BID_SIZE = 10  # also refer to min_size
effective_number_of_bits = 3

GRID_NUM = int((high_price - low_price) / SPACING_PRICE)
BOARD_LOT = min(round(INIT_COIN / GRID_NUM, effective_number_of_bits), AVERAGE_ASK_BID_SIZE)


def stop_loss(money_remain, ratio=STOP_LOSS_RATIO):
    if money_remain < INIT_MONEY * ratio:
        print(f'money remain: {money_remain}. Send Alarm!!!  Sleep and operate by hand')
        gevent.sleep(1800)
        return True
    return False

def place_orders(coin, money, last_trade_price, enobs):
    buy_price = round(last_trade_price - SPACING_PRICE, enobs)
    sell_price = round(last_trade_price + SPACING_PRICE, enobs)
    if coin > BOARD_LOT and buy_price < money:
        order_ids = place_batch_orders([
            {'price': buy_price, 'size': BOARD_LOT, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            {'price': sell_price, 'size': BOARD_LOT, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
        ])

        if 0 in order_ids:
            for i, oid in enumerate(order_ids):
                if oid != 0:
                    cancel_order(oid)
                    side = 'buy' if i == 0 else 'sell'
                    print(f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {BOARD_LOT}')
            return False
        return int(time.time()), order_ids[0], order_ids[1]
    return False

def strategy(state, enobs=3):
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    buy_sell_pair = []

    available = state.get_available()
    coin = available[coin_unit]
    money = available[money_unit]
    r = place_orders(coin, money, last_trade_price, enobs)
    if r is False:
        return
    buy_sell_pair.append(r)

    while True:
        available = state.get_available()
        coin = available[coin_unit]
        money = available[money_unit]

        if stop_loss(money):
            continue

        if len(buy_sell_pair) == 0:
            pass





