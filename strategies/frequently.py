#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from api.apiwrapper import cancel_order, place_batch_orders, cancel_batch_orders
from const import INSTRUMENT, VALUTA_IDX


def parse_trading_pair(state, trading_pair):
    remove_pair = []
    for buy_order_id, sell_order_id in trading_pair:
        buy_trade = state.get_order(buy_order_id)
        sell_trade = state.get_order(sell_order_id)
        buy_state = int(buy_trade[-1])
        sell_state = int(sell_trade[-1])

        if {buy_state, sell_state} == {2}:
            state.delete_filled_orders((buy_order_id, sell_order_id))
            remove_pair.append((buy_order_id, sell_order_id))

        elif {buy_state, sell_state} == {0}:
            cancel_batch_orders((buy_order_id, sell_order_id))
            remove_pair.append((buy_order_id, sell_order_id))

        elif {buy_state, sell_state} == {0, 2}:
            pass
        elif {buy_state, sell_state} == {0, 1}:
            time.sleep(30)
        elif {buy_state, sell_state} == {1}:
            time.sleep(30)
        elif {buy_state, sell_state} == {1, 2}:
            time.sleep(30)

    [trading_pair.remove(i) for i in remove_pair]


def strategy(state, enobs=3):
    """ Need ticker(parse_ticker_detail) and account in websocket API.
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    trading_pair = []
    i = 0

    while True:
        parse_trading_pair(state, trading_pair)
        available = state.get_available()
        coin = available[coin_unit]
        money = available[money_unit]

        timestamp, current_price, best_ask, best_bid, best_ask_size, best_bid_size = state.get_latest_trend()
        if timestamp > last_time:
            if best_ask - 10**-enobs * 3 >= best_bid:  # e.g best_ask: 7, best_bid: 4, 2 slots between them
                size = max(best_ask_size, best_bid_size)
                buy_price = round(best_bid + 10**-enobs, enobs)  # buy before sell
                if size < coin and buy_price < money:
                    sell_price = round(best_ask - 10**-enobs, enobs)
                    order_ids = place_batch_orders([
                        {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                        {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
                    ])

                    if 0 in order_ids:
                        [cancel_order(i) for i in order_ids if i != 0]
                        print('quit strategy.')
                        return

                    trading_pair.append((buy_order_id, sell_order_id))

                    i += 1
                    if i == 3:
                        break
                    time.sleep(np.random.randint(30, 100))
            last_time = timestamp

