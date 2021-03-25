#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from .TradeBuyid import TradeBuyid


class FakeTrade(TradeBuyid):
    def __init__(self, fname):
        super(FakeTrade, self).__init__(fname)

    def get_open_buy_order_update_filled(self, last_price):
        condition = self.trade.info[: self.state_bit] == 1
        open_buy_orderid_prices = {}
        if np.any(condition):
            for open_buy_order_idx in np.argwhere(condition).ravel():
                buy_price = self.trade.info[open_buy_order_idx, 1]
                if last_price <= buy_price:
                    self.trade.modify_bits([open_buy_order_idx], self.state_bit, 2)
                else:
                    open_buy_orderid_prices[self.trade.info[open_buy_order_idx, self.buy_order_bit]] = buy_price
        return open_buy_orderid_prices

    def get_open_sell_order_update_filled(self, last_price):
        condition = self.trade.info[: self.state_bit] == 9
        open_sell_orderid_prices = {}
        if np.any(condition):
            for open_sell_order_idx in np.argwhere(condition).ravel():
                sell_price = self.trade.info[open_sell_order_idx, 3]
                if last_price >= sell_price:
                    self.sell_finished.append(self.trade.info[i, :])
                    self.trade.delete(i)
                else:
                    open_sell_orderid_prices[self.trade.info[open_sell_order_idx, self.sell_order_bit]] = sell_price
        return open_sell_orderid_prices

    @staticmethod
    def place_buy_order(last_price, size):
        return int(''.join(map(str, np.random.randint(0, 10, size=16))))

    @staticmethod
    def place_batch_sell_orders(sell_orders):
        return [int(''.join(map(str, np.random.randint(0, 10, size=16))))
                for _ in sell_orders]
