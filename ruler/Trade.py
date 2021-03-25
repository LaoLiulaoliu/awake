#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Blaze import Blaze
from storage.Numpd import Numpd
from api.apiwrapper import get_open_buy_orders, get_open_sell_orders
from const import TRADE_FINISHED


class Trade(object):
    """ This class is for websocket API.

        0: buy_order_id, 1: buy_timestamp, 2: bid_price, 3: size, 4: state
        0: sell_order_id, 1: sell_timestamp, 2: ask_price, 3: size, 4: state

        types: int, int, np.float64, np.float64, int

        buy_timestamp: millisecond,
        state: 0-init open(default in np.zeros data), 1-partially filled, 2-filled, 8-delete(not show after filled)
    """

    def __init__(self, fname):
        self.index_bit = 0
        self.state_bit = 4

        self.trade = Blaze(fname, 5, 200)
        self.sell_finished = Numpd(TRADE_FINISHED, 5)

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
        self.trade.load(self.index_bit, [int, int, np.float64, np.float64, int])
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

    def get_open_buy_order_update_filled(self):
        """(self.trade.info[: 6] == 1) - open buy orders, 剩下的状态是1的，置2
        """
        r = get_open_buy_orders()
        if len(r) > 0:
            open_buy_order_idx = set()
            for order_id in list(r.keys()):
                condition = self.trade.info[:, self.buy_order_bit] == order_id
                if np.any(condition):  # initial load have historical human placed orders, not added
                    open_buy_order_idx.add(np.argwhere(condition)[0][0])

            trade_open_buy_order_idx = set(np.argwhere(self.trade.info[:, self.state_bit] == 1).ravel())
            rest_idx = list(trade_open_buy_order_idx - open_buy_order_idx)  # {1,2,3} - {1, 5}
            if len(rest_idx) > 0:
                print(f'get_open_buy_order_update_filled: {trade_open_buy_order_idx} - {open_buy_order_idx} = {rest_idx}')
                for i in range(15):
                    print(', '.join(map(str, self.trade.info[i])))
                self.trade.modify_bits(rest_idx, self.state_bit, 2)
        return r

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

    def get_open_sell_order_update_filled(self):
        """(self.trade.info[: 6] == 9) - open sell orders, 剩下的状态是9的，置8,
           delete_sell_order
        """
        r = get_open_sell_orders()
        if len(r) > 0:
            open_sell_order_idx = set()
            for order_id in list(r.keys()):
                condition = self.trade.info[:, self.sell_order_bit] == order_id
                if np.any(condition):
                    open_sell_order_idx.add(np.argwhere(condition)[0][0])

            trade_open_sell_order_idx = set(np.argwhere(self.trade.info[:, self.state_bit] == 9).ravel())
            rest_idx = list(trade_open_sell_order_idx - open_sell_order_idx)
            if len(rest_idx) > 0:
                for i in rest_idx:
                    self.sell_finished.append(self.trade.info[i, :])
                    self.trade.delete(i)
        return r

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


