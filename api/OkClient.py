#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class OkClient(Client):

    def __init__(self):
        super().__init__()
        self.exchange_name = 'ok'

        self._f_balance = dict()
        self._ws_sub = dict()
        self._orders = dict()
        self._f_ws_sub = dict()
        self._last_kline = dict()

    def ws_kline(self, message):
        try:
            kline = message['table']
            l = len(kline) - 1
            interval = int(kline[14:l])
            message = message['data']
            for i in message:
                instrument_id = i['instrument_id']
                candle = i['candle']
                last_k = candle[0]

                data = {'exchange': self.exchange_name, 'instrument_id': instrument_id, 'interval': interval,
                        'time': last_k[0], 'open': float(last_k[1]), 'high': float(last_k[2]), 'low': float(last_k[3]),
                        'close': float(last_k[4])}
                self.strategy.ws_kline(self, data)

        except Exception as e:
            print('异常了-ws_kline', e, message)


if __name__ == '__main__':
    client = OkClient()
    instrument_info = client.f_instrument_info()
    print(instrument_info)

