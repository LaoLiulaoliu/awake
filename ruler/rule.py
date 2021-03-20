#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from storage.Numpd import Numpd
from .Trade import Trade
from api.apiwrapper import *
from .State import State
from const import INSTRUMENT, VALUTA_IDX, TREND_NAME, TRADE_NAME


def r20210219(capital=200, do_trade=False):
    trend = Numpd(TREND_NAME.format(datetime.utcnow().strftime('%Y-%m-%d')), 2)
    trend.trend_load()
    state = State(trend)

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    high_24h, low_24h, last_price_init, begin_time = get_high_low_lastest()
    # pickup_leak_place_buy(low_24h, capital, trade)


    state.set_restart_state(begin_time, last_price_init)

    print(trend.status())
    # high_precent = [high_24h * 0.01 * i for i in range(100, 70, -1)]  # math.log2(30) = 5    # high_precent_index = {}

    diff_boundary = 150
    bias = 50
    count = 0
    while True:
        t = time.time()
        ret = state.trace_trend_update_state()
        time.sleep(0.01)
        if ret is None:
            continue
        timestamp, last_price = ret
        trace_t = time.time()

        ret = trade.get_open_buy_order_update_filled()
        time.sleep(0.01)
        open_buy_orderid_prices = ret  # {} or have content
        open_buy_orders_t = time.time()

        if do_trade:
            high_hh = state.get_30min()['h']
            # buy strategy
            if high_hh - diff_boundary > last_price:
                if trade.have_around_open_orders(last_price - bias, last_price + bias,
                                                 list(open_buy_orderid_prices.values())) is False:
                    if trade.have_around_filled_buy_orders(last_price - bias, last_price + bias) is False:
                        size = round(capital / last_price, 8)
                        buy_order_id = place_buy_order(last_price, size)
                        time.sleep(0.01)
                        if buy_order_id is not None:  # if no enough balance(usdt)
                            trade.append([int(time.time() * TIME_PRECISION), last_price, size, 0, buy_order_id, 0, 1])

            # sell strategy
            r = trade.select_filled_buy_orders()
            if r.size > 0:
                sell_orders = []
                sell_order_of_buy_orderid = []
                for filled_buy_order in r:
                    if filled_buy_order[1] + diff_boundary < last_price:  # maybe place after buy filled?
                        sell_orders.append({'price': last_price, 'size': filled_buy_order[2], 'side': 'sell',
                                            'instrument_id': INSTRUMENT[VALUTA_IDX]})
                        sell_order_of_buy_orderid.append(filled_buy_order[4])
                if len(sell_orders) > 0:
                    sell_order_ids = place_batch_sell_orders(sell_orders)
                    for sell_id, buy_id in zip(sell_order_ids, sell_order_of_buy_orderid):
                        if sell_id != 0:
                            trade.append([0, 0, 0, last_price, buy_id, sell_id, 9])
                time.sleep(0.01)

        count += 1
        if 1023 & count == 0:
            count = 1
            trade.get_open_sell_order_update_filled()
            strategy_t = time.time()
            print(
                f'circle: {strategy_t - t}, trace: {trace_t - t}, order: {open_buy_orders_t - trace_t}, strategy: {strategy_t - open_buy_orders_t}')
