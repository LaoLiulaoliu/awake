#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt

from analysis.draw_spot import dump_data, load_and_draw
from test.tradeinfo_test import tradeinfo_test


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'hs:du:t', ['save=', 'draw=', 'dump=', 'test='])
    except getopt.GetoptError:
        print('main.py -s leveldb_name -t')
        sys.exit(2)

    for opt, arg in opts:
        print(opt, arg)
        if opt == '-h':
            print('python main.py -s leveldb_name -t')
            sys.exit()
        elif opt in ('-s', '--save'):
            # '2021-02-19T12-17-16'
            arg = arg if arg else None
            from analysis.saveBid import save
            save(arg)
        elif opt in ('-d', '--draw'):
            load_and_draw()
        elif opt in ('-u', '--dump'):
            dump_data(arg)
        elif opt in ('-t', '--test'):
            tradeinfo_test(arg)
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
    # main(['-d'])
