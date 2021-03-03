#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np


class Numpp(object):
    def __init__(self, column_dim, init_row_num=1000):
        self.column_dim = column_dim

        self.row_size = init_row_num
        self.current_size = 0
        assert self.current_size < self.row_size

        self.info = np.zeros((init_row_num, column_dim))

    def push_back(self, line_list):
        if len(line_list) != self.column_dim:
            raise Exception(f'line size[{len(line_list)}] != column dimension[{self.column_dim}]')

        if self.current_size == self.row_size:
            self.enlarge()

        self.info[self.current_size, :] = line_list
        self.current_size += 1

    def enlarge(self):
        self.info = np.concatenate((self.info, np.zeros((self.row_size, self.column_dim))), axis=0)
        self.row_size *= 2

    def status(self):
        return f'Total row: {self.row_size}, data shape: {self.info.shape}, current size: {self.current_size}'

    def first(self):
        return self.info[0, :]

    def last(self):
        return self.info[self.current_size - 1, :] if self.current_size > 0 else self.info[self.current_size, :]

    def update(self, idx):
        if idx < self.row_size:
            self.info[idx, :] = [0] * self.column_dim

    def get_idx(self, idx):
        return self.info[idx, :]

    def get_all(self):
        return self.info[0:self.current_size, :]

    def get_range(self, start, end=None):
        if end is None:
            return None if start >= self.current_size else self.info[start:self.current_size, :]

        if end > self.current_size:
            end = self.current_size
        return None if start >= end else self.info[start:end, :]

    def get_double_range(self, start):
        if start >= self.current_size:
            return None
        begin = self.current_size - (self.current_size - start) * 2
        return self.info[0:self.current_size, :] if begin < 0 else self.info[begin:self.current_size, :]

    def pop_last(self):
        if self.current_size > 0:
            self.info[self.current_size - 1, :] = [0] * self.column_dim

    def iterator(self, reverse=False):
        if reverse:
            for i in range(self.current_size - 1, -1, -1):
                yield i, self.info[i, :]
        else:
            for i in range(self.current_size):
                yield i, self.info[i, :]

