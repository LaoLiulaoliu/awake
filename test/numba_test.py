#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
import numba

class A(object):

  @staticmethod
  @numba.jit(nopython=True)
  def func(h, l, prices):
    for p in prices:
      if l < p < h:
        return True
    return False


def run_multi_times()
    t = time.time()
    for i in range(100):
      A.func(9.1, 3.2, np.asarray([2.1, 4.2], dtype=np.float32))
    print(time.time() - t)


def numba_list_cost():
    from numba.typed import List
    t = time.time()
    List([1,2,3])
    print('numba List cost too much time: ', time.time() - t)


def test():
    t = time.time()
    a = A()
    b = {1:2.1, 3:4.2}
    c = list(b.values())
    print(np.asarray(c, dtype=np.float32) is c)  # False
    print(np.asarray(c) is c)  # False
    r = a.func(9.1, 3.2, np.asarray(c, dtype=np.float32))

test()
