#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
import numba as nb
from numba.typed import List

class A(object):

  @staticmethod
  @nb.jit(nopython=True)
  def func(h, l, prices):
    for p in prices:
      if l < p < h:
        return True
    return False


t = time.time()
List([1,2,3])
print('numba List cost too much time: ', time.time() - t)

t = time.time()
a = A()
b = {1:2.1, 3:4.2}
c = list(b.values())
print(np.asarray(c, dtype=np.float32) is c)
print(np.asarray(c) is c)
r = a.func(9.1, 3.2, np.asarray(c, dtype=np.float32))

# add numba cost more time here
for i in range(100):
  a.func(9.1, 3.2, np.asarray(c, dtype=np.float32))
print(time.time() - t)

