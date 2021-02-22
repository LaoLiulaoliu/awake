#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from .Numpd import Numpd
from .OkexSpot import OkexSpot
from .strategy import *
from .State import State


def r20210219(capital=200, do_trade=False):
    spot = OkexSpot(use_trade_key=True)
    state = State()
    tradeinfo = Numpd(f'TRADE_{VALUTA_IDX}.py', 5)
    tradeinfo.load()

    high_24h, low_24h, last_price_init, begin_time = get_high_low_lastest(spot)
    # pickup_leak_place_buy(low_24h, capital, spot, tradeinfo)

    trend = Numpd(f"TREND_{datetime.utcnow().strftime('%Y-%m-%d')}.txt", 2)
    trend.trend_load()
    state.set_restart_state(trend, spot, begin_time, last_price_init)

    print(trend.data.status())
    # high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5    # high_precent_index = {}
    
    diff_boundary = 150
    trade = {}
    open_buy_orderid_prices = {}
    filled_buy_orderid_prices_size = []
    while True:
        t = time.time()
        ret = get_open_buy_orders(spot)
        if ret is not None:
            open_buy_orderid_prices = ret

        open_buy_orders_t = time.time()
        ret = state.trace_trend_update_state(spot, trend)
        ticket_t = time.time()

        if ret:
            timestamp, last_price = trend.last()

            if do_trade:
                high_hh = state.get_30min()['h']
                # buy strategy
                if high_hh - diff_boundary > last_price:
                    if have_around_open_orders(last_price - 50, last_price + 50, list(open_buy_orderid_prices.values())) is False:
                        if have_around_filled_orders(last_price - 50, last_price + 50, trade) is False:
                            size = round(capital / last_price, 8)
                            order_id = place_buy_order(spot, last_price, size)
                            if order_id is not None:  # if no enough balance(usdt)
                                tradeinfo.append([int(time.time() * TIME_PRECISION), last_price, size, order_id, 0])
                                trade[order_id] = [0, last_price, size, 0]  # order_id: state, price, size, pocket

                # sell strategy
                r = get_filled_buy_orders(spot, '6494679719429120')
                if r is not None:
                    filled_buy_orderid_prices_size = r
                for oid, p, size in filled_buy_orderid_prices_size:
                    if p + diff_boundary < last_price:
                        order_id = place_sell_order(spot, last_price, size)
                        if order_id in trade:  # need trade.pop(order_id)? write whole not poped to file periodically
                            trade[order_id][0] = 2  # state filled
                            trade[order_id][3] = 1  # save to pocket
                        else:
                            print(f'order_id not in trade: {order_id}, {trade}')

        strategy_t = time.time()
        print(f'circle: {strategy_t - t}, order: {open_buy_orders_t - t}, ticket: {ticket_t - open_buy_orders_t}, strategy: {strategy_t - ticket_t}')
