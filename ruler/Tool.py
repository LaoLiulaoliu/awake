#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime


class Tool(object):

    @staticmethod
    def binary_section_search(target, array):
        low = 0
        high = len(array) - 1
        middle = (low + high) // 2
        while low < high:
            if low == middle:  # low < target < high, low + 1 = high
                if abs(target - array[middle]) > abs(target - array[middle + 1]):
                    return middle + 1
                else:
                    return middle

            if target < array[middle]:
                high = middle
                middle = (low + high) // 2
            elif target > array[middle + 1]:
                low = middle + 1
                middle = (low + high) // 2
            else:
                if abs(target - array[middle]) > abs(target - array[middle + 1]):
                    return middle + 1
                else:
                    return middle

    @staticmethod
    def float_close(a, b, precision=1e5):
        if precision * abs(a - b) < 1:
            return True
        return False

    @staticmethod
    def convert_time_str(time_str, precision=1000):
        return int(datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * precision)

    @staticmethod
    def get_timestamp():
        now = datetime.now()
        t = now.isoformat('T', 'milliseconds')
        return t + 'Z'