#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Systemic risk: network broke and reconnect again

import gevent
from gevent import monkey;

monkey.patch_all()
from datetime import datetime

from api.OkexWS import OkexWS
from storage.Numpd import Numpd
from ruler.State import State
from ruler.Cron import Cron
from ruler.Scheduler import Scheduler
from ruler.Trade import Trade
from strategies.frequently import strategy
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
    trend = Numpd(eval(TREND_NAME_TIME, globals(), {}), 4)  # 4: parse_ticker 6: parse_ticker_detail
    trend.trend_full_load()

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    state = State(trend, trade)

    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    ws = OkexWS([f'spot/ticker:{INSTRUMENT[VALUTA_IDX].upper()}',
                 f'spot/order:{INSTRUMENT[VALUTA_IDX].upper()}',
                 f'spot/account:{coin_unit}',
                 f'spot/account:{money_unit}',
                 f'spot/depth5:{INSTRUMENT[VALUTA_IDX].upper()}'
                ],
                state,
                use_trade_key=True)
    greenlet = gevent.spawn(ws.ws_create)

    schedule_rotate_trend_file(trend.reopen)
    gevent.sleep(1)

    strategy(state)

    greenlet.join()
    print(ws.get_connection())


main()
