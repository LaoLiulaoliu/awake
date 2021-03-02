#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from ruler.rule import r20210219


def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'd:fhs:u:z:', ['draw=', 'save=', 'dump=', 'trade='])
    except getopt.GetoptError:
        print('main.py -s leveldb_name -t')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-d', '--draw'):
            from analysis.draw_spot import draw_trend_txt
            draw_trend_txt(arg)
        elif opt == '-f':
            from ruler.fast_order import do_order
            do_order()
        elif opt == '-h':
            print('python main.py -s leveldb_name -t')
            sys.exit()
        elif opt in ('-s', '--save'):
            # '2021-02-19T12-17-16'
            arg = arg if arg else None
            from analysis.saveBid import save
            save(0, arg)
        elif opt in ('-u', '--dump'):
            from analysis.draw_spot import dump_data
            dump_data(arg)
        elif opt in ('-z', '--trade'):
            r20210219(int(arg), do_trade=True)
        else:
            print(None)


if __name__ == '__main__':
    main(sys.argv[1:])
    # main(['-d'])
