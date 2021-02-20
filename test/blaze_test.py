# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner.Blaze import Blaze


def blaze_test():
    data = [1, 2, 3, 4]
    tradeinfo = Blaze('friend.txt', len(data), 3)
    tradeinfo.load()
    print(tradeinfo.data.status())

    for j in range(3):
        for i in range(3):
            tradeinfo.append(data)
        print(f'idx: {j}', tradeinfo.data.status())
