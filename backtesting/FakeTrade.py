import time
import numpy as np
from functools import partialmethod
from ruler.Trade import Trade
from const import TIME_PRECISION

class FakeTrade(Trade):
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


    def place_buy_order(self, price, size, side=0):
        order_id = int(''.join(map(str, np.random.randint(0, 10, size=16))))
        timestamp = int(time.time() * TIME_PRECISION)
        self.append([
            order_id, timestamp, np.float64(price),
            np.float64(size), side, 0])
        return order_id

    place_sell_order = partialmethod(place_buy_order, side=1)

    def place_batch_orders(self, orders):
        order_ids = []
        timestamp = int(time.time() * TIME_PRECISION)
        for order in orders:
            order_id = int(''.join(map(str, np.random.randint(0, 10, size=16))))
            side = 0 if order['side'] == 'buy' else 1
            self.append([
                order_id, timestamp, np.float64(order['price']),
                np.float64(order['size']), side, 0])
            order_ids.append(order_id)
        return order_ids   

    def modify_order(self, order_id, price, size):
        line_list = [order_id, 0, price, size, 0, 0]
        idx = np.argwhere(self.trade.info[:, self.index_bit] == order_id)[0][0]
        self.trade.modify(idx, 2, 4, line_list)
        return order_id

    def cancel_order(self, order_id):
        self.delete_canceled_orders([order_id])
        return order_id