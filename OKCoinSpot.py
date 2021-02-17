#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from secret import *

from HttpMD5Util import HttpMD5Util

class OKCoinSpot(object):
    """ 币币api
    """

    def __init__(self):
        self.http = HttpMD5Util()

    def get_server_time(self):
        endpoint = '/api/general/v3/time'
        data = self.http.httpGet(endpoint)
        print(data)

    def tickers(self, symbol=''):
        """获取OKCOIN现货行情信息
        """
        endpoint = '/api/spot/v3/instruments/ticker'
        params=''
        if symbol:
            params = 'symbol=%(symbol)s' %{'symbol':symbol}

        return self.http.httpGet(endpoint, params)

    def ticker(self, instrument_id):
        path = '/api/spot/v3/instruments/{}/ticker'.format(instrument_id)
        return self.http.httpGet(path)

    def instruments(self):
        path = '/api/spot/v3/instruments'
        return self.http.httpGet(path)

    def trade(self, side, instrument_id, price, amount):
        path = '/api/spot/v3/orders'
        params = {'type': 'limit', 'side': side, 'instrument_id': instrument_id, 'size': amount, 'price': price,
                  'margin_trading': 1}
        return self.httpPost(path, params)

    def order(self, instrument_id, orderid):
        path = '/api/spot/v3/orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.http.httpGet(path, params)

    def orders(self):
        path = '/api/spot/v3/orders_pending'
        return self.http.httpGet(path)

    def kline(self, instrument_id, interval, start='', end=''):
        path = '/api/spot/v3/instruments/{}/candles'.format(instrument_id)
        params = {'granularity': interval, 'start': start, 'end': end}
        return self.http.httpGet(path, params)

    def account(self, instrument_id):
        path = '/api/spot/v3/accounts/' + instrument_id
        return self.http.httpGet(path)

    def cancel_order(self, instrument_id, orderid):
        path = '/api/spot/v3/cancel_orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.http.httpPost(path, params)

if __name__ == '__main__':
    client = OKCoinSpot()
    #client.get_server_time()
    client.ticker('btc_usd')
