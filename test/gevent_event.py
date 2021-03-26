#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
from gevent.event import Event
from gevent.event import AsyncResult
    
evt = Event()
ay = AsyncResult()

def setter():
    print('Setter enter')
    gevent.sleep(2)
    print("Setter done")
    evt.set()
    ay.set(22)

def waiter():
    print("waiter enter")
    evt.wait()  # blocking
    print("watiter exit")

def getter():
    print('getter enter')
    r = ay.get()
    print(f'getter {r} exit')

def main():
    gevent.joinall([
        gevent.spawn(waiter),
        gevent.spawn(getter),
        gevent.spawn(setter),
    ])

if __name__ == '__main__': 
    main()
