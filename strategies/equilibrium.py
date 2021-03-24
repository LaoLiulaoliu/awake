#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# okex 2020-03-20 2021-03-02 10min balance 1000 stocks 0.05 fee 0.08
#     交易次数 692 浮动0.01  least 0.001 return 527.7 年化 55.5%  drawdown 12.6% 3848.78
#     交易次数 173 浮动0.02  least 0.002 return 550.8 年化 57.9%  drawdown 9.7% 3983.8
#     交易次数 173 浮动0.025  least 0.002 return 552.6 年化 58%  drawdown 9.7% 3988.4

#     change maker fee to 0
#     交易次数 681 浮动0.005  least 0.001 return 549.62257 年化 57.77%  drawdown 10.9% 3929.5
#     交易次数 677 浮动0.01  least 0.001 return 570.3 年化 59.95%  drawdown 10.4% 3948
#     交易次数 173 浮动0.02  least 0.002 return 557.7 年化 58.6%  drawdown 9.6% 3990.7
#     交易次数 175 浮动0.025  least 0.002 return 564 年化 56%  drawdown 9.5% 3997
#     交易次数 476 浮动0.03  least 0.001 return 521.4 年化 54.8%  drawdown 12.3% 3891

from api.apiwrapper import place_buy_order, place_sell_order
from const import INSTRUMENT, VALUTA_IDX


def strategy(state, least_coin_proportion=0.05):
    """ Websocket account change message to get balance, need whole account without other strategies.
        Calculating balance based on order state change message, can fuse others in one account.

        Need ticker and account in API.
    """
    threshold = 0.02
    coin_unit, money_unit = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()

    while True:
        timestamp, current_price, best_ask, best_bid = state.get_latest_trend()
        if timestamp > last_time:
            balance = state.get_balance()
            coin = balance[coin_unit]
            money = balance[money_unit]

            if abs(last_trade_price - current_price) / last_trade_price > threshold:
                half_money = 0.5 * (money + coin * current_price)
                need_buy_amount = half_money / current_price - coin
                least_coin_amount = least_coin_proportion * coin
                if need_buy_amount > least_coin_amount:
                    buy_order_id = place_buy_order(best_bid, need_buy_amount)
                    last_trade_price = current_price

                elif -need_buy_amount < least_coin_amount:
                    sell_order_id = place_sell_order(best_ask, -need_buy_amount)
                    last_trade_price = current_price

            last_time = timestamp
