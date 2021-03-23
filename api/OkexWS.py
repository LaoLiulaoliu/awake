#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import zlib
from datetime import datetime
from websocket import WebSocketApp
from .HttpUtil import HttpUtil
from .secret import *
from .tradesecret import *

WS_URL = 'wss://real.okex.com:8443/ws/v3'


class OkexWS(HttpUtil):
    def __init__(self, sub_list, state, use_trade_key=False):
        super(OkexWS, self).__init__(use_trade_key)

        self.__connection = None
        self.__ws_subs = []  # 'spot/ticker:BTC-USDT'
        if isinstance(sub_list, list):
            self.__ws_subs = [sub for sub in sub_list if sub not in self.__ws_subs]

        self.state = state
        self.use_trade_key = use_trade_key

        if use_trade_key:
            self.__apikey = apikey
            self.__secretkey = secretkey
            self.__passphrase = passphrase
        else:
            self.__apikey = API_KEY
            self.__secretkey = SECRET_KEY
            self.__passphrase = PASS_PHRASE

    def ws_create(self):
        try:
            self.__connection = WebSocketApp(WS_URL,
                                              on_message=self.on_message,
                                              on_close=self.on_close,
                                              on_error=self.on_error)
            if self.use_trade_key:
                self.__connection.on_open = self.on_open
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
        timestamp = str(round(datetime.now().timestamp(), 3))
        sign = self.signature(timestamp, 'GET', endpoint, '')

        sub = {'op': 'login', 'args': [self.__apikey, self.__passphrase, timestamp, sign.decode('utf-8')]}
        return self.__connection.send(json.dumps(sub))

    def on_open(self):
        print('ws_on_open: ', self.__ws_subs)
        self.login()
        time.sleep(0.1)

        self.__connection.send(json.dumps({'op': 'subscribe', 'args': self.__ws_subs}))

    def on_error(self, error):
        print('ws_on_error', self.__connection, error)

    def on_close(self):
        print('ws_on_close', self.__connection, self.__ws_subs)
        self.__connection = None

    def on_message(self, message):
        data = json.loads(self.inflate(message))
        if 'table' in data:
            table = data['table']
            if table == 'spot/ticker':
                # [{'last': '49338.5', 'open_24h': '47991.9', 'best_bid': '49326.7', 'high_24h': '50210.1', 'low_24h': '47907.2', 'open_utc0': '49597.5', 'open_utc8': '49188.4', 'base_volume_24h': '9467.36886712', 'quote_volume_24h': '462894723.35643254', 'best_ask': '49326.8', 'instrument_id': 'BTC-USDT', 'timestamp': '2021-03-02T14:15:12.522Z', 'best_bid_size': '0.56306288', 'best_ask_size': '0.13743411', 'last_qty': '0.0089648'}]
                self.state.parse_ticker(data['data'])
            elif table == 'spot/depth':
                print(data['action'], data['data'])
            elif table == 'spot/depth5':
                print(data['data'])
            elif table == 'spot/depth_l2_tbt':
                print(data['action'], data['data'])
            elif table == 'spot/candle60s':
                # [{'candle': ['2021-03-20T06:18:00.000Z', '58219.7', '58222.4', '58212.8', '58222.4', '0.14625923'], 'instrument_id': 'BTC-USDT'}]
                # data is pushed every 500ms, will duplicated in one minute.
                print(data['data'])
            elif table == 'spot/account':
                # push update data, sometimes have duplicated data
                print('account: ', data['data'])
            elif table == 'spot/order':
                print('order: ', data['data'])
            elif table == 'spot/order_algo':
                print('order_algo: ', data['data'])
            elif table == 'spot/trade':
                # push filled orders on the whole market - public
                self.state.parse_trade(data['data'])
            else:
                print('ws_on_message:table: ', data)

        elif 'event' in data:
            if data['event'] == 'login':
                print('event login success: ', data['success'])
            elif data['event'] == 'subscribe':
                print('event subscribe channel: ', data['channel'])
            elif data['event'] == 'error':
                print('event error: ', data['errorCode'], data['message'])

    def inflate(self, data):
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        inflated = decompress.decompress(data)
        inflated += decompress.flush()
        return inflated
