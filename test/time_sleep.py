#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import numpy as np

l = []
for i in range(100):
    s = time.time()
    time.sleep(0.1)
    l.append(time.time() - s)
print(np.mean(l))
