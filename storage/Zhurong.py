#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict


class Zhurong(object):
    def __init__(self, fname, sep='\t'):
        self.data = OrderedDict()
        self.flush_count = 0

        self.fp = None
        self.fname = fname
        self.fp = self.open(fname)
        self.sep = sep

    def open(self, fname=None):
        if self.fp is None:
            return open(fname, 'a+') if fname else open(self.fname, 'a+')
        return self.fp

    def close(self):
        if self.fp:
            self.fp.close()

    def flush(self):
        self.fp.flush()

    def flush_candles(self):
        self.flush_count += 1
        if 63 & self.flush_count == 0:
            self.flush()
            self.flush_count = 0

    def append(self, line_list):
        """Keep 1440 candles in memory, that is 1 day long.
        """
        try:
            self.data[line_list[0]] = line_list[1:]
            self.fp.write(self.sep.join(map(str, line_list)) + '\n')
        except Exception as e:
            print(f'Zhurong::append exception is: {e}, data: {line_list}')

        if self.data.__len__() - 1440 > 0:
            self.data.popitem(last=False)  # FIFO

        self.flush_candles()

    def last(self):
        item = self.data.popitem(last=True)  # LIFO
        self.data[item[0]] = item[1:]
        return item