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

    def ws_ticker(self, message):
        try:
            for i in message:
                instrument_id = i['instrument_id']
                data = {'instrument_id': instrument_id, 'last': i['last'], 'bid': i['best_bid'], 'ask': i['best_ask'],
                        'time': i['timestamp']}
                self.strategy.ws_ticker(self, data)
        except Exception as e:
            print('异常了-ws_ticker', e, message)

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

    def ws_order(self, message):
        try:
            for i in message:
                instrument_id = i['instrument_id']
                order_id = i['order_id']
                status = self.__status[i['state']]
                side = i['type']
                side = self.__trade_side[side]
                amount = int(i['size'])
                filled_amount = int(i['filled_qty'])
                fee = float(i['fee'])
                init_price = float(i['price'])
                price = float(i['price_avg'])
                client_oid = i['client_oid']

                data = {'instrument_id': instrument_id, 'order_id': order_id, 'status': status, 'side': side,
                        'amount': amount, 'filled_amount': filled_amount, 'price': price, 'init_price': init_price,
                        'fee': fee, 'client_oid': client_oid}
                self._orders[instrument_id] = data
                self.strategy.ws_order(self, data)
        except Exception as e:
            print('异常了-ws_order', e, message)

    def ws_account(self, message):
        try:
            for i in message:
                for k, v in i.items():
                    contracts = v['contracts']
                    for avail in contracts:
                        self._f_balance[k] = float(avail['available_qty'])
                        # do something
            print('ws_account', self._f_balance)
        except Exception as e:
            print('异常了--ws_account', e, message)

    def get_instrument_id(self, instruments, symbol, contract_type):
        for instrument in instruments:
            if instrument['symbol'] == symbol and instrument['contract_type' == contract_type]:
                return instrument['instrument_id']


if __name__ == '__main__':
    client = OkClient()
    instrument_info = client.f_instrument_info()
    print(instrument_info)

