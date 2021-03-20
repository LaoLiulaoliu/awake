#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime


class Cron(object):
    def __init__(self, method, arg):
        self.names = ['minute', 'hour', 'dayofmonth', 'month', 'dayofweek']
        self.wholes = {'minute': 60, 'hour': 24, 'dayofmonth': 31, 'month': 12, 'dayofweek': 7}
        self.tsets = {} # {'minute': {1}, 'hour': {1}, 'dayofmonth': {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31}, 'month': {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}, 'dayofweek': {0, 1, 2, 3, 4, 5, 6, 7}}
        self.method = method
        self.arg = arg

    def time_sets(self, crontab_arguments):
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

    def get_arg(self):
        return eval(self.arg, globals(), {})
