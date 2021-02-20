# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner.Blaze import Blaze


def tradeinfo_test(arg):
    tradeinfo = Blaze('friend.txt', 3)
    tradeinfo.load()
    print(tradeinfo.data.status())

    for j in range(3):
        for i in range(3):
            tradeinfo.append([1, 2, 3, 4])
        print(f'idx: {j}', tradeinfo.data.status())
