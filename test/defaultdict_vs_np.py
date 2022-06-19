#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Author: Liu Dan 

import time
import numpy as np
from collections import defaultdict

row, column = 1000, 1000

def dict_time():
    start = time.time()
    storage = defaultdict(dict)

    for i in range(row):
        for j in range(column):
            storage[f'{i}_{j}'] = i + j

    for i in range(row):
        for j in range(column):
            a = storage[f'{i}_{j}']

    print('dict time: ', time.time() - start)

def array_time():
    start = time.time()
    storage = np.zeros((row, column), dtype=np.float64)

    for i in range(row):
        for j in range(column):
            storage[i, j] = i + j

    for i in range(row):
        for j in range(column):
            a = storage[i, j]
    print('array time: ', time.time() - start)

dict_time()
array_time()
