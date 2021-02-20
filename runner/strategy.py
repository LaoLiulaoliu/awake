#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from functools import partial
from .OkexSpot import OkexSpot, INSTRUMENT, print_error_or_get_order_id
from .Blaze import Blaze
from .Tool import Tool

RETRY = 10
TIME_PRECISION = 1000
HALF_HOUR = 1800000
VALUTA_IDX = 0


def place_buy_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY):
        r = spot.place_order('buy', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def place_sell_order(spot, bid_price, size):
    """place RETRY times, return order when success
    """
    for i in range(RETRY):
        r = spot.place_order('sell', INSTRUMENT[VALUTA_IDX], bid_price, size)
        order_id = print_error_or_get_order_id(r)
        if order_id:
            return order_id


def get_open_buy_orders(spot):
    """place RETRY times, return open orders when success
    """
    for i in range(RETRY):
        r = spot.open_orders(INSTRUMENT[VALUTA_IDX])
        if 'error_code' not in r and len(r) > 0:
            return {i['order_id']: float(i['price']) for i in r if i['side'] == 'buy'}


def get_filled_buy_orders(spot, before=None):
    """ TODO !!! The maximum result is 100
    """
    for i in range(RETRY):
        r = spot.orders(2, INSTRUMENT[VALUTA_IDX], before)
        if 'error_code' not in r and len(r) > 0:
            return [(i['order_id'], float(i['price']), i['size']) for i in r if i['side'] == 'buy']


def get_high_low_last(spot):
    for i in range(RETRY):
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
        size = round(capital / low_precent[i], 8)
        order_id = place_buy_order(spot, low_precent[i], size)
        tradeinfo.append([int(time.time() * TIME_PRECISION), low_precent[i], size, order_id, 0])
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


def r20210219(capital=200):
    spot = OkexSpot(use_trade_key=True)
    tradeinfo = Blaze(f'TRADE_{VALUTA_IDX}.py', 5)
    tradeinfo.load()

    high_24h, low_24h, last_price_init, begin_time = get_high_low_last(spot)
    # pickup_leak_place_buy(low_24h, capital, spot, tradeinfo)

    trend = Blaze('TREND.txt', 2)
    r = trend.custom_reload(partial(get_high_low_half_hour, begin_time))
    if r:
        high_hh, low_hh, last_half_hour_idx = r
    else:  # empty trend file or expired trend file
        trend.append((begin_time, last_price_init))
        high_hh, low_hh, last_half_hour_idx = last_price_init, last_price_init, 0
        first_half_hour_no_bid(spot, trend, last_price_init)

    print(trend.data.status())
    # high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5    # high_precent_index = {}
    
    diff_boundary = 150
    trade = {}
    open_buy_orderid_prices = {}
    filled_buy_orderid_prices_size = []
    while True:
        t = time.time()
        r = get_open_buy_orders(spot)
        if r is not None:
            open_buy_orderid_prices = r

        open_buy_orders_t = time.time()
        r = trace_trend(spot, trend, last_half_hour_idx, high_hh, low_hh)
        ticket_t = time.time()

        if r is not None:
            last_half_hour_idx, high_hh, low_hh = r
            timestamp, last_price = trend.last()

            # buy strategy
            print(high_hh, low_hh, last_price)
            if high_hh - diff_boundary > last_price:
                if have_around_open_orders(last_price - 50, last_price + 50, list(open_buy_orderid_prices.values())) is False:
                    size = round(capital / last_price, 8)
                    order_id = place_buy_order(spot, last_price, size)
                    tradeinfo.append([int(time.time() * TIME_PRECISION), last_price, size, order_id, 0])
                    trade[order_id] = [0, last_price, size, 0]  # order_id: state, price, size, pocket

            # sell strategy
            r = get_filled_buy_orders(spot, '6494679719429120')
            if r is not None:
                filled_buy_orderid_prices_size = r
            for oid, p, size in filled_buy_orderid_prices:
                if p + diff_boundary < last_price:
                    order_id = place_sell_order(spot, last_price + 50, size)
                    if order_id in trade:
                        trade[order_id][0] = 2
                        trade[order_id][3] = 1
                    else:
                        print(f'order_id not in trade: {order_id}, {trade}')

        strategy_t = time.time()
        print(f'circle: {strategy_t - t}, order: {open_buy_orders_t - t}, ticket: {ticket_t - open_buy_orders_t}, strategy: {strategy_t - ticket_t}')
