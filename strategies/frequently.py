#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from api.apiwrapper import place_buy_order, place_sell_order


def parse_trading_pair(trading_pair):
    for buy_order_id, sell_order_id in trading_pair:
        pass

def strategy(state, enobs=3):
    """ Need ticker(parse_ticker_detail) in API.
    """
    last_time, last_trade_price, best_ask, best_bid = state.get_latest_trend()
    trading_pair = []
    i = 0

    while True:
        parse_trading_pair(trading_pair)

        timestamp, current_price, best_ask, best_bid, best_ask_size, best_bid_size = state.get_latest_trend()
        if timestamp > last_time:
            if best_ask - 10**-enobs * 3 >= best_bid:  # e.g best_ask: 7, best_bid: 4, 2 slots between them
                size = max(best_ask_size, best_bid_size)
                buy_price = round(best_bid + 10**-enobs, enobs)  # buy before sell
                sell_price = round(best_ask - 10**-enobs, enobs)
                buy_order_id = place_buy_order(buy_price, size)
                sell_order_id = place_sell_order(sell_price, size)
                trading_pair.append((buy_order_id, sell_order_id))

                i += 1
                if i == 3:
                    break
            last_time = timestamp

