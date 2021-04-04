#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from .Numpp import Numpp


class Numpd(Numpp):
    def __init__(self, fname, col_dim, init_row_num=1000, sep='\t'):
        """ For large scale data, only support sequential write, not support modify operation.
        modify plan: write to log file, when load file to memory, reorganize it.

        param: col_dim, timestamp price size instrument_id order_id
        """
        super(Numpd, self).__init__(col_dim, init_row_num)

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

    def reopen(self, f_new_name):
        if self.fp:
            self.fp.close()
        self.info.fill(0)

        self.fname = f_new_name
        self.fp = open(f_new_name, 'a+')

    def load(self, convert=None):
        self.fp.seek(0, 0)
        if convert:
            for line in self.fp:
                self.push_back(list(map(convert, line.split(self.sep))))
        else:
            for line in self.fp:
                self.push_back(line.split(self.sep))

    def reload(self, convert=None, reverse=True, callback=lambda x: None):
        self.load(convert)
        return callback(self.iterator(reverse=reverse))

    def trend_load(self):
        self.fp.seek(0, 0)
        for line in self.fp:
            timestamp, price = line.split(self.sep)
            self.push_back((int(timestamp), np.float64(price)))

    def trend_full_load(self):
        self.fp.seek(0, 0)
        for line in self.fp:
            timestamp, price, ask, bid = line.split(self.sep)
            self.push_back((int(timestamp), np.float64(price), np.float64(ask), np.float64(bid)))

    def append(self, line_list):
        try:
            self.push_back(line_list)
            self.fp.write(self.sep.join(map(str, line_list)) + '\n')
        except Exception as e:
            print(f'Numpd::append exception is: {e}, data: {line_list}')
