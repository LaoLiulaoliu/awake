#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent
from gevent.event import Event
    
evt = Event()
    
def setter():
    print('S: Hey wait for me, I have to do something')
    gevent.sleep(1)
    print("S: I'm done")
    evt.set()

def waiter():
    print("waiter wait for you")
    evt.wait()  # blocking
    print("watiter finish")

def main():
    gevent.joinall([
        gevent.spawn(setter),
#        gevent.spawn(waiter),
#        gevent.spawn(waiter)
    ])

if __name__ == '__main__': 
    main()
