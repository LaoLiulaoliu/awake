# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from retrying import retry


def retry_if_error(exception):
    print('sleeped')
    return isinstance(exception, IOError)


class retry_test(object):
    # @retry(stop_max_attempt_number=3, retry_on_exception=retry_if_error)
    @retry(stop_max_attempt_number=3)
    def read_file(self):
        print('begin')
        with open('file', 'r') as f:
            return f.read()


t = retry_test()

try:
    t.read_file()
except Exception as e:
    print('e is: ', e)
