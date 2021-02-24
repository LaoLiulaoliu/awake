#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np

data = np.arange(40000).reshape(20000, 2)


def n(a, n=10000):
    t = time.time()
    for i in range(n):
        mx = a[:, 1].max()
        mn = a[:, 1].min()
    print(time.time() - t)  # 0.2708454132080078


def m(a, n=10000):
    """ even sorted list, it's still slow
    """
    t = time.time()
    for i in range(n):
        b = sorted(a[:, 1], reverse=False)
        b[0], b[-1]
    print(time.time() - t)  # 12.64269232749939


n(data)
m(data)
