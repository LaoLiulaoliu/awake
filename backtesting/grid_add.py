#!/usr/bin/env python
# -*- coding: utf-8 -*-


money = 100.
coin = 50.
size = 1
first_price = 0
last_price = 0
earn = 0

with open('log') as fd:
    for line in fd:
        if 'dealed' in line:
            price = float(line.split()[-1])
            if first_price == 0:
                first_price = price
                earn = coin * first_price + money
                print(f'init money[{money}], coin[{coin}], usd: {earn}')
            last_price = price
            if 'buy' in line:
                money -= price * size
                coin += size
            elif 'sell' in line:
                money += price * size
                coin -= size

print(f'money[{money}], coin[{coin}], usd: {coin * last_price + money}')
print(f'earn: {coin * last_price + money - earn}')
print('if no deal happen, init usd', 50 * first_price + 100,
    'finial usd: ', 50 * last_price + 100,
    'earn: ', 50 * (last_price - first_price))