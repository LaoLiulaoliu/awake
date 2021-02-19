#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from analysis.saveBid import save
from test.test_tradeinfo import test_tradeinfo

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'hs:t', ['save=', 'test='])
    except getopt.GetoptError:
      print('main.py -s leveldb_name -t')
      sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('python main.py -s leveldb_name -t')
            sys.exit()
        elif opt in ('-s', '--save'):
            # '2021-02-19T12-17-16'
            arg = arg if arg else None
            save(arg)
        elif opt in ('-t', '--test'):
            test_tradeinfo(arg)
        else:
            print(None)

if __name__ == '__main__':
    main(sys.argv[1:])
