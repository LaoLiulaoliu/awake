#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from .Tool import Tool
from const import MIN_60, MIN_42, MIN_30, MIN_12, VALUTA_IDX, TIME_PRECISION, INSTRUMENT


class State(object):
    def __init__(self):
        self.flush_trend = 0
        # p60: pair of 60 minutes
        # h: high_price, l: low_price, i: last_period_time_index,
        self.p60 = {'h': 0, 'l': 0, 'i': 0}

        self.p42 = {'h': 0, 'l': 0, 'i': 0}
        self.p30 = {'h': 0, 'l': 0, 'i': 0}
        self.p12 = {'h': 0, 'l': 0, 'i': 0}

        self.pair = [self.p12, self.p30, self.p42]
        self.compare_time = [MIN_12, MIN_30, MIN_42]

    def set_init_state(self, high, low, idx):
        for pair in self.pair:
            pair['h'] = high
            pair['l'] = low
            pair['i'] = idx

    def set_restart_state(self, trend, spot, begin_time, begin_price):
        """1. data is too short, less than 12 minutes, need traverse 3 times. seted all True
           2. data expired largest period(60), no care long short. seted all False
           3. data expired short period, not expired long period. seted half False, half True
           4. empty trend file. seted all False

           False need init, empty trend file or expired trend file
        """
        self.set_init_state(0, 100000000, -1)
        seted = [False, False, False]
        period_idx = 0

        for pair, compare_time in zip(self.pair, self.compare_time):
            for i, data in trend.iterator(reverse=True):
                timestamp, price = data

                if begin_time - timestamp < compare_time:
                    if price > pair['h']:
                        pair['h'] = price
                    if price < pair['l']:
                        pair['l'] = price
                    pair['i'] = i
                    seted[period_idx] = True
                else:
                    break
            period_idx += 1

        for i in seted:
            if i is False:
                self.set_init_state(begin_price, begin_price, 0)

        if False in seted:
            trend.append((begin_time, begin_price))
            if seted[1] is False:
                self.first_several_minutes_no_bid(spot, trend, 1)
            elif seted[0] is False:
                self.first_several_minutes_no_bid(spot, trend, 0)

    def compare_set_current_high_low(self, current_price):
        """ 当前值是最大最小值，设置之
        """
        for pair in self.pair:
            if current_price > pair['h']:
                pair['h'] = current_price
            if current_price < pair['l']:
                pair['l'] = current_price

    def update_high_low_idx(self, timestamp, trend):
        """if 当前时间 - 前12分钟时间点的data[index] > 12分钟:
               时间点前进一步
           if 淘汰时间点有最大最小值:
               当下12分钟时间数据list排序
        """
        for pair, compare_time in zip(self.pair, self.compare_time):
            high_need_sort, low_need_sort = False, False
            while True:
                pre_time, pre_price = trend.get_idx(pair['i'])
                if timestamp - pre_time > compare_time:
                    if Tool.float_close(pair['h'], pre_price):
                        high_need_sort = True
                    elif Tool.float_close(pair['l'], pre_price):
                        low_need_sort = True
                    pair['i'] += 1
                else:
                    break

            if high_need_sort or low_need_sort:
                r = trend.get_range(pair['i'])
                if r is not None:
                    if high_need_sort:
                        pair['h'] = r[:, 1].max()
                    if low_need_sort:
                        pair['l'] = r[:, 1].min()

    def trace_trend_update_state(self, spot, trend):
        r = spot.ticker(INSTRUMENT[VALUTA_IDX])
        if r:
            if 'timestamp' not in r:
                print('timestamp not in r:', r)
                return
            self.flush_trend_nearly_one_hour(trend)

            timestamp = Tool.convert_time_str(r['timestamp'], TIME_PRECISION)
            current_price = float(r['last'])
            trend.append((timestamp, current_price))

            self.compare_set_current_high_low(current_price)
            self.update_high_low_idx(timestamp, trend)
            return True
        return False

    def flush_trend_nearly_one_hour(self, trend):
        self.flush_trend += 1
        if 8191 & self.flush_trend == 0:
            self.flush_trend = 1
            trend.flush()

    def first_several_minutes_no_bid(self, spot, trend, idx):
        while True:
            r = self.trace_trend_update_state(spot, trend)
            if r and self.pair[idx]['i'] > 0:
                break
            time.sleep(0.01)

    def get_60min(self):
        return self.p60

    def get_42min(self):
        return self.p42

    def get_30min(self):
        return self.p30

    def get_12min(self):
        return self.p12

    def get_time_segment_max_min(self, trend):
        r = trend.get_range(self.p42['i'], self.p12['i'])
        if r is not None:
            return r[:, 1].max(), r[:, 1].min()
