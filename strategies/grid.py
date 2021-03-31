#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# demand: 1. stop loss and alarm; 2. web server for stop; 3.backtesting for more profit

import gevent
import time
from api.apiwrapper import cancel_order, place_batch_orders, \
    place_buy_order, place_sell_order, modify_order
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
COIN_UNIT, MONEY_UNIT = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))


def stop_loss(money_remain, ratio=STOP_LOSS_RATIO):
    if money_remain < INIT_MONEY * ratio:
        print(f'money remain: {money_remain}. Send Alarm!!!  Sleep and operate by hand')
        gevent.sleep(1800)
        return True
    return False

def place_init_orders(state, last_trade_price, enobs):
    available = state.get_available()
    coin = available[COIN_UNIT]
    money = available[MONEY_UNIT]

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
                    state.delete_canceled_orders([oid])
                    side = 'buy' if i == 0 else 'sell'
                    print(f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {BOARD_LOT}')
            return False
        return int(time.time()), order_ids[0], order_ids[1]
    return False

def place_modify_order():
    pass

def strategy(state, enobs=3):
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    buy_sell_pair = []

    r = place_init_orders(state, last_trade_price, enobs)
    if r is False:
        return
    buy_sell_pair.append(r)

    while True:
        available = state.get_available()
        coin = available[COIN_UNIT]
        money = available[MONEY_UNIT]

        if stop_loss(money):
            continue
        if len(buy_sell_pair) == 0:
            return False

        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()


        for timestamp, buy_order_id, sell_order_id in buy_sell_pair:
            buy_trade = state.get_order_by_id(buy_order_id)
            sell_trade = state.get_order_by_id(sell_order_id)
            buy_state = int(buy_trade[-1])
            sell_state = int(sell_trade[-1])
            buy_price = round(current_price - SPACING_PRICE, enobs)
            sell_price = round(current_price + SPACING_PRICE, enobs)

            if buy_state == 2:
                if buy_price < money:
                    order_id = place_buy_order(buy_price, BOARD_LOT)
                modify_order(sell_order_id, sell_price, BOARD_LOT)
            elif sell_state == 2:
                if coin > BOARD_LOT:
                    order_id = place_sell_order(sell_price, BOARD_LOT)
                modify_order(buy_order_id, buy_price, BOARD_LOT)




