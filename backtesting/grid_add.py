#!/usr/bin/env python
# -*- coding: utf-8 -*-


money = 0.
coin = 0.
size = 1
print(f'init money: {money}, coin: {coin}')

with open('log') as fd:
    for line in fd:
        if 'dealed' in line:
            if 'buy' in line:
                money -= float(line.split()[-1]) * size
                coin += size
            elif 'sell' in line:
                money += float(line.split()[-1]) * size
                coin -= size

print(f'money: {money}, coin: {coin}')