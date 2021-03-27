#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
import time
import numpy as np
from api.apiwrapper import cancel_order, place_batch_orders, cancel_batch_orders
from const import INSTRUMENT, VALUTA_IDX


def parse_buy_sell_pair(state, buy_sell_pair):
    remove_pair = []
    if remove_pair or buy_sell_pair:
        print(f'enter remove pair: {remove_pair}, buy_sell_pair: {buy_sell_pair}')
        state.show_several_trade(5)

    for timestamp, buy_order_id, sell_order_id in buy_sell_pair:
        buy_trade = state.get_order_by_id(buy_order_id)
        sell_trade = state.get_order_by_id(sell_order_id)
        buy_state = int(buy_trade[-1])
        sell_state = int(sell_trade[-1])

        if {buy_state, sell_state} == {2}:
            state.delete_filled_orders((buy_order_id, sell_order_id))
            remove_pair.append((timestamp, buy_order_id, sell_order_id))
            print(f'both filled: {buy_trade}, {sell_trade}')

        elif {buy_state, sell_state} == {0}:
            cancel_batch_orders((buy_order_id, sell_order_id))
            state.delete_canceled_orders((buy_order_id, sell_order_id))
            remove_pair.append((timestamp, buy_order_id, sell_order_id))
            print(f'both pending: {buy_trade}, {sell_trade}')

        elif {buy_state, sell_state} == {0, 2}:
            if time.time() - timestamp > 1800:
                if buy_state == 0:
                    cancel_order(buy_order_id)
                    state.delete_canceled_orders([buy_order_id])
                    remove_pair.append((timestamp, buy_order_id, sell_order_id))
                    print(f'delete buy {buy_order_id}: {buy_trade}')
                elif sell_state == 0:
                    cancel_order(sell_order_id)
                    state.delete_canceled_orders([sell_order_id])
                    remove_pair.append((timestamp, buy_order_id, sell_order_id))
                    print(f'delete sell {sell_order_id}: {sell_state}')
        elif {buy_state, sell_state} == {0, 1}:
            gevent.sleep(1)
            print(f'both unknown: {buy_trade}, {sell_trade}')
        elif {buy_state, sell_state} == {1}:
            gevent.sleep(1)
            print(f'both unknown: {buy_trade}, {sell_trade}')
        elif {buy_state, sell_state} == {1, 2}:
            gevent.sleep(1)
            print(f'both unknown: {buy_trade}, {sell_trade}')

    [buy_sell_pair.remove(i) for i in remove_pair]
    if remove_pair or buy_sell_pair:
        print(f'exit remove pair: {remove_pair}, buy_sell_pair: {buy_sell_pair}')
        state.show_several_trade(5)



def strategy(state, enobs=3):
    """ Need ticker, account, order in websocket API, please set in awake.py
        depth5 is more frequent than ticker, but it is CPU bound, may block websocket.
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    buy_sell_pair = []
    ongoing_num = 3

    while True:
        parse_buy_sell_pair(state, buy_sell_pair)
        available = state.get_available()
        coin = available[coin_unit]
        money = available[money_unit]

        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        best_ask_size, best_bid_size = state.get_best_size()
        if timestamp > last_time:
            print('trend: ', timestamp, last_time, current_price, best_ask, best_bid, best_ask_size, best_bid_size)
            if best_ask - 10**-enobs * 3 >= best_bid:  # e.g best_ask: 7, best_bid: 4, 2 slots between them
                size = min(best_ask_size, best_bid_size, coin)  # hold coin < market bid coin
                buy_price = round(best_bid + 10**-enobs, enobs)  # buy before sell
                sell_price = round(best_ask - 10**-enobs, enobs)
                print(f'buy_price: {buy_price}, sell_price: {sell_price}, size: {size}, coin: {coin}, {len(buy_sell_pair)} > {ongoing_num}')
                if size > 0 and buy_price < money:
                    if len(buy_sell_pair) > ongoing_num:
                        continue

                    order_ids = place_batch_orders([
                        {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                        {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
                    ])

                    print({'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                          '\n',
                          {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]})
                    print(f'place order_ids: {order_ids}')

                    if 0 in order_ids:
                        for i, oid in enumerate(order_ids):
                            if oid != 0:
                                cancel_order(oid)
                                side = 'buy' if i == 0 else 'sell'
                                print(f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {size}')

                    buy_sell_pair.append((int(time.time()), order_ids[0], order_ids[1]))
                    gevent.sleep(np.random.randint(5, 15))
            last_time = timestamp

