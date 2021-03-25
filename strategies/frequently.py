#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
from api.apiwrapper import cancel_order, place_batch_orders, cancel_batch_orders
from const import INSTRUMENT, VALUTA_IDX


def parse_buy_sell_pair(state, buy_sell_pair):
    remove_pair = []
    if remove_pair or buy_sell_pair:
        print(f'enter remove pair: {remove_pair}, buy_sell_pair: {buy_sell_pair}')
        state.show_several_trade(5)

    for buy_order_id, sell_order_id in buy_sell_pair:
        buy_trade = state.get_order_by_id(buy_order_id)
        sell_trade = state.get_order_by_id(sell_order_id)
        buy_state = int(buy_trade[-1])
        sell_state = int(sell_trade[-1])

        if {buy_state, sell_state} == {2}:
            state.delete_filled_orders((buy_order_id, sell_order_id))
            remove_pair.append((buy_order_id, sell_order_id))
            print(f'both filled: {buy_trade}, {sell_trade}')

        elif {buy_state, sell_state} == {0}:
            cancel_batch_orders((buy_order_id, sell_order_id))
            state.delete_canceled_orders((buy_order_id, sell_order_id))
            remove_pair.append((buy_order_id, sell_order_id))
            print(f'both pending: {buy_trade}, {sell_trade}')

        elif {buy_state, sell_state} == {0, 2}:
            pass
        elif {buy_state, sell_state} == {0, 1}:
            time.sleep(30)
        elif {buy_state, sell_state} == {1}:
            time.sleep(30)
        elif {buy_state, sell_state} == {1, 2}:
            time.sleep(30)
        print(f'both unknown: {buy_trade}, {sell_trade}')

    [buy_sell_pair.remove(i) for i in remove_pair]
    if remove_pair or buy_sell_pair:
        print(f'remove pair: {remove_pair}, buy_sell_pair: {buy_sell_pair}')
        state.show_several_trade(5)



def strategy(state, enobs=3):
    """ Need ticker, account, order, depth in websocket API,
        please set in awake.py
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    buy_sell_pair = []
    i = 0

    while True:
        parse_buy_sell_pair(state, buy_sell_pair)
        available = state.get_available()
        coin = available[coin_unit]
        money = available[money_unit]

        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        timestamp_depth, best_ask, best_bid, best_ask_size, best_bid_size = state.get_depth()
        if timestamp_depth > timestamp:  # depth update quicker than ticker
            print(f'coin: {coin}, money: {money}')
            print('trend: ', timestamp, current_price, best_ask, best_bid, best_ask_size, best_bid_size)
            if best_ask - 10**-enobs * 3 >= best_bid:  # e.g best_ask: 7, best_bid: 4, 2 slots between them
                size = max(best_ask_size, best_bid_size)
                buy_price = round(best_bid + 10**-enobs, enobs)  # buy before sell
                size = min(size, coin)  # hold coin < market bid coin
                if buy_price < money:
                    sell_price = round(best_ask - 10**-enobs, enobs)
                    order_ids = place_batch_orders([
                        {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                        {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
                    ])

                    print({'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                        {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]})
                    print(f'place order_ids: {order_ids}')
                    if 0 in order_ids:
                        [cancel_order(i) for i in order_ids if i != 0]
                        print('quit strategy.')
                        return

                    buy_sell_pair.append((order_ids[0], order_ids[1]))

                    i += 1
                    if i == 2:
                        break
                    time.sleep(np.random.randint(25, 100))
            last_time = timestamp

