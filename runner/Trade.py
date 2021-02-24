#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Blaze import Blaze
from storage.Numpd import Numpd
from .strategy import get_open_buy_orders, get_open_sell_orders


class Trade(object):
    """ 0: buy_timestamp, 1: buy_price, 2: size, 3: sell_price, 4. buy_order_id, 5: sell_order_id,
        6: 1-open buy, 2-fill buy, 9-open sell. do not use 0 in np.zeros data
    """

    def __init__(self, fname):
        self.buy_order_bit = 4
        self.sell_order_bit = 5
        self.state_bit = 6

        self.trade = Blaze(fname, 7, 200)
        self.sell_finished = Numpd('sell_finished_orders.txt', 7)

    def append(self, line_list):
        """change order_id to int for numpy in api return, okex is 16bit char with digital.
        coded state 1 9
        """
        if line_list[self.state_bit] == 1:
            self.trade.append(line_list)
        elif line_list[self.state_bit] == 9:
            idx = np.argwhere(self.trade.info[:, self.buy_order_bit] == line_list[self.buy_order_bit])[0][0]
            self.trade.info[idx, self.sell_order_bit:self.state_bit+1] = line_list[self.sell_order_bit:self.state_bit+1]

    def load(self):
        self.trade.load()
        self.sell_finished.load()

    def select_open_buy_orders(self):
        """coded state 1
        """
        return np.compress(self.trade.info[:, self.state_bit] == 1, self.trade.info, axis=0)

    def select_filled_buy_orders(self):
        """coded state 2
        """
        return np.compress(self.trade.info[:, self.state_bit] == 2, self.trade.info, axis=0)

    def select_open_sell_orders(self):
        """coded state 9
        """
        return np.compress(self.trade.info[:, self.state_bit] == 9, self.trade.info, axis=0)

    def get_open_buy_order_update_filled(self, spot):
        """(self.trade.info[: 6] == 0) - open buys orders, 剩下的状态是0的，置2
        """
        r = get_open_buy_orders(spot)
        if r is not None:
            open_buy_order_idx = set()
            for order_id in list(r.keys()):
                condition = self.trade.info[:, self.buy_order_bit] == order_id
                if np.any(condition):  # initial load have historical human placed orders, not added
                    open_buy_order_idx.add(np.argwhere(condition)[0][0])

            trade_open_buy_order_idx = set(np.argwhere(self.trade.info[: self.state_bit] == 1).ravel())
            rest_idx = list(trade_open_buy_order_idx - open_buy_order_idx)  # {1,2,3} - {1, 5}
            if len(rest_idx) > 0:
                self.trade.info[rest_idx, self.state_bit] = 2
            return r

    def have_around_open_buy_orders(self, low, high):
        """coded state 1
        """
        condition = self.trade.info[:, self.state_bit] == 1
        if np.any(condition) is True:
            open_records = np.compress(condition, self.trade.info, axis=0)
            return np.any((open_records[:, 1] > low) & (open_records[:, 1] < high))
        return False

    def have_around_filled_buy_orders(self, low, high):
        """coded state 2
        """
        condition = self.trade.info[:, self.state_bit] == 2
        if np.any(condition) is True:
            filled_records = np.compress(condition, self.trade.info, axis=0)
            return np.any((filled_records[:, 1] > low) & (filled_records[:, 1] < high))
        return False

    def get_open_sell_order_update_filled(self, spot):
        """ not implemented yet
        """
        r = get_open_sell_orders(spot)
        if r is not None:
            open_sell_order_idx = set()
            for order_id in list(r.keys()):
                condition = self.trade.info[:, self.buy_order_bit] == order_id
                open_sell_order_idx.add(np.argwhere(condition)[0][0])

            trade_open_buy_order_idx = set(np.argwhere(self.trade.info[: self.state_bit] == 9).ravel())
            rest_idx = list(trade_open_buy_order_idx - open_sell_order_idx)
            if len(rest_idx) > 0:
                self.trade.info[rest_idx, self.state_bit] = 2
            return r

    def del_sell_order(self):
        pass
