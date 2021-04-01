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
    queue.put(6)
    queue.put(7)

    evt.set()
    ay.set([0, 2])
    # gevent.sleep(1)
    ay.set([1, 3])

    gevent.sleep(1)
    ay.set([4, 5])

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
        print(item)
    print('exit queuer')

def main():
    gevent.joinall([
        gevent.spawn(waiter),
        gevent.spawn(getter),
        gevent.spawn(setter),
        gevent.spawn(queuer)
    ])

if __name__ == '__main__': 
    main()
