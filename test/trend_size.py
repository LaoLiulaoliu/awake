#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

import sys
import time
import numpy as np

six_hours = 10 * 3600 * 6
twenty_four_hours = 10 * 3600 * 24

def gen_numpy(hours):
    now = int(time.time())
    n = np.zeros((hours, 4), dtype=np.float64)
    print(f'hours empty size: {n.nbytes / 1024**2}M')
    for i in range(hours):
        n[i] = [now, 111.1, 222.1, 333.3]
    print(f'hours size: {sys.getsizeof(n) / 1024**2}M')
    print(n[:10])
    n.fill(0)
    print(n[:10])

gen_numpy(six_hours) # 6.591796875M
gen_numpy(twenty_four_hours)  # 26.3671875M
