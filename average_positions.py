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
from ruler.Trade import Trade
from api.apiwrapper import place_buy_order, place_sell_order
from const import TREND_NAME_TIME, INSTRUMENT, TIME_PRECISION, TRADE_NAME, VALUTA_IDX


def schedule_rotate_trend_file(method):
    """ 00:00 utc everyday
    """
    crontab = '0 0 * * *'
    cron = Cron(method, TREND_NAME_TIME)
    cron.time_sets(crontab)

    s = Scheduler()
    return gevent.spawn(s.run, [cron])

def strategy(balance, coin, state, least_coin_amount=0.001):
    """ okex 2020-03-20 2021-03-02 10min balance 1000 stocks 0.05 fee 0.08
    交易次数 692 浮动0.01  least 0.001 return 527.7 年化 55.5%  drawdown 12.6% 3848.78
    交易次数 173 浮动0.02  least 0.002 return 550.8 年化 57.9%  drawdown 9.7% 3983.8
    交易次数 173 浮动0.025  least 0.002 return 552.6 年化 58%  drawdown 9.7% 3988.4

    change maker fee to 0
    交易次数 681 浮动0.005  least 0.001 return 549.62257 年化 57.77%  drawdown 10.9% 3929.5
    交易次数 677 浮动0.01  least 0.001 return 570.3 年化 59.95%  drawdown 10.4% 3948
    交易次数 173 浮动0.02  least 0.002 return 557.7 年化 58.6%  drawdown 9.6% 3990.7
    交易次数 175 浮动0.025  least 0.002 return 564 年化 56%  drawdown 9.5% 3997
    交易次数 476 浮动0.03  least 0.001 return 521.4 年化 54.8%  drawdown 12.3% 3891
    """
    threshold = 0.02
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()

    while True:
        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        if timestamp > last_time:
            if abs(last_trade_price - current_price) / last_trade_price > threshold:
                half_money = 0.5 * (balance + coin * current_price)
                need_buy_amount = half_money / current_price - coin
                if need_buy_amount > least_coin_amount:
                    buy_order_id = place_buy_order(best_bid, need_buy_amount)
                    last_trade_price = current_price

                elif need_buy_amount < -least_coin_amount:
                    sell_order_id = place_sell_order(best_ask, -need_buy_amount)
                    last_trade_price = current_price
                    # when order push changed data, calcuate strategy account info.
                    # or change global account info based on changed account message


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
    #strategy(init_balance, init_coin, state)

    greenlet.join()

main()
