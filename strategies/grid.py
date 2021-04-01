#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# demand: 1. web server for stop; 2. logging, 3. backtesting for more profit

import gevent
import time
import numpy as np
from api.apiwrapper import cancel_order, place_batch_orders, \
    place_buy_order, place_sell_order, modify_order
from const import INSTRUMENT, VALUTA_IDX, TIME_PRECISION
from alarm.ding import alarm


INIT_MONEY = 1240
INIT_COIN = 730
STOP_LOSS_RATIO = 0.4

low_price = 1.0
high_price = 2.5
SPACING_PRICE = 0.004
AVERAGE_ASK_BID_SIZE = 7.5  # also refer to min_size
effective_number_of_bits = 3

GRID_NUM = int((high_price - low_price) / SPACING_PRICE)
BOARD_LOT = max(round(INIT_COIN / GRID_NUM, effective_number_of_bits), AVERAGE_ASK_BID_SIZE)
COIN_UNIT, MONEY_UNIT = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
SLEEP = 30


def place_pair_orders(state, last_trade_price, enobs):
    available = state.get_available()
    coin = available[COIN_UNIT]
    money = available[MONEY_UNIT]

    buy_price = round(last_trade_price - SPACING_PRICE, enobs)
    sell_price = round(last_trade_price + SPACING_PRICE, enobs)
    size = round(np.random.normal(BOARD_LOT, 0.5), enobs)
    if coin > size and buy_price < money:
        order_ids = place_batch_orders([
            {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
        ])

        print({'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX], 'id': order_ids[0]},
                '\n',
            {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX], 'id': order_ids[1]})

        if 0 in order_ids:
            for i, oid in enumerate(order_ids):
                if oid != 0:
                    cancel_order(oid)
                    state.delete_canceled_orders([oid])
                    side = 'buy' if i == 0 else 'sell'
                    print(f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {size}')
            return

        return [int(time.time() * TIME_PRECISION), order_ids[0], order_ids[1]]
    return


def grid_init_orders(state, last_trade_price, enobs):
    while True:
        r = place_pair_orders(state, last_trade_price, enobs)
        if r is None:
            gevent.sleep(SLEEP)
        else:
            return r


def stop_loss(money_remain, ratio=STOP_LOSS_RATIO):
    while True:
        if money_remain < INIT_MONEY * ratio:
            alarm(f'money remain: {money_remain}, init money: {INIT_MONEY}. Sleep 900s and operate by hand')
            gevent.sleep(900)
        else:
            break


def strategy(state, enobs=3):
    """ Need ticker, account, order in websocket API, please set in awake.py
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    buy_sell_pair = grid_init_orders(state, last_trade_price, enobs)

    for state_order_id, order_state in state.get_order_change():
        available = state.get_available()
        coin = available[COIN_UNIT]
        money = available[MONEY_UNIT]

        stop_loss(money)
        timestamp, buy_order_id, sell_order_id = buy_sell_pair

        if state_order_id == buy_order_id:
            buy_state = order_state
            sell_state = 0
        elif state_order_id == sell_order_id:
            buy_state = 0
            sell_state = order_state
        else:
            print(f'irrelevant order: {state_order_id}, state: {order_state}')
            continue  # other irrelevant order
        success = True
        print(f'{timestamp} changed {0 if buy_order_id == state_order_id else 1} order, state: {buy_state} : {sell_state}')

        # modify failed, hold still, then buy lower sell higher.
        # buy or sell failed, logic chain breaking,
        # cancel another trade pair, wait and boot on again.
        if buy_state == 2:
            while True:
                timestamp, current_price, best_ask, best_bid = state.get_latest_trend_nowait()
                buy_price = round(current_price - SPACING_PRICE, enobs)
                sell_price = round(current_price + SPACING_PRICE, enobs)

                if buy_price < money:
                    order_id = place_buy_order(buy_price, BOARD_LOT)
                    print(f'deal buy, new order: {buy_price}')
                    if order_id == 0:
                        cancel_order(sell_order_id)  # if not cancel, this order may auto-deal later
                        print('deal buy, place new buy error')
                        gevent.sleep(SLEEP)
                        success = False
                        continue
                    else:
                        if success is True:
                            r = modify_order(sell_order_id, sell_price, BOARD_LOT)
                            print(f'deal buy, modify sell {sell_price}, order_id: {r}')
                            buy_sell_pair[0] = timestamp
                            buy_sell_pair[1] = order_id
                            break
                        else:
                            r = place_pair_orders(state, current_price, enobs)
                            if r is None:
                                success = False
                                print('deal buy, place pair order fail')
                                continue
                            else:
                                buy_sell_pair = r
                                success = True
                                print('deal buy, place pair order success')
                                break
                else:
                    cancel_order(sell_order_id)
                    print(f'deal buy, cancel sell: {sell_order_id}')
                    gevent.sleep(SLEEP)
                    success = False
                    continue

        elif sell_state == 2:
            while True:
                timestamp, current_price, best_ask, best_bid = state.get_latest_trend_nowait()
                buy_price = round(current_price - SPACING_PRICE, enobs)
                sell_price = round(current_price + SPACING_PRICE, enobs)

                if coin > BOARD_LOT:
                    order_id = place_sell_order(sell_price, BOARD_LOT)
                    print(f'deal sell, new order: {sell_price}')
                    if order_id == 0:
                        cancel_order(buy_order_id)
                        print('deal sell, place new sell error')
                        gevent.sleep(SLEEP)
                        success = False
                        continue
                    else:
                        if success is True:
                            r = modify_order(buy_order_id, buy_price, BOARD_LOT)
                            print(f'deal sell, modify buy {buy_price}, order_id {r}')
                            buy_sell_pair[0] = timestamp
                            buy_sell_pair[2] = order_id
                            break
                        else:
                            r = place_pair_orders(state, current_price, enobs)
                            if r is None:
                                success = False
                                print('deal sell, place pair order fail')
                                continue
                            else:
                                buy_sell_pair = r
                                success = True
                                print('deal sell, place pair order success')
                                break
                else:
                    cancel_order(buy_order_id)
                    print(f'deal sell, cancel buy: {buy_order_id}')
                    gevent.sleep(SLEEP)
                    success = False
                    continue
