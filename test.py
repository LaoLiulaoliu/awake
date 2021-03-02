#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import sys
import getopt
from test.numpd_test import numpd_test
from api.OkexSpot import OkexSpot, INSTRUMENT
from api.apiwrapper import place_batch_sell_orders, get_open_orders
from api.OkexWS import OkexWS
from backtesting.run import r20210219


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'nors', ['numpd=', 'spot=', 'run=', 'socket='])
    except getopt.GetoptError:
        print('test.py -n')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-n', '--numpd'):
            numpd_test()
        elif opt in ('-o', '--spot'):
            VALUTA_IDX = 0
            spot = OkexSpot(use_trade_key=True)
            # print(spot.open_orders(INSTRUMENT[VALUTA_IDX]))
            # print(spot.order_details('6493087372753920', INSTRUMENT[VALUTA_IDX]))
            # print(spot.trad_fee())
            # print(spot.orders(2, INSTRUMENT[VALUTA_IDX], '6494679719429120')) bingo
            # print(spot.orders(2, INSTRUMENT[VALUTA_IDX]))

            orders = [
                {'price': 60000, 'size': 0.00001, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
                {'price': 60001, 'size': 0.00001, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            ]
            print(place_batch_sell_orders(orders))
        elif opt in ('-s', '--socket'):
            ws = OkexWS()
            ws.ws_create()
            ws.login()
            ws.subscription(['spot/ticker:BTC-USDT'])
        elif opt in ('-r', '--run'):
            r20210219('TREND_2021-02-24.txt')
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
