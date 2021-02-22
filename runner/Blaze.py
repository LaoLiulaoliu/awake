#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from .Numpp import Numpp


class Blaze(object):
    """write to log file, when load file to memory, reorganize.
    """
    def __init__(self, fname, col_dim, init_row_num=1000):
        self.fp = None
        self.fname = fname
        self.fp = self.open(fname, 'wb')

        self.data = Numpp(col_dim, init_row_num)

    def open(self, fname=None):
        if self.fp is None:
            return open(fname, 'wb') if fname else open(self.fname, 'wb')
        return self.fp

    def close(self):
        if self.fp:
            self.fp.close()

    def flush(self):
        self.fp.seek(0, 0)  # simulate closing & reopening file
        np.save(self.fp, self.data.get_all())