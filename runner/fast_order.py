#!/usr/bin/env python3
# -*- coding: utf-8 -*-

TOP = 58000
SECTION = int(TOP * (0.8 - 0.6)) # 11600
PART = int(SECTION / 10)  # 1160
capital = 50

spot = OkexSpot(use_trade_key=True)
for i in range(1, 11):
    price = int(TOP * 0.8) - PART * i
    size = round(capital / price, 8)
    print(price, size)
    place_buy_order(spot, price, size)