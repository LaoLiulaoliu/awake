#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gevent.lock
from .HttpUtil import HttpUtil
from const import INSTRUMENT


class OkexSpotV5(object):
    __sem = gevent.lock.BoundedSemaphore(1)

    def __new__(cls, *args, **kwargs):
        if not hasattr(OkexSpotV5, '_instance'):
            with OkexSpotV5.__sem:
                if not hasattr(OkexSpotV5, '_instance'):
                    OkexSpotV5._instance = object.__new__(cls)
        return OkexSpotV5._instance

    def __init__(self, use_trade_key=False):
        self.http = HttpUtil(use_trade_key, version=5)

    def get_server_time(self):
        """
        {"ts":"1597026383085"}
        """
        endpoint = 'api/v5/public/time'
        data = self.http.httpGet(endpoint)
        print(data['data'][0]['ts'])

    def kline(self, instrument_id, bar='15m', before='', after=''):
        """  Maximum of 1440 latest entries
        param instrument_id: need uppercase
        param bar: [1m/3m/5m/15m/30m/1H/2H/4H/6H/12H/1D/1W/1M/3M/6M/1Y]
        """
        path = '/api/v5/market/candles'
        params = {'instId': instrument_id, 'bar': bar}
        if before:
            params['before'] = before
        if after:
            params['after'] = before
        return self.http.httpGet(path, params)

    def kline_history(self, instrument_id, bar='15m', before='', after=''):
        """ historical candels of 9 major currencies are provided: BTC, ETH, LTC, ETC, XRP, EOS, BCH, BSV, TRX.
        """
        path = '/api/v5/market/history-candles'
        params = {'instId': instrument_id, 'bar': bar}
        if before:
            params['before'] = before
        if after:
            params['after'] = before
        return self.http.httpGet(path, params)



def print_error_or_get_order_id(ret):
    if 'error_code' in ret and ret['error_code'] != '0':
        print(ret)
        return 0
    else:
        return int(ret['order_id'])


if __name__ == '__main__':
    VALUTA_IDX = 0
    spot = OkexSpotV5()
