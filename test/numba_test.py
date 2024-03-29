#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import numpy as np
import numba
import functools


def time_decoator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = time.time()
        ret = func(*args, **kwargs)
        print(time.time() - t)
        return ret
    return wrapper


class A(object):

    @staticmethod
    @numba.jit(nopython=True)
    def func(h, l, prices):
        for p in prices:
            if l < p < h:
                return True
        return False

    @staticmethod
    @numba.vectorize('float64(float64, float64, float64)', target='parallel', nopython=True)
    def rule_with_parallel(y, a, b):
        if y < a:
            return a
        if y > b:
            return b
        return y

def run_multi_times():
    t = time.time()
    for i in range(100):
      A.func(9.1, 3.2, np.asarray([2.1, 4.2]))
    print(time.time() - t)  # 0.1, but python 0.00033


def another_run_multi_times():
    t = time.time()
    for i in range(100):
        for j in [2.1, 4.2]:
            A.rule_with_parallel(j, 9.1, 3.2)
    print(time.time() - t)  # 0.0154, python 5.22e-05


def numba_list_cost():
    from numba.typed import List
    t = time.time()
    List([1,2,3])
    print('numba List cost too much time: ', time.time() - t)


def test_array_list():
    t = time.time()
    a = A()
    b = {1:2.1, 3:4.2}
    c = list(b.values())
    print(np.asarray(c, dtype=np.float32) is c)  # False
    print(np.asarray(c) is c)  # False
    r = a.func(9.1, 3.2, np.asarray(c, dtype=np.float32))

def test_convert_float():
    t = time.time()
    for i in range(10000):
        np.float64('123')
    print('np.float64 convert cost: ', time.time() - t)

    t = time.time()
    for i in range(10000):
        float('123')
    print('float convert cost: ', time.time() - t)

def test_convert_int():
    t = time.time()
    for i in range(10000):
        np.int64('123')
    print('np.int64 convert cost: ', time.time() - t)

    t = time.time()
    for i in range(10000):
        int('123')
    print('int convert cost: ', time.time() - t)


def float_close(a, b, precision=1e5):
    if precision * abs(a - b) < 1:
        return True
    return False

@time_decoator
def test_float_close():
    for i in range(10000):
        float_close(np.float64(1.001), np.float64(1.0001))

@time_decoator
def test_npfloat_close():
    for i in range(10000):
        np.isclose(np.float64(1.001), np.float64(1.0001))


test_float_close()
test_npfloat_close()
