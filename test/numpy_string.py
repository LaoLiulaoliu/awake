#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np

candles = np.dtype({'names': ['timestamp', 'price', 'vol'], 'formats': ['u8', 'S32', 'S32']}, align=True)
a = np.array([(1619321040000, '3', '5.5'), (1619320980000, '24', '55.2')], dtype=candles)
b = np.full((10, ), 0, dtype=candles)
c = np.empty((10, ), dtype=candles)
print(a, a.shape)
print(b, b.shape)
print(c, c.shape)
