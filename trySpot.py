#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from secret import *

from HttpMD5Util import HttpMD5Util

class OKCoinSpot(object):

    def __init__(self, url, apikey, secretkey):
        self.__url = url
        self.__apikey = apikey
        self.__secretkey = secretkey
        self.http = HttpMD5Util()

    def get_server_time(self):
        endpoint = '/api/general/v3/time'
        params = ''
        data = self.http.httpGet(self.__url, endpoint, params)
        print(data)

    #获取OKCOIN现货行情信息
    def ticker(self, symbol = ''):
        TICKER_RESOURCE = "/api/spot/v3/instruments/ticker"
        params=''
        if symbol:
            params = 'symbol=%(symbol)s' %{'symbol':symbol}
        print(self.__url + TICKER_RESOURCE)
        return self.http.httpGet(self.__url + TICKER_RESOURCE,params)

if __name__ == '__main__':
    client = OKCoinSpot(BASE_URL, API_KEY, SECRET_KEY)
    client.ticker('btc_usd')
    client.get_server_time()
