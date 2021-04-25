#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from storage.Numpd import Numpd
from api.OkexSpotV5 import OkexSpotV5
from const import INSTRUMENT, VALUTA_IDX


class Candles(object):

    def __init__(self):
        self.spot5 = OkexSpotV5(use_trade_key=True)
        self.candles = Numpd('candles_1m.txt', 7)

    def get_latest_candles(self):
        r = self.spot5.candles(INSTRUMENT[VALUTA_IDX].upper(), '1m', limit=5)
        if 'data' in r:
            self.parse_candles(r['data'])

    def parse_candles(self, message):
        """return data sort by time from large to small
        """
        candle = self.candles.last()
        last_timestamp = int(candle[0])

        for i in reversed(message):
            timestamp = int(i[0])
            if last_timestamp < timestamp:
                i = list(map(np.float64, i))
                self.candles.append(i)