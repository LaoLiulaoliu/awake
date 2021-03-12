#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import gevent
from gevent import monkey

monkey.patch_socket()

def fn(n):
    for i in range(n):
        print(gevent.getcurrent(), i)
        gevent.sleep(2)

greenlet1 = gevent.spawn(fn, 3)
greenlet2 = gevent.spawn(fn, 2)

# 等待greenlet1执行结束
greenlet1.join()
greenlet2.join()
print('greenlet run over')

# 获取fn的返回值
print(greenlet1.value)