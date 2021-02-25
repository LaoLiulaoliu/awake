#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from test.numpd_test import numpd_test
from api.OkexSpot import OkexSpot, INSTRUMENT
from runner.strategy import place_batch_sell_orders


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'no', ['numpd=', 'spot='])
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
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
