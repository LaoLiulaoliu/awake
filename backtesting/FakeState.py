from ruler.State import State


class FakeState(State):
    """for backtesting
    """

    def __init__(self, trend, trade):
        super(FakeState, self).__init__(trend, trade)
        self.trend = trend
        self.trade = trade

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
            yield int(timestamp), price

    def first_thirty_minutes_no_bid(self, idx):
        for r in self.trend_iter_state():
            if r is not None and self.pair[idx]['i'] > 0:
                break


    def get_latest_trend(self):
        return self.trend.iterator()

    get_latest_trend_nowait = get_latest_trend

    def delete_canceled_orders(self, order_ids):
        self.trade.delete_canceled_orders(order_ids)
        pass

    def get_order_change(self, last_price):
        for order in self.trade.select_open_orders():
            if int(order[4]) == 0:
                if last_price < order[2]:
                    self.trade.append([order[0], 0, 0, 0, 0, 2])
                    self.available[self.coin_unit] += order[3]
                    self.available[self.money_unit] -= order[2] * order[3]
                    return int(order[0]), order[2], 2
            elif int(order[4]) == 1:
                if last_price > order[2]:
                    self.trade.append([order[0], 0, 0, 0, 0, 2])
                    self.available[self.coin_unit] -= order[3]
                    self.available[self.money_unit] += order[2] * order[3]
                    return int(order[0]), order[2], 2
        return 0, 0, 0

    def set_unit(self, coin_unit, money_unit):
        self.coin_unit = coin_unit
        self.money_unit = money_unit

    def set_available(self, coin, money):
        self.available[self.coin_unit] = coin
        self.available[self.money_unit] = money

    def get_available(self):
        return self.available