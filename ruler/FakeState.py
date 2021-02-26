#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .State import State
from storage.Numpd import Numpd


class FakeState(State):
    """for backtesting
    """

    def __init__(self, trend_fname):
        super(FakeState, self).__init__()
        self.trend = Numpd(trend_fname, 2)
        self.trend.trend_load()

    def init(self):
        for i, data in self.trend.iterator(reverse=False):
            timestamp, price = data
            self.set_init_state(price, price, 0)
            break
        self.first_thirty_minutes_no_bid(1)

    def trend_iter_state(self):
        for i, data in self.trend.iterator(reverse=False):
            timestamp, price = data
            self.compare_set_current_high_low(price)
            self.update_high_low_idx(timestamp, self.trend, i)
            yield timestamp, price

    def first_thirty_minutes_no_bid(self, idx):
        for r in self.trend_iter_state():
            if r is not None and self.pair[idx]['i'] > 0:
                break
