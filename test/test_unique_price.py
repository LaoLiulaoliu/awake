#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import time
from collections import defaultdict

def delete_buy_sell_price_from_recorder(buy_price, buy_prices, sell_price, sell_prices, enobs):
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)

    buy_prices[buy_key].remove(buy_value)
    sell_prices[sell_key].remove(sell_value)

def best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
    """
    buy_prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)

    if buy_value in buy_prices[buy_key] or sell_value in sell_prices[sell_key]:
        return True
    else:
        buy_prices[buy_key].add(buy_value)
        sell_prices[sell_key].add(sell_value)
        return False

def parse_price(buy_sell_pair, buy_prices, sell_prices, enobs):
    # after filled or timeout
    remove_pair = []

    for k, v in buy_sell_pair.items():
        buy_price, sell_price = v
        if buy_price - 1.73 < 1e-5:
            pass
        else:
            remove_pair.append(k)
            break

    for i in remove_pair:
        buy_price, sell_price = buy_sell_pair.pop(i)
        delete_buy_sell_price_from_recorder(buy_price, buy_prices, sell_price, sell_prices, enobs)

        print('del: ', buy_price, buy_prices, sell_price, sell_prices)


def main(enobs=3):
    buy_prices = defaultdict(set)
    sell_prices = defaultdict(set)
    buy_sell_pair = defaultdict(tuple)

    prices = [1.732, 1.734, 1.735, 1.736, 1.732, 1.734, 1.735]
    for p in prices:
        parse_price(buy_sell_pair, buy_prices, sell_prices, enobs)

        buy_price = round(p - 2 * 10 ** -enobs, enobs)
        sell_price = round(p + 2 * 10 ** -enobs, enobs)

        if best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
            print('continue: ', buy_price, buy_prices, sell_price, sell_prices)
            continue
        else:
            print('add: ', buy_price, buy_prices, sell_price, sell_prices)
            buy_sell_pair[int(time.time())] = (buy_price, sell_price)
            time.sleep(1)


main()
