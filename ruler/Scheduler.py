#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gevent
from datetime import datetime


class Scheduler(object):
    def __init__(self):
        self.crons = []

    def add(self, cron):
        self.crons.append(cron)

    def execute(self, method, arg):
        job = gevent.spawn(method, arg) if arg is None else gevent.spawn(method)

    def run(self):
        while True:
            # cost 0.00003s empty, 0.0005 loaded in mac 2.4G
            [self.execute(s.method, s.get_arg()) for s in self.crons if s.timematch()]

            # assume this for loop can be finished in less than one minute
            gevent.sleep(60 - datetime.utcnow().second)
