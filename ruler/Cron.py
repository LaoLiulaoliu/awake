#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()
import gevent
from datetime import datetime

class Cron(object):
    def __init__(self, method):
        self.names = ['minute', 'hour', 'dayofmonth', 'month', 'dayofweek']
        self.wholes = {'minute': 60, 'hour': 24, 'dayofmonth': 31, 'month': 12, 'dayofweek': 7}
        self.tsets = {}
        self.method = method

    def _time_sets(self, crontab_arguments):
        args = crontab_arguments.split()
        if len(args) != len(self.names):
            raise ValueError(f'valid crontab expression: {crontab_arguments}')

        for arg, name in zip(args, self.names):

            nsets = set()
            for e in arg.split(','):
                if '/' in e:  # */3
                    star, div = e.rsplit('/', 1)
                    if star != '*':
                        raise ValueError('valid syntax: */n')
                    nsets.update(filter(lambda x: x % int(div) == 0, range(0, self.wholes[name])))
                elif '-' in e:  # 1-5
                    f, t = e.split('-')
                    nsets.update(range(int(f), int(t)+1))
                elif e == '*':
                    nsets.update(range(0, self.wholes[name]+1))
                else:  # 7
                    nsets.add(int(e))

            self.tsets[name] = nsets

    def timematch(self):
        t = datetime.utcnow()
        return  t.minute in self.tsets['minute'] and \
                t.hour in self.tsets['hour'] and \
                t.day in self.tsets['dayofmonth'] and \
                t.month in self.tsets['month'] and \
                t.weekday() in self.tsets['dayofweek']


class Scheduler(object):
    def execute(method):
        job = gevent.spawn(method, concurrency=10)
        job.rawlink(task_completed, method=method)

    def run(self, schedules):
        while True:
            # assume this for loop can be finished in less than one minute
            [execute(s.method) for s in schedules if s.timematch()]

            gevent.sleep(60 - datetime.utcnow().second)

crontab_arguments = '1 1 * * *'
c = Cron()
c._time_sets(crontab_arguments)
print(c.tsets, c.get_crontab_arguments())

scheduler = Scheduler()
scheduler.run([s])
