#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import base64
import datetime
import hmac
import json
import requests
import threading
import time
import zlib

from retrying import retry
from websocket import WebSocketApp

CONTENT_TYPE = 'Content-Type'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'
APPLICATION_JSON = 'application/json'
BASE_URL = 'https://www.okex.com'
# WS_URL = 'ws://echo.websocket.org/'
WS_URL = 'wss://real.okex.com:8443/ws/v3'
API_KEY = ''
SECRET_KEY = ''
PASS_PHRASE = ''


class OkAPI:

    def __init__(self, client):

        self.client = client
        self.__baseUrl = BASE_URL
        self.__apikey = API_KEY
        self.__secretkey = SECRET_KEY
        self.__passphrase = PASS_PHRASE
        self.__sub_connect = None  # 订阅连接
        self.__ws_subs = []
        self.__direct = None

    def get_header(self, api_key, sign, timestamp, passphrase):
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = api_key
        header[OK_ACCESS_SIGN] = sign
        header[OK_ACCESS_TIMESTAMP] = str(timestamp)
        header[OK_ACCESS_PASSPHRASE] = passphrase
        return header

    def parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'
        return url[0:-1]

    def timestamp(self):
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        timestamp = timestamp[0:-3] + 'Z'
        return timestamp

    def transfer(self, instrument_id, fund, amount):

        path = '/api/account/v3/transfer'
        params = {'currency': fund, 'amount': amount, 'from': '1', 'to': '5',
                  'instrument_id': '{}-{}'.format(instrument_id, fund)}
        return self.httpPost(path, params)

    # -----------------------------交割合约api-----------------------------
    def f_ticker(self, instrument_id):
        path = '/api/futures/v3/instruments/{}/ticker'.format(instrument_id)
        return self.httpGet(path)

    def f_depth(self, instrument_id):
        path = '/api/futures/v3/instruments/{}/book'.format(instrument_id)
        params = {'instrument_id': instrument_id, 'size': 10}
        return self.httpGet(path, params)

    def f_position(self, instrument_id=None):
        path = '/api/futures/v3/{}/position'.format(instrument_id) if instrument_id else '/api/futures/v3/position'
        return self.httpGet(path)

    def f_instruments(self):
        path = '/api/futures/v3/instruments'
        return self.httpGet(path)

    def f_trade(self, instrument_id, side, price, amount, client_oid=''):
        path = '/api/futures/v3/order'
        params = {'instrument_id': instrument_id, 'type': side, 'price': price, 'size': amount, 'match_price': '0',
                  'client_oid': client_oid}
        return self.httpPost(path, params)

    def f_order_info(self, instrument_id, client_oid):
        path = '/api/futures/v3/orders/{}/{}'.format(instrument_id, client_oid)
        return self.httpGet(path)

    def f_kline(self, instrument_id, interval, end=''):
        path = '/api/futures/v3/instruments/{}/candles'.format(instrument_id)
        params = {'granularity': interval, 'end': end}
        return self.httpGet(path, params)

    def f_account(self, instrument_id):
        path = '/api/futures/v3/accounts/{}'.format(instrument_id)
        return self.httpGet(path)

    def f_cancel_order(self, instrument_id, client_oid):
        path = '/api/futures/v3/cancel_order/{}/{}'.format(instrument_id, client_oid)
        params = {'instrument_id': instrument_id, 'client_oid': client_oid}
        return self.httpPost(path, params)

    # -----------------------------永续合约api-----------------------------
    def sf_ticker(self, instrument_id):
        path = '/api/swap/v3/instruments/{}/ticker'.format(instrument_id)
        return self.httpGet(path)

    def sf_position(self, instrument_id=None):
        path = '/api/swap/v3/{}/position'.format(instrument_id) if instrument_id else '/api/swap/v3/position'
        return self.httpGet(path)

    def sf_trade(self, instrument_id, side, price, amount, client_oid=''):
        path = '/api/swap/v3/order'
        params = {'instrument_id': instrument_id, 'type': side, 'price': price, 'size': amount, 'match_price': '0',
                  'client_oid': client_oid}
        return self.httpPost(path, params)

    def sf_kline(self, instrument_id, interval, end=''):
        path = '/api/swap/v3/instruments/{}/candles'.format(instrument_id)
        params = {'granularity': interval, 'end': end}
        return self.httpGet(path, params)

    def sf_cancel_order(self, instrument_id, client_oid):
        path = '/api/swap/v3/cancel_order/{}/{}'.format(instrument_id, client_oid)
        params = {'instrument_id': instrument_id, 'client_oid': client_oid}
        return self.httpPost(path, params)

    # -----------------------------币币杠杆api-----------------------------
    def l_trade(self, side, instrument_id, price, amount):
        path = '/api/margin/v3/orders'
        params = {'type': 'limit', 'side': side, 'instrument_id': instrument_id, 'size': amount, 'price': price,
                  'margin_trading': 2}
        return self.httpPost(path, params)

    def l_borrow(self, instrument_id, currency, amount):
        path = '/api/margin/v3/accounts/borrow'
        params = {'instrument_id': instrument_id, 'currency': currency, 'amount': amount}
        return self.httpPost(path, params)

    def l_borrowed(self, instrument_id, status=0):
        path = '/api/margin/v3/accounts/{}/borrowed'.format(instrument_id)
        params = {'status': status}
        return self.httpGet(path, params)

    def l_repay(self, instrument_id, currency, amount, borrow_id=None):
        path = '/api/margin/v3/accounts/repayment'
        params = {'instrument_id': instrument_id, 'currency': currency, 'amount': str(amount)}
        if borrow_id:
            params['borrow_id'] = borrow_id
        return self.httpPost(path, params)

    def l_order(self, instrument_id, orderid):
        path = '/api/margin/v3/orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.httpGet(path, params)

    def l_accounts(self):
        path = '/api/margin/v3/accounts'
        return self.httpGet(path)

    def l_account(self, instrument_id):
        path = '/api/margin/v3/accounts/' + instrument_id
        return self.httpGet(path)

    def l_availability(self, instrument_id):
        path = '/api/margin/v3/accounts/{}/availability'.format(instrument_id)
        return self.httpGet(path)

    def l_cancel_order(self, instrument_id, orderid):
        path = '/api/margin/v3/cancel_orders/' + orderid
        params = {'instrument_id': instrument_id, 'order_id': orderid}
        return self.httpPost(path, params)

    def httpDelete(self, path, data):
        if data:
            path = path + self.parse_params_to_str(data)
        url = self.__baseUrl + path
        timestamp = self.timestamp()
        header = self.get_header(self.__apikey, self.signature(timestamp, 'DELETE', path, '', self.__secretkey),
                                 timestamp, self.__passphrase)
        try:
            response = requests.delete(url, headers=header)
        except Exception as e:
            raise Exception(e)

        return response.json()


    def on_message(self, message):
        data = json.loads(self.inflate(message))
        print('ok_on_message', data)
        if 'table' in data:
            table = data['table']
            if table.find('spot/ticker') != -1:
                self.client.ws_ticker(data['data'])
            elif table.find('futures/ticker') != -1:
                self.client.ws_f_ticker(data['data'])
            elif table.find('spot/candle') != -1:
                self.client.ws_kline(data)
            elif table.find('futures/candle') != -1:
                self.client.ws_f_kline(data)
            elif table.find('swap/candle') != -1:
                self.client.ws_sf_kline(data)
            elif table.find('spot/trade') != -1:
                self.client.ws_trade(data['data'])
            elif table.find('spot/account') != -1:
                self.client.ws_account(data['data'])
            elif table.find('spot/margin_account') != -1:
                self.client.ws_l_account(data['data'])
            elif table.find('futures/account') != -1:
                self.client.ws_f_account(data['data'])
            elif table.find('swap/account') != -1:
                self.client.ws_sf_account(data['data'])
            elif table.find('spot/order') != -1:
                self.client.ws_order(data['data'])
            elif table.find('futures/order') != -1:
                self.client.ws_f_order(data['data'])
            elif table.find('swap/order') != -1:
                self.client.ws_sf_order(data['data'])
            elif table.find('futures/position') != -1:
                self.client.ws_f_position(data['data'])
            elif table.find('swap/position') != -1:
                self.client.ws_sf_position(data['data'])
            elif table.find('depth') != -1:
                self.client.ws_depth(data['data'])
            elif table.find('depth5') != -1:
                pass

        elif 'event' in data:
            print(data)
            if data['event'] == 'login':
                s = []
                for sub_config in self.__ws_subs:
                    s.append('{}/{}:{}'.format(sub_config.trade_kind, sub_config.frequency,
                                               sub_config.instrument_id))
                self.__sub_connect.send(json.dumps({'op': 'subscribe', 'args': s}))


if __name__ == '__main__':
    from exchange.SubConfig import SubConfig
    from common.Common import Common

    o = OkAPI('')
    # o.__ws_sub_create()
    # ins = o.f_instruments()
    ins = o.f_ticker("XRP-USD-200925")
    print(ins)
    sub_list = []
    sub_config = SubConfig(Common.futures, "XRP-USD-200925", "", Common.frequency_tick)
    sub_list.append(sub_config)
    o.ws_sub(sub_list)

