#!/usr/bin/env python
# -*- coding: utf-8 -*-


money = 0.
coin = 0.
size = 1
print(f'init money: {money}, coin: {coin}')

with open('buy') as fd:
    for line in fd:
        money -= float(line) * size
        coin += size

with open('sell') as fd:
    for line in fd:
        money += float(line) * size
        coin -= size

print(f'money: {money}, coin: {coin}')