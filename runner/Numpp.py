#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


class Numpp(object):
    def __init__(self, column_dim, init_row_num=1000):
        self.column_dim = column_dim

        self.row_size = init_row_num
        self.current_size = 0
        self.info = np.zeros((init_row_num, column_dim))

    def append(self, line_list):
        if len(line_list) != self.column_dim:
            raise Exception(f'line size[{len(line_list)}] != column dimension[{self.column_dim}]')

        if self.current_size == self.row_size:
            self.enlarge()

        self.info[self.current_size, :] = line_list
        self.current_size += 1

    def enlarge(self):
        self.info = np.vstack((self.info, np.zeros((self.row_size, self.column_dim))))
        self.row_size *= 2

    def status(self):
        return f'Total row: {self.row_size}, data shape: {self.info.shape}, current row: {self.current_size}'

    def first(self):
        return self.info[0, :]

    def last(self):
        return self.info[self.current_size - 1, :] if self.current_size > 0 else self.info[self.current_size, :]

    def update(self, idx):
        if idx < self.row_size:
            self.info[idx, :] = [0] * self.column_dim

    def pop_last(self):
        if self.current_size > 0:
            self.info[self.current_size - 1, :] = [0] * self.column_dim

    def iterator(self, reverse=False):
        if reverse:
            for i in range(self.current_size - 1, -1, -1):
                yield self.info[i, :]
        else:
            for i in range(self.current_size):
                yield self.info[i, :]
