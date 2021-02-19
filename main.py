#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from analysis.saveBid import save
from test.test_tradeinfo import test_tradeinfo

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'hs:t:', ['save=', 'test='])
    except getopt.GetoptError:
      print('main.py -s leveldb_name -t 1')
      sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('python main.py -s leveldb_name -t 1')
            sys.exit()
        elif opt in ('s', '--save'):
            arg = arg if arg else None
            save(arg)
        elif opt in ('t', '--test'):
            outputfile = arg

if __name__ == '__main__':
    main(sys.argv[1:])
