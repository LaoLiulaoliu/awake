#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from functools import partial

from .Blaze import Blaze
from .OkexSpot import OkexSpot
from .strategy import *  # TIME_PRECISION, VALUTA_IDX


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
            for oid, p, size in filled_buy_orderid_prices_size:
                if p + diff_boundary < last_price:
                    order_id = place_sell_order(spot, last_price + 50, size)
                    if order_id in trade:
                        trade[order_id][0] = 2
                        trade[order_id][3] = 1
                    else:
                        print(f'order_id not in trade: {order_id}, {trade}')

        strategy_t = time.time()
        print(f'circle: {strategy_t - t}, order: {open_buy_orders_t - t}, ticket: {ticket_t - open_buy_orders_t}, strategy: {strategy_t - ticket_t}')
