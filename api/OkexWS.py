#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import gevent
import zlib
from datetime import datetime
from websocket import WebSocketApp
from .HttpUtil import HttpUtil

WS_URL = 'wss://real.okex.com:8443/ws/v3'


class OkexWS(HttpUtil):
    def __init__(self, use_trade_key=False):
        super(OkexWS, self).__init__(use_trade_key)

        self.__connection = None
        self.__ws_subs = []

    def ws_create(self, run_in_background=False):
        try:
            self.__connection = WebSocketApp(WS_URL,
                                              on_message=self.on_message,
                                              on_close=self.on_close,
                                              on_error=self.on_error)
            self.__connection.on_open = self.on_open
            if run_in_background:
                g = gevent.spawn(self.ws_create, True)
                g.join()
            else:
                self.__connection.run_forever(ping_interval=20)
        except Exception as e:
            print(f'ws_create exception: {e}')
            time.sleep(5)
            self.ws_create()

    def subscription(self, sub_list):
        subs = []
        for sub in sub_list:
            if sub not in self.__ws_subs:
                subs.append(sub)
                self.__ws_subs.append(sub)

        if self.__connection:
            self.__connection.send(json.dumps({'op': 'subscribe', 'args': subs}))

    def unsubscription(self, unsub_list):
        subs = []
        for sub in unsub_list:
            subs.append(sub)
            self.__ws_subs.remove(sub)
        self.__connection.send(json.dumps({'op': 'unsubscribe', 'args': subs}))

    def login(self):
        endpoint = '/users/self/verify'
        timestamp = self.timestamp()
        sign = self.signature(timestamp, 'GET', endpoint, '')

        sub = {'op': 'login', 'args': [self.__apikey, self.__passphrase, timestamp, sign.decode('utf-8')]}
        return self.__connection.send(json.dumps(sub))

    def on_open(self):
        print('ws_on_open', self.__ws_subs)
        print('on_open login: ', self.login())
        time.sleep(0.1)

        self.__connection.send(json.dumps({'op': 'subscribe', 'args': self.__ws_subs}))

    def on_error(self, error):
        print('ws_on_error', self.__connection, error)

    def on_close(self):
        print('ws_on_close', self.__connection, self.__ws_subs)
        self.__connection = None

    def on_message(self, message):
        data = json.loads(self.inflate(message))
        print('ws_on_message', data)
        if 'table' in data:
            table = data['table']
            if table.find('spot/ticker') != -1:
                self.client.ws_ticker(data['data'])
            elif table.find('spot/candle') != -1:
                self.client.ws_kline(data)
            elif table.find('spot/trade') != -1:
                self.client.ws_trade(data['data'])
            elif table.find('spot/account') != -1:
                self.client.ws_account(data['data'])
            elif table.find('spot/order') != -1:
                self.client.ws_order(data['data'])
            elif table.find('depth') != -1:
                self.client.ws_depth(data['data'])
            elif table.find('depth5') != -1:
                pass

        elif 'event' in data:
            if data['event'] == 'login':
                self.__connection.send(json.dumps({'op': 'subscribe', 'args': self.__ws_subs}))

    def inflate(self, data):
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated
