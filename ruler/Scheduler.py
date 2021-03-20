#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
from datetime import datetime


class Scheduler(object):
    def __init__(self):
        pass

    def execute(self, method, arg):
        job = gevent.spawn(method, arg)

    def run(self, schedules):
        while True:
             # cost 0.00003s empty, 0.0005 loaded in mac 2.4G
            [self.execute(s.method, s.get_arg()) for s in schedules if s.timematch()]

            # assume this for loop can be finished in less than one minute
            gevent.sleep(60 - datetime.utcnow().second)
