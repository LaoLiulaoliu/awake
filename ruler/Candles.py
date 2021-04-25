#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Zhurong import Zhurong
from api.OkexSpotV5 import OkexSpotV5
from const import INSTRUMENT, VALUTA_IDX


class Candles(object):

    def __init__(self):
        self.spot5 = OkexSpotV5(use_trade_key=True)
        self.candles = Zhurong('candles_1m.txt')

    def get_latest_candles(self):
        r = self.spot5.candles(INSTRUMENT[VALUTA_IDX].upper(), '1m', limit=5)
        if 'data' in r:
            self.parse_candles(r['data'])

    def parse_candles(self, message):
        """return data sort by time from large to small
        """
        candle = self.candles.last()
        last_timestamp = candle[0]

        for i in reversed(message):
            timestamp = int(i[0])
            if last_timestamp < timestamp:
                self.candles.append([timestamp] + list(map(np.float64, i[1:])))