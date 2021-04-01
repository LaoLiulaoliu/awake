#!/usr/bin/env python
# -*- coding: utf-8 -*-


money = 100.
coin = 50.
size = 1
first_price = 0
last_price = 0


with open('log') as fd:
    for line in fd:
        if 'dealed' in line:
            price = float(line.split()[-1])
            if first_price == 0:
                first_price = price
                print(f'init money[{money}], coin[{coin}], usd: {coin*first_price + money}')
            last_price = price
            if 'buy' in line:
                money -= price * size
                coin += size
            elif 'sell' in line:
                money += price * size
                coin -= size

print(f'money[{money}], coin[{coin}], usd: {coin*last_price + money}')