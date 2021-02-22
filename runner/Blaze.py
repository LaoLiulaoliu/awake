#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from .Numpp import Numpp


class Blaze(Numpp):
    """ For in memory, high performance, small data.
        synchronous to hard disk in real time.
    """
    def __init__(self, fname, col_dim, init_row_num=1000):
        super(Blaze, self).__init__(col_dim, init_row_num)

        self.fp = None
        self.fname = fname
        self.fp = self.open(fname)

    def open(self, fname=None):
        if self.fp is None:
            return open(fname, 'wb') if fname else open(self.fname, 'wb')
        return self.fp

    def close(self):
        if self.fp:
            self.fp.close()

    def flush(self):
        self.fp.seek(0, 0)  # simulate closing & reopening file
        np.save(self.fp, self.get_all())

    def load(self):
        """Only use after self.__init__
        """
        try:
            arr = np.load(self.fname)
        except ValueError:  # empty file
            return
        length = len(arr)
        if length == 0:
            return
        while length > self.row_size:
            self.enlarge()
        self.info[:length, :] = arr

    def append(self, line_list):
        self.push_back(line_list)
        self.flush()

    def delete(self, idx):
        """np.delete(self.info, idx, axis=0) copy a new array
           not support persist to disk yet.
        """
        if 0 <= idx < self.current_size:  # self.current_size < self.row_size
            for i in range(idx, self.current_size):
                self.info[i, :] = self.info[i+1, :]

            self.current_size -= 1