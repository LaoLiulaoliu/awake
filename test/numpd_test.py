# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from runner.Numpd import Numpd


def numpd_test():
    data = [1, 2, 3, 4]
    trend = Numpd('friend.txt', len(data), 3)
    trend.load()
    print(trend.data.status())

    for j in range(3):
        for i in range(3):
            trend.append(data)
        print(f'idx: {j}', trend.data.status())
