#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from HttpUtil import HttpUtil

class OkexSpot(object):
    """ 币币api
    """

    def __init__(self):
        self.http = HttpUtil()

    def get_server_time(self):
        """
        {'iso': '2021-02-18T08:50:44.924Z', 'epoch': '1613638244.924'}
        """
        endpoint = '/api/general/v3/time'
        data = self.http.httpGet(endpoint)
        print(data)

    def instruments(self):
        """ lots of this kind of data
		{
		  "base_currency": "BTC",
		  "category": "1",
		  "instrument_id": "BTC-USDT",
		  "min_size": "0.0001",
		  "quote_currency": "USDT",
		  "size_increment": "0.00000001",
		  "tick_size": "0.1"
		}
        """
        path = '/api/spot/v3/instruments'
        return self.http.httpGet(path)

    def account(self, currency=None):
        """ instrument_id
        BTC: {'frozen': '0', 'hold': '0', 'id': '', 'currency': 'BTC', 'balance': '0.0067287', 'available': '0.0067287', 'holds': '0'}
        USDT: {'frozen': '0', 'hold': '0', 'id': '', 'currency': 'USDT', 'balance': '0.00027828', 'available': '0.00027828', 'holds': '0'}
        """
        path = '/api/spot/v3/accounts/' + currency if currency else '/api/spot/v3/accounts/'
        return self.http.httpGet(path)

    def tickers(self, symbol=None):
        """OKCOIN all currency conversion current bid data
        """
        endpoint = '/api/spot/v3/instruments/ticker'
        params = {'symbol': symbol} if symbol else None

        return self.http.httpGet(endpoint, params)

    def ticker(self, instrument_id='BTC-USDT'):
        """
		{
		  "best_ask": "51846.7",
		  "best_bid": "51846.6",
		  "instrument_id": "BTC-USDT",
		  "open_utc0": "52116",
		  "open_utc8": "51150.3",
		  "product_id": "BTC-USDT",
		  "last": "51840.1",
		  "last_qty": "0.0006",
		  "ask": "51846.7",
		  "best_ask_size": "0.04177949",
		  "bid": "51846.6",
		  "best_bid_size": "0.00943893",
		  "open_24h": "50610.7",
		  "high_24h": "52617.9",
		  "low_24h": "50522.9",
		  "base_volume_24h": "8952.40823458",
		  "timestamp": "2021-02-18T07:15:38.435Z",
		  "quote_volume_24h": "461411588.69765782"
		}
        """
        path = '/api/spot/v3/instruments/{}/ticker'.format(instrument_id)
        return self.http.httpGet(path)

    def trade(self, side, instrument_id, price, amount):
        path = '/api/spot/v3/orders'
        params = {'type': 'limit', 'side': side, 'instrument_id': instrument_id, 'size': amount, 'price': price,
                  'margin_trading': 1}
        return self.http.httpPost(path, params)

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

    def cancel_order(self, instrument_id, orderid):
        path = '/api/spot/v3/cancel_orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.http.httpPost(path, params)



if __name__ == '__main__':
    client = OkexSpot()
    print( client.ticker('BTC-USDT') )
    print(client.orders())
