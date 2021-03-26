#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
from gevent import monkey;

monkey.patch_all()

import sys
import getopt
from datetime import datetime
from test.numpd_test import numpd_test
from api.OkexSpot import OkexSpot, INSTRUMENT
from api.OkexWS import OkexWS
from backtesting.run import r20210219
from const import TREND_NAME
from storage.Numpd import Numpd
from ruler.State import State
from ruler.Cron import Cron
from ruler.Scheduler import Scheduler
from const import TREND_NAME_TIME


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'anors', ['numpd=', 'spot=', 'run=', 'socket='])
    except getopt.GetoptError:
        print('test.py -n')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-n', '--numpd'):
            numpd_test()
        elif opt in ('-a', '--a'):
            def method(num):
                print(f'in method: {num}')
                for i in range(50):
                    gevent.sleep(0.1)
                gevent.sleep(0)

            crontab = '*/3 * * * *'
            cron = Cron(method, TREND_NAME_TIME)
            cron.time_sets(crontab)

            s = Scheduler()
            g = gevent.spawn(s.run, [cron])
            while True:
                print('main thread')
                gevent.sleep(10)

        elif opt in ('-o', '--spot'):
            VALUTA_IDX = 0
            spot = OkexSpot(use_trade_key=False)
            # print(spot.open_orders(INSTRUMENT[VALUTA_IDX]))
            # print(spot.order_details('6493087372753920', INSTRUMENT[VALUTA_IDX]))
            print(spot.trad_fee(INSTRUMENT[3]))
            # print(spot.account())
            # print(spot.ticker())
            # print(spot.kline(INSTRUMENT[VALUTA_IDX], 3600))
            # print(spot.orderbook(INSTRUMENT[VALUTA_IDX], 0.1, 10))
            # print(spot.orders(2, INSTRUMENT[VALUTA_IDX], '6494679719429120')) bingo
            # print(spot.orders(2, INSTRUMENT[VALUTA_IDX]))

            # orders = [
            #     {'price': 60000, 'size': 0.00001, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            #     {'price': 60001, 'size': 0.00001, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            # ]
            # print(place_batch_orders(orders))
        elif opt in ('-s', '--socket'):

            trend = Numpd(TREND_NAME.format(datetime.utcnow().strftime('%Y-%m-%d')), 4)
            trend.trend_full_load()
            state = State(trend, trade=None)

            ws = OkexWS(['spot/account:ALPHA',
                         'spot/account:USDT',
                         'spot/order:BSV-USDT',
                         'spot/depth5:ALPHA-USDT'], state, use_trade_key=True)
            greenlet = gevent.spawn(ws.ws_create)
            # ws.subscription(['spot/depth:BTC-USDT'])
            print('websocket created, can do sth in the following coroutine')
            greenlet.join()
        elif opt in ('-r', '--run'):
            r20210219('TREND_2021-02-24.txt')
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
