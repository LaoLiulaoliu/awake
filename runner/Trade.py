#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Blaze import Blaze
from .OkexSpot import OkexSpot
from .strategy import get_open_buy_orders


class Trade(object):
    """ 0: timestamp, 1: price, 2: size, 3: buy_order_id, 4: sell_order_id,
        5: 0-open buy, 2-fill buy, 9-open sell
    """

    def __init__(self):
        self.spot = OkexSpot(use_trade_key=True)
        self.trade = Blaze('Trade_{VALUTA_IDX}.txt', 6)
        self.trade.load()

    def append(self, timestamp, line_list):
        self.trade.append(line_list)

    def select_open_buy_order(self):
        return np.compress(self.trade.info[:, 5] == 0, self.trade.info, axis=0)[0]

    def get_open_buy_order_update_filled(self):
        """self.trade.info[: 5] - open buys orders, 剩下的状态是0的，置2
        """
        r = get_open_buy_orders(self.spot)
        if r is not None:
            condition = self.trade.info[: 5] == 0
            idxs = np.argwhere(condition == True).ravel()

            for order_id in list(r.keys()):
                cond = self.trade.info[:, 3] == order_id
                # record = np.compress(cond, self.trade.info, axis=0)[0]
                idx = np.argwhere(condition == True)[0]

            return r

    def filled_buy_order(self):
        return np.compress(self.trade.info[:, 5] == 2, self.trade.info, axis=0)[0]

    def open_sell_order(self):
        return np.compress(self.trade.info[:, 5] == 9, self.trade.info, axis=0)[0]

    def del_sell_order(self):
        pass
