#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Zhurong import Zhurong
from api.OkexSpotV5 import OkexSpotV5


class Candles(object):

    def __init__(self, fname):
        self.spot5 = OkexSpotV5(use_trade_key=True)
        self.candles = Zhurong(fname)

    def get_latest_candles(self, instrument_id, bar, limit):
        r = self.spot5.candles(instrument_id, bar, limit=limit)
        if 'data' in r:
            self.parse_candles(r['data'])

    def parse_candles(self, message):
        """return data sort by time from large to small
        """
        candle = self.candles.last()
        last_timestamp = candle[0] if candle else 0

        for i in reversed(message):
            timestamp = int(i[0])
            if last_timestamp < timestamp:
                self.candles.append([timestamp] + list(map(np.float64, i[1:])))