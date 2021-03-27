#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Blaze import Blaze
from storage.Numpd import Numpd
from api.apiwrapper import get_open_buy_orders, get_open_sell_orders
from const import TRADE_FINISHED


class Trade(object):
    """ This class is for websocket API.

        0: buy_order_id, 1: buy_timestamp, 2: bid_price, 3: size, 4: side, 5: state
        0: sell_order_id, 1: sell_timestamp, 2: ask_price, 3: size, 4: side, 5: state

        types: int, int, np.float64, np.float64, int, int

        buy_timestamp: millisecond,
        side: buy-0, sell-1,
        state: 0-init open(default in np.zeros data), 1-partially filled, 2-filled,
               5-canceled(delete), 8-delete(not show after filled)
    """

    def __init__(self, fname):
        self.index_bit = 0
        self.side_bit = 4
        self.state_bit = 5

        self.trade = Blaze(fname, 6, 200)
        self.sell_finished = Numpd(TRADE_FINISHED, 6)

    def append(self, line_list):
        """change order_id to int for numpy in api return, okex is 16bit char with digital.
        """
        if line_list[self.state_bit] == 0:
            self.trade.append(line_list)
        elif line_list[self.state_bit] == 1:
            idx = np.argwhere(self.trade.info[:, self.index_bit] == line_list[self.index_bit])[0][0]
            self.trade.modify(idx, self.state_bit, self.state_bit + 1, line_list)
        elif line_list[self.state_bit] == 2:
            idx = np.argwhere(self.trade.info[:, self.index_bit] == line_list[self.index_bit])[0][0]
            self.trade.modify(idx, self.state_bit, self.state_bit + 1, line_list)

    def load(self):
        self.trade.load(self.index_bit, [int, int, np.float64, np.float64, int, int])
        self.sell_finished.load()

    def delete_filled_orders(self, order_ids):
        for order_id in order_ids:
            idx = np.argwhere(self.trade.info[:, self.index_bit] == order_id)[0][0]
            self.trade.delete(idx)

    delete_canceled_orders = delete_filled_orders

    def print_first_trade_info(self, num=1):
        print(f'trade len {self.trade.current_size}: {self.trade.info[:num]}')

    def select_order_by_id(self, order_id):
        """return one dimension numpy array of the data
        """
        return np.compress(self.trade.info[:, self.index_bit] == order_id, self.trade.info, axis=0).ravel()

    def select_open_orders(self):
        """coded state 0
        """
        return np.compress(self.trade.info[:, self.state_bit] == 0, self.trade.info, axis=0)

    def select_filled_orders(self):
        """coded state 2
        """
        return np.compress(self.trade.info[:, self.state_bit] == 2, self.trade.info, axis=0)

    def select_open_buy_orders(self):
        return np.compress((self.trade.info[:, self.side_bit] == 0) & (self.trade.info[:, self.state_bit] == 0), self.trade.info, axis=0)

    def select_open_sell_orders(self):
        return np.compress((self.trade.info[:, self.side_bit] == 1) & (self.trade.info[:, self.state_bit] == 0), self.trade.info, axis=0)

    def have_around_open_buy_orders(self, low, high):
        """coded state 1
        """
        condition = self.trade.info[:, self.state_bit] == 1
        if np.any(condition) is True:
            open_records = np.compress(condition, self.trade.info, axis=0)
            return np.any((open_records[:, 1] > low) & (open_records[:, 1] < high))
        return False

    @staticmethod
    def have_around_open_orders(low, high, prices):
        for p in prices:
            if low < p < high:
                return True
        return False

    def have_around_filled_buy_orders(self, low, high):
        """coded state 2
        """
        condition = self.trade.info[:, self.state_bit] == 2
        if np.any(condition) is True:
            filled_records = np.compress(condition, self.trade.info, axis=0)
            return np.any((filled_records[:, 1] > low) & (filled_records[:, 1] < high))
        return False

    def settlement(self):
        earn = np.sum([(i[3] - i[1]) * i[2] for i in self.sell_finished.iterator()])

        open_buy = 0
        btc = 0
        for i in np.compress(self.trade.info[:, self.state_bit] == 1, self.trade.info, axis=0):
            open_buy += i[1] * i[2]

        for i in np.compress(self.trade.info[:, self.state_bit] == 2, self.trade.info, axis=0):
            btc += i[2]

        for i in np.compress(self.trade.info[:, self.state_bit] == 9, self.trade.info, axis=0):
            btc += i[2]

        print(f'earned: {earn}, open buy money: {open_buy}, btc in repo: {btc}')


