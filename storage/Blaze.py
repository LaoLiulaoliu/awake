#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from .Numpp import Numpp


class Blaze(Numpp):
    """ For in memory, high performance, large data.

    Based on state:
    first bit is flag, A means add, M means modify, D means delete
    A   rest of data
    M   rest of data
    D   rest of data
    """
    def __init__(self, fname, col_dim, init_row_num=1000, sep='\t'):
        super(Blaze, self).__init__(col_dim, init_row_num)

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

    def load(self, write_search_idx, data_type):
        """
        data_type list of type, e.g. [int, float, float, float, int, int, int]
        ValueError: invalid literal for int() with base 10: '0.0'
        """
        self.fp.seek(0, 0)
        for l in self.fp:
            flag, rest = l.split(self.sep, maxsplit=1)
            if flag == 'A':
                self.push_back([t(float(d)) for d, t in zip(rest.split(), data_type)])
            elif flag == 'M':
                line_list = [t(float(d)) for d, t in zip(rest.split(), data_type)]
                self.info[np.argwhere(self.info[:, write_search_idx] == line_list[write_search_idx])[0][0], :] = line_list
            elif flag == 'D':
                line_list = [t(float(d)) for d, t in zip(rest.split(), data_type)]
                idx = np.argwhere(self.info[:, write_search_idx] == line_list[write_search_idx])[0][0]
                for i in range(idx, self.current_size):
                    self.info[i, :] = self.info[i+1, :]
                self.current_size -= 1

        self.fp.truncate(0)
        [self.fp.write('A' + self.sep + self.sep.join(map(str, l)) + '\n')
                for i, l in self.iterator(False)]

    def append(self, line_list):
        try:
            self.push_back(line_list)
            self.fp.write('A' + self.sep + self.sep.join(map(str, line_list)) + '\n')
        except Exception as e:
            print(f'Blaze::append exception is: {e}, data: {line_list}')

    def modify(self, idx, start, end, line_list):
        try:
            self.info[idx, start:end] = line_list[start:end]
            self.fp.write('M' + self.sep + self.sep.join(map(str, self.info[idx, :])) + '\n')
        except Exception as e:
            print(f'Blaze::modify exception is: {e}, data: {line_list}')

    def modify_bits(self, indices, bit, num):
        try:
            self.info[indices, bit] = num
            [self.fp.write('M' + self.sep + self.sep.join(map(str, line_list)) + '\n')
                    for line_list in self.info[indices, :]]
        except Exception as e:
            print(f'Blaze::modify_bits exception is: {e}, data: {line_list}')

    def delete(self, idx):
        """np.delete(self.info, idx, axis=0) copy a new array
           not support persist to disk yet.
        """
        if 0 <= idx < self.current_size:  # self.current_size < self.row_size
            self.fp.write('D' + self.sep + self.sep.join(map(str, self.info[idx, :])) + '\n')
            for i in range(idx, self.current_size):
                self.info[i, :] = self.info[i+1, :]

            self.current_size -= 1
