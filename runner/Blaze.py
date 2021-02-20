#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .Numpp import Numpp


class Blaze(object):
    def __init__(self, fname, col_dim, init_row_num=1000, sep='\t'):
        """
        col_dim: timestamp price size instrument_id order_id
        """
        self.fp = None
        self.fname = fname
        self.fp = self.open(fname)
        self.sep = sep

        self.data = Numpp(col_dim, init_row_num)

    def open(self, fname=None):
        if self.fp is None:
            return open(fname, 'a+') if fname else open(self.fname, 'a+')
        return self.fp

    def close(self):
        if self.fp:
            self.fp.close()

    def append(self, line_list):
        try:
            self.data.append(line_list)
            self.fp.write(self.sep.join(map(str, line_list)) + '\n')
        except Exception as e:
            print(f'exception is: {e}')

    def load(self):
        self.fp.seek(0, 0)
        for line in self.fp:
            self.data.append(line.split(self.sep))
