#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from test.blaze_test import blaze_test
from runner.strategy import r20210219
from runner.OkexSpot import OkexSpot, INSTRUMENT

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'bdhos:u:z:', ['dump=', 'save=', 'trade='])
    except getopt.GetoptError:
        print('main.py -s leveldb_name -t')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-b', '--blaze'):
            blaze_test()
        elif opt == '-h':
            print('python main.py -s leveldb_name -t')
            sys.exit()
        elif opt in ('-o', '--spot'):
            VALUTA_IDX = 0
            spot = OkexSpot(use_trade_key=True)
            # print(spot.open_orders(INSTRUMENT[VALUTA_IDX]))
            # print(spot.order_details('6493087372753920', INSTRUMENT[VALUTA_IDX]))
            # print(spot.trad_fee())
            # print(spot.orders(0, INSTRUMENT[VALUTA_IDX]))
            print(spot.orders(2, INSTRUMENT[VALUTA_IDX]))
        elif opt in ('-s', '--save'):
            # '2021-02-19T12-17-16'
            arg = arg if arg else None
            from analysis.saveBid import save
            save(arg)
        elif opt in ('-d', '--draw'):
            from analysis.draw_spot import load_and_draw
            load_and_draw()
        elif opt in ('-u', '--dump'):
            from analysis.draw_spot import dump_data
            dump_data(arg)
        elif opt in ('-z', '--trade'):
            r20210219(int(arg))
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
    # main(['-d'])
