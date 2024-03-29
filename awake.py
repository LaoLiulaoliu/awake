#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Systemic risk: network broke and reconnect again

import gevent
from gevent import monkey;

monkey.patch_all()
from datetime import datetime
from functools import partial

from api.OkexWSV3 import OkexWSV3
from api.OkexWSV5 import OkexWSV5
from api.instruments import ENOBs
from storage.Numpd import Numpd
from ruler.Candles import Candles
from ruler.State import State
from ruler.Cron import Cron
from ruler.Scheduler import Scheduler
from ruler.Trade import Trade
from strategies.frequently import strategy
from const import TREND_NAME_TIME, INSTRUMENT, TRADE_NAME, VALUTA_IDX, API_VERSION

import monitor.log


scheduler = Scheduler()


def schedule_candle_minute(method):
    crontab = '* * * * *'
    cron = Cron(method)
    cron.time_sets(crontab)
    scheduler.add(cron)


def schedule_rotate_trend_file(method, crontab='0 0 * * *'):
    """ 00:00 utc everyday
    """
    cron = Cron(method, TREND_NAME_TIME)
    cron.time_sets(crontab)
    scheduler.add(cron)


def main():
    """ websocket is IO bound, strategy is CPU bound. strategy will block websocket in gevent.
    """
    trend = Numpd(eval(TREND_NAME_TIME, globals(), {}), 6)  # 4: parse_ticker 6: parse_ticker_detail
    trend.trend_full_load()

    trade = Trade(TRADE_NAME.format(VALUTA_IDX))
    trade.load()

    state = State(trend, trade)

    candles = Candles('candles_1m.txt')

    greenlets = []
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    if API_VERSION == 5:
        ws1 = OkexWSV5([{'channel': 'tickers', 'instId': INSTRUMENT[VALUTA_IDX].upper()}],
                       state, use_trade_key=True, channel='public')

        ws_channels = [
            {'channel': 'account', 'ccy': money_unit},
            {'channel': 'account', 'ccy': coin_unit},
            {'channel': 'orders', 'instType': 'SPOT', 'instId': INSTRUMENT[VALUTA_IDX].upper()}
        ]
#        ws2 = OkexWSV5(ws_channels, state, use_trade_key=True, channel='private')
        greenlets.append(gevent.spawn(ws1.ws_create))
#        greenlets.append(gevent.spawn(ws2.ws_create))

        schedule_candle_minute(partial(candles.get_latest_candles, INSTRUMENT[VALUTA_IDX].upper(), '1m', 5))
    else:
        ws_channels = [f'spot/ticker:{INSTRUMENT[VALUTA_IDX].upper()}',
                       f'spot/order:{INSTRUMENT[VALUTA_IDX].upper()}',
                       f'spot/account:{coin_unit}',
                       f'spot/account:{money_unit}'
                       ]
        ws = OkexWSV3(ws_channels, state, use_trade_key=True)
        greenlets.append(gevent.spawn(ws.ws_create))

    schedule_rotate_trend_file(trend.reopen)
    greenlets.append(gevent.spawn(scheduler.run))
    gevent.sleep(5)

    enobs = 3
    for i in ENOBs:
        if i['instrument_id'] == INSTRUMENT[VALUTA_IDX].upper():
            enobs = len(i['tick_size'].split('.')[1])

#    greenlets.append(gevent.spawn(strategy, state, enobs))
    gevent.joinall(greenlets)


main()
