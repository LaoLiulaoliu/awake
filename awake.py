#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Systemic risk: network broke and reconnect again

import gevent
from gevent import monkey;

monkey.patch_all()
from datetime import datetime

from api.OkexWS import OkexWS
from api.instruments import ENOBs
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
    """ websocket is IO bound, strategy is CPU bound. strategy will block websocket in gevent.
    """
    trend = Numpd(eval(TREND_NAME_TIME, globals(), {}), 4)  # 4: parse_ticker 6: parse_ticker_detail
    trend.trend_full_load()

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    state = State(trend, trade)

    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    ws = OkexWS([f'spot/ticker:{INSTRUMENT[VALUTA_IDX].upper()}',
                 f'spot/order:{INSTRUMENT[VALUTA_IDX].upper()}',
                 f'spot/account:{coin_unit}',
                 f'spot/account:{money_unit}'
                ],
                state,
                use_trade_key=True)
    g1 = gevent.spawn(ws.ws_create)
    g2 = schedule_rotate_trend_file(trend.reopen)
    gevent.sleep(3)

    enobs = 3
    for i in ENOBs:
        if i['instrument_id'] == INSTRUMENT[VALUTA_IDX].upper():
            enobs = len(i['tick_size'].split('.')[1])

    g3 = gevent.spawn(strategy, state, enobs)
    gevent.joinall([g1, g2, g3])

main()
