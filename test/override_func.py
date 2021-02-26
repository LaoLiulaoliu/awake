#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

class A(object):
  def __init__(self):
    pass

  def add(self, a, b):
    return a + b

  def sub(self, a, b):
    return a - b


class B(A):
  def __init__(self):
    super(B, self).__init__()
    self.a1 = {'h': 0, 'l': 1000}
    self.a2 = {'h': 0, 'l': 1000}
    self.pair = [self.a1, self.a2]

  def add(self, a):
    return a + 1

  def sub(self, a):
    return a - 1

  def compare_set_current_high_low(self, current_price):
    for pair in self.pair:
      if current_price > pair['h']:
        pair['h'] = current_price
      if current_price < pair['l']:
        pair['l'] = current_price

def test():
  b = B()
  print(b.add(3))
  print(b.sub(3))
  a = A()
  print(a.add(3, 2))
  print(a.sub(3, 2))

def test_numba():
  t = time.time()
  b = B()
  b.compare_set_current_high_low(100)
  print(b.pair)
  print(time.time() - t)

test_numba()
