#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import getopt
from analysis.saveBid import save

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'hs:', ['save=', 'ofile='])
    except getopt.GetoptError:
      print 'main.py -i <inputfile> -o <outputfile>'
      sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ('s', '--save'):
            arg = arg if arg else None
            save(arg)
        elif opt in ('-o', '--ofile'):
            outputfile = arg

if __name__ == '__main__':
    main(sys.argv[1:])
