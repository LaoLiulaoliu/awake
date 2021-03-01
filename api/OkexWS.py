#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import gevent
import zlib
from datetime import datetime
from websocket import WebSocketApp
from .HttpUtil import HttpUtil

# WS_URL = 'ws://echo.websocket.org/'
WS_URL = 'wss://real.okex.com:8443/ws/v3'


class OkexWS(HttpUtil):
    def __init__(self, use_trade_key=False):
        super(OkexWS, self).__init__(use_trade_key)

        self.__sub_connect = None
        self.__ws_subs = []
        self.__direct = None

    def __ws_sub_create(self):
        try:
            self.__sub_connect = WebSocketApp(WS_URL,
                                              on_message=self.on_message,
                                              on_close=self.on_close,
                                              on_error=self.on_error)
            self.__sub_connect.on_open = self.on_open
            self.__sub_connect.run_forever(ping_interval=20)
        except Exception as e:
            print('__ws_sub_create exception: {e}')
            time.sleep(5)
            self.__ws_sub_create()

    def subscription(self, sub_list):
        subs = []
        for sub in sub_list:
            if sub not in self.__ws_subs:
                subs.append(f'{sub.trade_kind}/{sub.frequency}:{sub.instrument_id}')
                self.__ws_subs.append(sub)

        if self.__sub_connect:
            self.__sub_connect.send(json.dumps({'op': 'subscribe', 'args': subs}))
        else:
            g = gevent.spawn(self.__ws_sub_create)
            g.join()

    def unsubscription(self, unsub_list):
        subs = []
        for sub in unsub_list:
            subs.append(f'{sub.trade_kind}/{sub.frequency}:{sub.instrument_id}')
            self.__ws_subs.remove(sub)
        self.__sub_connect.send(json.dumps({'op': 'unsubscribe', 'args': subs}))

    def login(self, ws):
        endpoint = '/users/self/verify'
        timestamp = self.timestamp()
        sign = self.signature(timestamp, 'GET', endpoint, '')

        sub = {'op': 'login', 'args': [self.__apikey, self.__passphrase, timestamp, sign.decode('utf-8')]}
        return ws.send(json.dumps(sub))

    def on_open(self):
        print('ws_on_open', self.__ws_subs)
        self.login(self.__sub_connect)
        time.sleep(0.1)

        subs = [f'{sub.trade_kind}/{sub.frequency}:{sub.instrument_id}' for sub in self.__ws_subs]
        self.__sub_connect.send(json.dumps({'op': 'subscribe', 'args': subs}))

    def on_error(self, error):
        print('ws_on_error', self.__sub_connect, error)

    def on_close(self):
        print('ws_on_close', self.__sub_connect, self.__ws_subs)
        self.__sub_connect = None

    def on_message(self, message):
        data = json.loads(self.inflate(message))
        print('ws_on_message', data)
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
            if data['event'] == 'login':
                subs = [f'{sub.trade_kind}/{sub.frequency}:{sub.instrument_id}' for sub in self.__ws_subs]
                self.__sub_connect.send(json.dumps({'op': 'subscribe', 'args': subs}))

    def inflate(self, data):
        decompress = zlib.decompressobj(
            -zlib.MAX_WBITS
        )
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated
