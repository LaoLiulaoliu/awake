#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import gevent
import numpy as np
import gevent._util
import gevent.queue
from gevent.event import Event, AsyncResult
from .Tool import Tool
from const import MIN_60, MIN_42, MIN_30, MIN_12, TIME_PRECISION
from api.apiwrapper import get_ticker, get_account


class State(object):
    __sem = gevent.lock.BoundedSemaphore(1)

    def __new__(cls, *args, **kwargs):
        if not hasattr(State, '_instance'):
            with State.__sem:
                if not hasattr(State, '_instance'):
                    State._instance = object.__new__(cls)
        return State._instance

    def __init__(self, trend, trade):
        self.trend = trend
        self.flush_trend = 0
        self.trade = trade
        self.event = Event()
        self.async_result = AsyncResult()
        self.queue = gevent.queue.Queue()

        self.balance = {}
        self.available = {}
        self.parse_account(get_account())

        self.best_size = np.zeros(2)
        self.depth = [0, 0, 0, 0, 0]  # caution about initial value

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

    def set_restart_state(self, begin_time, begin_price):
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
            for i, data in self.trend.iterator(reverse=True):
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
            self.trend.append((begin_time, begin_price))
            if seted[1] is False:
                self.first_several_minutes_no_bid(1)
            elif seted[0] is False:
                self.first_several_minutes_no_bid(0)

    def compare_set_current_high_low(self, current_price):
        """ 当前值是最大最小值，设置之
        """
        for pair in self.pair:
            if current_price > pair['h']:
                pair['h'] = current_price
            if current_price < pair['l']:
                pair['l'] = current_price

    def update_high_low_idx(self, timestamp, trend_replay_current_idx=None):
        """if 当前时间 - 前12分钟时间点的data[index] > 12分钟:
               时间点前进一步
           if 淘汰时间点有最大最小值:
               当下12分钟时间数据list排序

        :param trend_replay_current_idx: only used for replay trend
        """
        for pair, compare_time in zip(self.pair, self.compare_time):
            high_need_sort, low_need_sort = False, False
            while True:
                pre_time, pre_price = self.trend.get_idx(pair['i'])
                if timestamp - pre_time > compare_time:
                    if Tool.float_close(pair['h'], pre_price):
                        high_need_sort = True
                    elif Tool.float_close(pair['l'], pre_price):
                        low_need_sort = True
                    pair['i'] += 1
                else:
                    break

            if high_need_sort or low_need_sort:
                r = self.trend.get_range(pair['i'], trend_replay_current_idx)
                if r is not None:
                    if high_need_sort:
                        pair['h'] = r[:, 1].max()
                    if low_need_sort:
                        pair['l'] = r[:, 1].min()

    def trace_trend_update_state(self):
        r = get_ticker()
        if r:
            if 'timestamp' not in r:
                print('timestamp not in r:', r)
                return
            self.flush_trend_nearly_ten_min()

            timestamp = Tool.convert_time_str(r['timestamp'], TIME_PRECISION)
            current_price = np.float64(r['last'])
            self.trend.append((timestamp, current_price))

            self.compare_set_current_high_low(current_price)
            self.update_high_low_idx(timestamp)
            return timestamp, current_price

    def flush_trend_nearly_ten_min(self):
        """ 10 * 60 * 14 = 8400
        """
        self.flush_trend += 1
        if 8191 & self.flush_trend == 0:
            self.trend.flush()
            self.flush_trend = 1

    def first_several_minutes_no_bid(self, idx):
        while True:
            r = self.trace_trend_update_state()
            if r is not None and self.pair[idx]['i'] > 0:
                break
            time.sleep(0.1)

    def get_60min(self):
        return self.p60

    def get_42min(self):
        return self.p42

    def get_30min(self):
        return self.p30

    def get_12min(self):
        return self.p12

    def get_time_segment_max_min(self):
        r = self.trend.get_range(self.p42['i'], self.p12['i'])
        if r is not None:
            return r[:, 1].max(), r[:, 1].min()

    def restart_schedule(self):
        pass

    def schedule(self):
        pass

    def parse_ticker(self, message):
        for i in message:
            self.flush_trend_nearly_ten_min()

            timestamp = Tool.convert_time_str(i['timestamp'], TIME_PRECISION)
            current_price = np.float64(i['last'])
            self.trend.append((timestamp, current_price, np.float64(i['best_ask']), np.float64(i['best_bid'])))
            self.best_size[0] = np.float64(i['best_ask_size'])
            self.best_size[1] = np.float64(i['best_bid_size'])
            self.event.set()  # set flag to true

    def get_latest_trend(self):
        self.event.wait()  # wait stop when flag set to true
        self.event.clear()  # set flag to false
        return self.trend.last()

    def get_latest_trend_nowait(self):
        return self.trend.last()

    def get_best_size(self):
        return self.best_size

    def parse_ticker_detail(self, message):
        for i in message:
            self.flush_trend_nearly_ten_min()

            timestamp = Tool.convert_time_str(i['timestamp'], TIME_PRECISION)
            current_price = np.float64(i['last'])
            self.trend.append((timestamp,
                               current_price,
                               np.float64(i['best_ask']),
                               np.float64(i['best_bid']),
                               np.float64(i['best_ask_size']),
                               np.float64(i['best_bid_size'])))

    def parse_account(self, message):
        for i in message:
            currency = i['currency'].upper()
            self.balance[currency] = float(i['balance'])
            self.available[currency] = float(i['available'])

    def get_balance(self):
        return self.balance

    def get_available(self):
        return self.available

    def parse_order(self, message):
        """ canceled -1, open 0, filled 2, modify 0
        """
        for i in message:
            state = int(i['state'])
            if state == 0:
                timestamp = Tool.convert_time_str(i['timestamp'], TIME_PRECISION)
                side = 0 if i['side'] == 'buy' else 1
                self.trade.append([int(i['order_id']), timestamp, np.float64(i['price']),
                                   np.float64(i['size']), side, state])
            elif state == 1:
                self.trade.append([int(i['order_id']), 0, 0, 0, 0, state])
            elif state == 2:
                self.trade.append([int(i['order_id']), 0, 0, 0, 0, state])
            # print(i['instrument_id'])  # trading pair
            # float(i['fee']), int(i['size']), int(i['filled_size'])
            # init_price = float(i['price'])
            # price = float(i['price_avg'])
            print('parse order: ', i['side'], i['price'], ', deal price: ', i['price_avg'], state)
            self.queue.put([int(i['order_id']), float(i['price']), state])

    def delete_filled_orders(self, order_ids):
        self.trade.delete_filled_orders(order_ids)

    def delete_canceled_orders(self, order_ids):
        self.trade.delete_canceled_orders(order_ids)

    def get_order_by_id(self, order_id):
        return self.trade.select_order_by_id(order_id)

    def get_order_change(self):
        for item in self.queue:
            yield item[0], item[1], item[2]

    def get_changed_order(self):
        """ Caution!!! not tested well yet, if use test again

        If more than 2 orders come at the same time, only receive last order.
        Please make sure only comes one order at a time.

        need set in parse_order: self.async_result.set([int(i['order_id']), state])
        """
        state_order_id, order_state = self.async_result.get()
        self.async_result.set(gevent._util._NONE)
        return state_order_id, order_state

    def parse_trade(self, message):
        for i in message:
            print(i['side'], i['trade_id'], i['size'], i['price'])

    def show_trade_len(self):
        self.trade.print_trade_length_info()

    def parse_depth5(self, message):
        """ ticker is slow, need depth5 for high frequency
        """
        for i in message:
            timestamp = Tool.convert_time_str(i['timestamp'], TIME_PRECISION)
            price, size, number = i['asks'][0]
            best_ask, best_ask_size = float(price), float(size) * number
            price, size, number = i['bids'][0]
            best_bid, best_bid_size = float(price), float(size) * number

            self.depth = [timestamp, best_ask, best_bid, best_ask_size, best_bid_size]

    def get_depth(self):
        return self.depth
