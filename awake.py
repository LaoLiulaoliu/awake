#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import gevent
from gevent import monkey; monkey.patch_all()
from datetime import datetime
from api.OkexWS import OkexWS
from storage.Numpd import Numpd
from ruler.State import State
from ruler.Cron import Cron
from ruler.Scheduler import Scheduler
from const import TREND_NAME_TIME, INSTRUMENT, TIME_PRECISION, TRADE_NAME, VALUTA_IDX


def schedule_rotate_trend_file(method):
    """ 00:00 utc everyday
    """
    crontab = '0 0 * * *'
    cron = Cron(method, TREND_NAME_TIME)
    cron.time_sets(crontab)

    s = Scheduler()
    return gevent.spawn(s.run, [cron])

def strategy(balance, coin, state):
    threshold = 0.01
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()

    while True:
        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        if timestamp > last_time:
            if abs(last_trade_price - current_price) / last_trade_price > threshold:
                half_money = 0.5 * (balance + coin * current_price)
                need_buy_amount = half_money / current_price - coin
                if need_buy_amount > 0:
                    buy_order_id = place_buy_order(best_bid, need_buy_amount)
                    last_trade_price = current_price

                elif need_buy_amount < 0:
                    sell_order_id = place_sell_order(best_ask, -need_buy_amount)
                    last_trade_price = current_price


def main():
    init_balance = 1000
    init_coin = 600

    trend = Numpd(eval(TREND_NAME_TIME, globals(), {}), 4)
    trend.trend_full_load()
    state = State(trend)

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    ws = OkexWS([f'spot/ticker:{INSTRUMENT[VALUTA_IDX].upper()}'],
                state,
                use_trade_key=True)
    greenlet = gevent.spawn(ws.ws_create)

    schedule_rotate_trend_file(trend.reopen)
    strategy(init_balance, init_coin, trend)

    greenlet.join()

main()
