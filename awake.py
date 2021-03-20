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
from const import TREND_NAME_TIME, INSTRUMENT


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
    state = State(trend)

    ws = OkexWS([f'spot/ticker:{INSTRUMENT[3].upper()}'],
                state,
                use_trade_key=True)
    greenlet = gevent.spawn(ws.ws_create)

    schedule_rotate_trend_file(trend.reopen)
    greenlet.join()

main()
