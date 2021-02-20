#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .HttpUtil import HttpUtil

INSTRUMENT = 'btc-usdt'  # 0 index


class OkexSpot(object):
    """ 币币api
    """

    def __init__(self, use_trade_key=False):
        self.http = HttpUtil(use_trade_key)

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

    def ticker(self, instrument_id=INSTRUMENT):
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
        try:
            return self.http.httpGet(path)
        except Exception as e:
            print(f'OkexSpot::ticker exception is: {e}')
            self.http.break_and_connect()
            return

    def place_order(self, side, instrument_id, price, size):
        path = '/api/spot/v3/orders'
        params = {'type': 'limit', 'side': side, 'instrument_id': instrument_id, 'size': size, 'price': price,
                  'margin_trading': 1}
        return self.http.httpPost(path, params)

    def batch_orders(self, orders):
        """ orders is an List of dict, dict e.g.: {'instrument_id': 'btc-usdt', 'side': side, 'size': size, 'price': price}
        """
        path = '/api/spot/v3/batch_orders'
        params = [
            {'type': 'limit', 'instrument_id': order['instrument_id'], 'side': order['side'], 'size': order['size'],
             'price': order['price']}
            for order in orders]
        return self.http.httpPost(path, params)

    def cancel_order(self, orderid, instrument_id=INSTRUMENT):
        path = '/api/spot/v3/cancel_orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.http.httpPost(path, params)

    def cancel_multiple_orders(self, instrument_id=INSTRUMENT):
        path = '/api/spot/v3/cancel_batch_orders'
        params = [{'instrument_id': instrument_id}]
        return self.http.httpPost(path, params)

    def order_details(self, orderid, instrument_id=INSTRUMENT):
        path = '/api/spot/v3/orders/' + orderid
        params = {'instrument_id': instrument_id}
        return self.http.httpGet(path, params)

    def open_orders(self, instrument_id=INSTRUMENT):
        """This retrieves the list of your current open orders.
        """
        path = '/api/spot/v3/orders_pending'
        return self.http.httpGet(path, {'instrument_id': instrument_id})

    def kline(self, instrument_id, interval, start='', end=''):
        path = '/api/spot/v3/instruments/{}/candles'.format(instrument_id)
        params = {'granularity': interval, 'start': start, 'end': end}
        return self.http.httpGet(path, params)

    def trad_fee(self, instrument_id=INSTRUMENT):
        path = '/api/spot/v3/trade_fee'
        return self.http.httpGet(path)


def print_error_or_get_order_id(ret):
    if ret['error_code'] != '0':
        print(ret)
        return
    else:
        return ret['order_id']


if __name__ == '__main__':
    spot = OkexSpot()
    print(spot.ticker(INSTRUMENT))

    # r = spot.place_order('buy', INSTRUMENT, 1000, 1)
    # order_id = print_error_or_get_order_id(r)
    # spot.cancel_order('6486089829214208')
