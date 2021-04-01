#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
import gevent._util
import gevent.queue
from gevent.event import Event
from gevent.event import AsyncResult

    
evt = Event()
ay = AsyncResult()
queue = gevent.queue.Queue()

def setter():
    print('Setter enter')
    gevent.sleep(2)
    print("Setter done")
    queue.put([6, 8])
    queue.put([7, 9])

    evt.set()
    ay.set([0, 2])
    # gevent.sleep(1)
    ay.set([1, 3])

    gevent.sleep(1)
    ay.set([4, 5])

    while True:
        queue.put([7, 9])
        gevent.sleep(1)

def waiter():
    print("waiter enter")
    evt.wait()  # blocking
    print("watiter exit")

def getter():
    print('getter enter')
    r1, r2 = ay.get()
    ay.set(gevent._util._NONE)
    print(f'getter {r2} exit')

    gevent.sleep(0.2)

    print('getter enter again')
    r1, r2 = ay.get()
    ay.set(gevent._util._NONE)
    print(f'getter {r2} exit again')

def queuer():
    for item in queue:
        yield item[0]
    print('exit queuer')

def cycle():
    for i in queuer():
        print(i)
        gevent.sleep(0.01)

def main():
    gevent.joinall([
        gevent.spawn(waiter),
        gevent.spawn(getter),
        gevent.spawn(setter),
        gevent.spawn(cycle)
    ])

if __name__ == '__main__': 
    main()
