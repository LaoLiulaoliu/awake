#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
import time
import logging
import numpy as np
from collections import defaultdict
from api.apiwrapper import cancel_order, place_batch_orders, cancel_batch_orders
from const import INSTRUMENT, VALUTA_IDX

logger = logging.getLogger()


def parse_buy_sell_pair(state, buy_sell_pair, buy_prices, sell_prices, enobs):
    remove_pair = []
    if len(buy_sell_pair) > 0:
        logger.info(f'enter: buy_sell_pair: {buy_sell_pair}')
        state.show_trade_len()

    for k, v in buy_sell_pair.items():
        timestamp, buy_order_id, sell_order_id = k

        buy_trade = state.get_order_by_id(buy_order_id)
        sell_trade = state.get_order_by_id(sell_order_id)
        buy_state = int(buy_trade[-1])
        sell_state = int(sell_trade[-1])

        if {buy_state, sell_state} == {2}:
            state.delete_filled_orders((buy_order_id, sell_order_id))
            remove_pair.append((timestamp, buy_order_id, sell_order_id))
            logger.info(f'both filled: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')

        elif {buy_state, sell_state} == {0}:
            # cancel in [15, 24]s, aviod a lot orders, but may miss opportunity.
            cancel_batch_orders((buy_order_id, sell_order_id))
            state.delete_canceled_orders((buy_order_id, sell_order_id))
            remove_pair.append((timestamp, buy_order_id, sell_order_id))
            logger.info(f'both pending: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')

        elif {buy_state, sell_state} == {0, 2}:
            gevent.sleep(1)
            logger.info(
                f'both unknown[{buy_trade[-1]}, {sell_trade[-1]}]: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')
            # if time.time() - timestamp > 1800:
            #     if buy_state == 0:
            #         cancel_order(buy_order_id)
            #         state.delete_canceled_orders([buy_order_id])
            #         remove_pair.append((timestamp, buy_order_id, sell_order_id))
            #         logger.info(f'delete buy {buy_order_id}: {buy_trade}')
            #     elif sell_state == 0:
            #         cancel_order(sell_order_id)
            #         state.delete_canceled_orders([sell_order_id])
            #         remove_pair.append((timestamp, buy_order_id, sell_order_id))
            #         logger.info(f'delete sell {sell_order_id}: {sell_state}')
        elif {buy_state, sell_state} == {0, 1}:
            gevent.sleep(1)
            logger.info(
                f'both unknown[{buy_trade[-1]}, {sell_trade[-1]}]: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')
        elif {buy_state, sell_state} == {1}:
            gevent.sleep(1)
            logger.info(
                f'both unknown[{buy_trade[-1]}, {sell_trade[-1]}]: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')
        elif {buy_state, sell_state} == {1, 2}:
            gevent.sleep(1)
            logger.info(
                f'both unknown[{buy_trade[-1]}, {sell_trade[-1]}]: {buy_trade[2]}, {buy_trade[3]}, {sell_trade[2]}, {sell_trade[3]}')

    for i in remove_pair:
        buy_price, sell_price = buy_sell_pair.pop(i)
        delete_buy_sell_price_from_recorder(buy_price, buy_prices, sell_price, sell_prices, enobs)

    if remove_pair or len(buy_sell_pair) > 0:
        logger.info(f'exit: buy_sell_pair: {buy_sell_pair}, remove pair: {remove_pair}')
        state.show_trade_len()

def delete_buy_sell_price_from_recorder(buy_price, buy_prices, sell_price, sell_prices, enobs):
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)

    buy_prices[buy_key].remove(buy_value)
    sell_prices[sell_key].remove(sell_value)

def best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
    """
    buy_prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)

    if buy_value in buy_prices[buy_key] or sell_value in sell_prices[sell_key]:
        return True
    else:
        buy_prices[buy_key].add(buy_value)
        sell_prices[sell_key].add(sell_value)
        return False

def strategy(state, enobs=3):
    """ Need ticker, account, order in websocket API, please set in awake.py
        depth5 is more frequent than ticker, but it is CPU bound, may block websocket.
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))

    buy_sell_pair = defaultdict(tuple)
    ongoing_num = 10
    buy_prices = defaultdict(set)
    sell_prices = defaultdict(set)

    while True:
        parse_buy_sell_pair(state, buy_sell_pair, buy_prices, sell_prices, enobs)
        available = state.get_available()
        coin = available[coin_unit]
        money = available[money_unit]

        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        best_ask_size, best_bid_size = state.get_best_size()
        if timestamp > last_time:
            last_time = timestamp

            if coin < 1:
                continue

            if best_ask - 10 ** -enobs * 3 >= best_bid:  # e.g best_ask: 7, best_bid: 4, 2 slots between them
                limit = max(round(np.random.normal(2, 1), enobs), 1)
                size = int(min(best_ask_size, best_bid_size, limit))  # hold coin < market bid coin
                size = 1 if size < 1 else size
                buy_price = round(best_bid - 2 * 10 ** -enobs, enobs)  # buy before sell
                sell_price = round(best_ask + 2 * 10 ** -enobs, enobs)
                logger.info(
                    f'buy_price: {buy_price}, sell_price: {sell_price}, size: {size}, coin: {coin}, {len(buy_sell_pair)} > {ongoing_num}')
                if size > 0 and buy_price < money:
                    if len(buy_sell_pair) > ongoing_num:
                        continue

                    order_ids = place_batch_orders([
                        {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                        {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
                    ])

                    logger.info(
                        f'buy_price: {buy_price}, size: {size}, id: {order_ids[0]}; sell_price: {sell_price}, size: {size}, id: {order_ids[1]}')

                    if 0 in order_ids:
                        for i, oid in enumerate(order_ids):
                            if oid != 0:
                                cancel_order(oid)
                                state.delete_canceled_orders([oid])
                                side = 'buy' if i == 0 else 'sell'
                                logger.info(
                                    f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {size}')
                        continue

                    if best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
                        continue
                    else:
                        buy_sell_pair[(int(time.time()), order_ids[0], order_ids[1])] = (buy_price, sell_price)
                        gevent.sleep(np.random.randint(15, 24))
