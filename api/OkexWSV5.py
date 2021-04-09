#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import zlib
from datetime import datetime
from websocket import WebSocketApp
from .HttpUtil import HttpUtil
from .tradesecret import *

WS_PUBLIC = 'wss://ws.okex.com:8443/ws/v5/public'
WS_PRIVATE = 'wss://ws.okex.com:8443/ws/v5/private'


class OkexWSV5(HttpUtil):
    def __init__(self, sub_dict_list, state, use_trade_key=True, channel='private'):
        super(OkexWSV5, self).__init__(use_trade_key, 5)

        self.__connection = None
        self.__ws_subs = []
        if isinstance(sub_dict_list, list):
            self.__ws_subs = sub_dict_list

        self.state = state

        self.__apikey = apikey
        self.__secretkey = secretkey
        self.__passphrase = passphrase

        self.channel = channel
        self.ws_url = WS_PRIVATE if channel == 'private' else WS_PUBLIC

    def ws_create(self):
        try:
            self.__connection = WebSocketApp(self.ws_url,
                                             on_message=self.on_message,
                                             on_close=self.on_close,
                                             on_error=self.on_error)

            self.__connection.on_open = self.on_open
            self.__connection.run_forever(ping_interval=28, ping_timeout=27)  # Ensure ping_interval > ping_timeout
        except Exception as e:
            print(f'ws_create exception: {e}')
            time.sleep(5)
            self.ws_create()

    def subscription(self, sub_dict_list):
        if self.__connection:
            self.__ws_subs.extend(sub_dict_list)
            self.__connection.send(json.dumps({'op': 'subscribe', 'args': sub_dict_list}))

    def unsubscription(self, unsub_dict_list):
        for i in unsub_dict_list:
            self.__ws_subs.remove(i)
        self.__connection.send(json.dumps({'op': 'unsubscribe', 'args': unsub_dict_list}))

    def login(self):
        endpoint = '/users/self/verify'
        timestamp = str(round(time.time(), 3))
        sign = self.signature(timestamp, 'GET', endpoint, '')

        sub = {'op': 'login',
               'args': {'apiKey': self.__apikey, 'passphrase': self.__passphrase,
                        'timestamp': timestamp, 'sign': sign.decode('utf-8')}}
        return self.__connection.send(json.dumps(sub))

    def on_open(self):
        print('ws_on_open: ', self.__ws_subs)
        if self.channel == 'private':
            self.login()
        time.sleep(0.1)

        self.__connection.send(json.dumps({'op': 'subscribe', 'args': self.__ws_subs}))

    def on_error(self, error):
        """ If reconnect, on_open after create.
        ws_on_error:  <websocket._app.WebSocketApp object at 0x7fd942687f40> [Errno 104] Connection reset by peer
        ws_on_open:  [{'channel': 'tickers', 'instId': 'ALPHA-USDT'}]
        """
        print('ws_on_error: ', int(time.time()), self.__connection, error)
        self.ws_create()
        print('ws_on_error reconnected which will not be print.')

    def on_close(self):
        """ error occure before close
        """
        print('ws_on_close', int(time.time()), self.__connection, self.__ws_subs)
        self.ws_create()
        print(f'on close reconnect, connection: {self.__connection}')

    def on_message(self, message):
        data = json.loads(message)
        if 'data' in data:
            channel = data['arg']['channel']
            if channel == 'tickers':
                self.state.parse_ticker_v5(data['data'])
            elif channel == 'account':
                self.state.parse_account_v5(data['data'])
            elif channel == 'orders':
                self.state.parse_order_v5(data['data'])
            elif channel == 'spot/depth5':
                self.state.parse_depth5_v5(data['data'])
            elif channel == 'spot/depth':  # Public-Depth400
                print(data['action'], data['data'])
            elif channel == 'spot/depth_l2_tbt':
                print(data['action'], data['data'])
            elif channel == 'spot/candle60s':
                # [{'candle': ['2021-03-20T06:18:00.000Z', '58219.7', '58222.4', '58212.8', '58222.4', '0.14625923'], 'instrument_id': 'BTC-USDT'}]
                # data is pushed every 500ms, will duplicated in one minute.
                print(data['data'])
            elif channel == 'spot/trade':
                # push filled orders on the whole market - public
                self.state.parse_trade_v5(data['data'])
            else:
                print('ws_on_message:table: ', data)

        elif 'event' in data:
            if data['event'] == 'login':
                print('event login success: ', data['code'])
            elif data['event'] == 'subscribe':
                print('event subscribe channel: ', data['arg'])
            elif data['event'] == 'unsubscribe':
                print('event unsubscribe channel: ', data['arg'])
            elif data['event'] == 'error':
                print('event error: ', data['code'], data['msg'])
