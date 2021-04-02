#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import zlib
from datetime import datetime
from websocket import WebSocketApp
from .HttpUtil import HttpUtil
from .tradesecret import *

WS_PUBLIC = 'wss://wsaws.okex.com:8443/ws/v5/public'
WS_PRIVATE = 'wss://wsaws.okex.com:8443/ws/v5/private'


class OkexWSV5(HttpUtil):
    def __init__(self, sub_list, state, use_trade_key=True, channel='private'):
        super(OkexWSV5, self).__init__(use_trade_key, 5)

        self.__connection = None
        self.__ws_subs = []  # 'spot/ticker:BTC-USDT'
        if isinstance(sub_list, list):
            self.__ws_subs = [sub for sub in sub_list if sub not in self.__ws_subs]

        self.state = state

        self.__apikey = apikey
        self.__secretkey = secretkey
        self.__passphrase = passphrase

        self.ws_url = WS_PRIVATE if channel == 'private' else WS_PUBLIC

    def ws_create(self):
        try:
            self.__connection = WebSocketApp(self.ws_url,
                                             on_message=self.on_message,
                                             on_close=self.on_close,
                                             on_error=self.on_error)

            self.__connection.on_open = self.on_open
            self.__connection.run_forever(ping_interval=28, ping_timeout=28)
        except Exception as e:
            print(f'ws_create exception: {e}')
            time.sleep(5)
            self.ws_create()

    def subscription(self, sub_list):
        subs = [sub for sub in sub_list if sub not in self.__ws_subs]
        self.__ws_subs.extend(subs)

        if self.__connection:
            args = []
            for i in subs:
                channel, instId = i.split('/')
                args.append({'channel': channel, 'instId': instId})
            self.__connection.send(json.dumps({'op': 'subscribe', 'args': args}))

    def unsubscription(self, unsub_list):
        subs = [sub for sub in unsub_list if sub in self.__ws_subs]

        args = []
        for i in subs:
            channel, instId = i.split('/')
            args.append({'channel': channel, 'instId': instId})
            self.__ws_subs.remove(i)
        self.__connection.send(json.dumps({'op': 'unsubscribe', 'args': args}))

    def login(self):
        endpoint = '/users/self/verify'
        timestamp = str(round(datetime.now().timestamp(), 3))
        sign = self.signature(timestamp, 'GET', endpoint, '')

        sub = {'op': 'login',
               'args': {'apiKey': self.__apikey, 'passphrase': self.__passphrase,
                        'timestamp': timestamp, 'sign': sign.decode('utf-8')}}
        return self.__connection.send(json.dumps(sub))

    def on_open(self):
        print('ws_on_open: ', self.__ws_subs)
        self.login()
        time.sleep(0.1)

        args = []
        for i in self.__ws_subs:
            channel, instId = i.split('/')
            args.append({'channel': channel, 'instId': instId})
        self.__connection.send(json.dumps({'op': 'subscribe', 'args': args}))

    def on_error(self, error):
        """ If reconnect, on_open after create.
        ws_on_error:  <websocket._app.WebSocketApp object at 0x7f15f860ce50> Connection is already closed.
        ws_on_open:  ['spot/ticker:ALPHA-USDT']
        """
        print('ws_on_error: ', self.__connection, error)
        self.ws_create()
        print('ws_on_error reconnected which will not be print.', time.time())

    def on_close(self):
        """ error occure before close
        ws_on_error <websocket._app.WebSocketApp object at 0x7f69baf2be80> Connection is already closed.
        ws_on_close <websocket._app.WebSocketApp object at 0x7f69baf2be80> ['spot/ticker:ALPHA-USDT']
        """
        print('ws_on_close', self.__connection, self.__ws_subs)
        self.ws_create()
        print(f'on close reconnect, connection: {self.__connection}')

    def on_message(self, message):
        data = json.loads(self.inflate(message))
        if 'table' in data:
            table = data['table']
            if table == 'spot/ticker':
                # [{'last': '49338.5', 'open_24h': '47991.9', 'best_bid': '49326.7', 'high_24h': '50210.1', 'low_24h': '47907.2', 'open_utc0': '49597.5', 'open_utc8': '49188.4', 'base_volume_24h': '9467.36886712', 'quote_volume_24h': '462894723.35643254', 'best_ask': '49326.8', 'instrument_id': 'BTC-USDT', 'timestamp': '2021-03-02T14:15:12.522Z', 'best_bid_size': '0.56306288', 'best_ask_size': '0.13743411', 'last_qty': '0.0089648'}]
                self.state.parse_ticker(data['data'])
            elif table == 'spot/account':
                # push update data, sometimes have duplicated data
                self.state.parse_account(data['data'])
            elif table == 'spot/order':
                self.state.parse_order(data['data'])
            elif table == 'spot/depth5':
                self.state.parse_depth5(data['data'])
            elif table == 'spot/depth':  # Public-Depth400
                print(data['action'], data['data'])
            elif table == 'spot/depth_l2_tbt':
                print(data['action'], data['data'])
            elif table == 'spot/candle60s':
                # [{'candle': ['2021-03-20T06:18:00.000Z', '58219.7', '58222.4', '58212.8', '58222.4', '0.14625923'], 'instrument_id': 'BTC-USDT'}]
                # data is pushed every 500ms, will duplicated in one minute.
                print(data['data'])
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
