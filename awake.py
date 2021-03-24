#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import gevent
from gevent import monkey;

monkey.patch_all()
from api.OkexWS import OkexWS
from storage.Numpd import Numpd
from ruler.State import State
from ruler.Cron import Cron
from ruler.Scheduler import Scheduler
from ruler.Trade import Trade
from strategies.equilibrium import strategy
from const import TREND_NAME_TIME, INSTRUMENT, TRADE_NAME, VALUTA_IDX


def schedule_rotate_trend_file(method):
    """ 00:00 utc everyday
    """
    crontab = '0 0 * * *'
    cron = Cron(method, TREND_NAME_TIME)
    cron.time_sets(crontab)

    s = Scheduler()
    return gevent.spawn(s.run, [cron])


def main():
    trend = Numpd(eval(TREND_NAME_TIME, globals(), {}), 4)
    trend.trend_full_load()

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    state = State(trend, trade)

    ws = OkexWS([f'spot/ticker:{INSTRUMENT[VALUTA_IDX].upper()}'],
                state,
                use_trade_key=True)
    greenlet = gevent.spawn(ws.ws_create)

    schedule_rotate_trend_file(trend.reopen)
    # strategy(state)

    greenlet.join()
    print(ws.get_connection())


main()
