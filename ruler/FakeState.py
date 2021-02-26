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

        self.first_several_minutes_no_bid(1)

    def init(self):
        for i, data in self.trend.iterator(reverse=False):
            timestamp, price = data
            self.set_init_state(price, price, 0)
            break

    def trace_trend_update_state(self):
        for i, data in self.trend.iterator(reverse=False):
            timestamp, price = data
            self.compare_set_current_high_low(price)
            self.update_high_low_idx(timestamp, trend)
            return True
        return False

    def first_several_minutes_no_bid(self, idx):
        while True:
            r = self.trace_trend_update_state()
            if r and self.pair[idx]['i'] > 0:
                break
