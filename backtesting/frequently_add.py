#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from api.OkexSpotV3 import OkexSpotV3
from const import VALUTA_IDX, INSTRUMENT

VALUTA_IDX = 7
spot = OkexSpotV3(use_trade_key=True)



def get_all_filled_orders():
    result = spot.orders(2, INSTRUMENT[VALUTA_IDX])
    after = result[-1]['order_id']

    for i in range(1000000):
        r = spot.orders(2, INSTRUMENT[VALUTA_IDX], after=after)
        result.extend(r)
        if len(r) < 100:
            break
        after = r[-1]['order_id']
        time.sleep(0.3)
    return result

def parse(result):
    money = 0
    coin = 0
    print(f'order length: {len(result)}')
    for i, order in enumerate(result):
        if order['side'] == 'buy':
            money -= float(order['price_avg']) * float(order['size'])
            coin += float(order['size'])
        elif order['side'] == 'sell':
            money += float(order['price_avg']) * float(order['size'])
            coin += float(order['size'])

    print(f'money: {money}, coin: {coin}')


def main():
    result = get_all_filled_orders()
    print(result)
    parse(result)