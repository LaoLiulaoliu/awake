#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
