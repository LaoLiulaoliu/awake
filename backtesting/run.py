#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from ruler.FakeState import FakeState
from ruler.FakeTrade import FakeTrade
from const import INSTRUMENT, VALUTA_IDX


def r20210219(trend_fname, capital=10):
    trade = FakeTrade(f'TRADE_{VALUTA_IDX}.txt')
    trade.load()

    state = FakeState(trend_fname)
    state.init()

    diff_boundary = 150
    bias = 50
    for timestamp, last_price in state.trend_iter_state():
        s = time.time()
        ret = trade.get_open_buy_order_update_filled(last_price)
        open_buy_orderid_prices = ret  # {} or have content

        high_hh = state.get_30min()['h']
        # buy strategy
        if high_hh - diff_boundary > last_price:
            if trade.have_around_open_orders(last_price - bias, last_price + bias,
                                             list(open_buy_orderid_prices.values())) is False:
                if trade.have_around_filled_buy_orders(last_price - bias, last_price + bias) is False:
                    size = round(capital / last_price, 8)
                    buy_order_id = trade.place_buy_order(last_price, size)
                    if buy_order_id is not None:  # if no enough balance(usdt)
                        trade.append([timestamp, last_price, size, 0, buy_order_id, 0, 1])

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
                sell_order_ids = trade.place_batch_sell_orders(sell_orders)
                for sell_id, buy_id in zip(sell_order_ids, sell_order_of_buy_orderid):
                    if sell_id != 0:
                        trade.append([0, 0, 0, last_price, buy_id, sell_id, 9])
        print(time.time() -s)

    trade.get_open_sell_order_update_filled()
    trade.settlement()
