#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import datetime
import hmac
import base64
import json

from retrying import retry
from secret import *
from tradesecret import *

CONTENT_TYPE = 'Content-Type'
APPLICATION_JSON = 'application/json'
OK_ACCESS_KEY = 'OK-ACCESS-KEY'
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN'
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP'
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE'

BASE_URL = 'https://www.okex.com'
# WS_URL = 'ws://echo.websocket.org/'
WS_URL = 'wss://real.okex.com:8443/ws/v3'

class HttpUtil(object):
    def __init__(self):
        self.__url = BASE_URL
        self.__apikey = apikey
        self.__secretkey = secretkey
        self.__passphrase = PASS_PHRASE

        self.session = requests.sessions.Session()

    def get_header(self, sign, timestamp):
        header = dict()
        header[CONTENT_TYPE] = APPLICATION_JSON
        header[OK_ACCESS_KEY] = self.__apikey
        header[OK_ACCESS_SIGN] = sign
        header[OK_ACCESS_TIMESTAMP] = timestamp
        header[OK_ACCESS_PASSPHRASE] = self.__passphrase
        return header

    def timestamp(self):
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        return timestamp[0:-3] + 'Z' 

    def signature(self, timestamp, method, request_path, body):
        if body is None or body == {}:
            body = ''
        message = str(timestamp) + str.upper(method) + request_path + str(body)
        mac = hmac.new(bytes(self.__secretkey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256').digest()
        return base64.b64encode(mac)

    def parse_params_to_str(self, params):
        url = '?'
        for key, value in params.items():
            url = url + str(key) + '=' + str(value) + '&'
        return url[0:-1]

    @retry(stop_max_attempt_number=3)
    def httpGet(self, endpoint, data=None):
        if data:
            endpoint = endpoint + self.parse_params_to_str(data)

        timestamp = self.timestamp()
        signature = self.signature(timestamp, 'GET', endpoint, '')
        headers = self.get_header(signature, timestamp)
        print(self.__url + endpoint)

        response = self.session.request('GET', self.__url + endpoint, headers=headers, timeout=10)
        return response.json()

    @retry(stop_max_attempt_number=3)
    def httpPost(self, endpoint, data):
        body = json.dumps(data)
        timestamp = self.timestamp()
        signature = self.signature(timestamp, 'POST', endpoint, body)
        headers = self.get_header(signature, timestamp)

        response = self.session.request('POST', self.__url + endpoint, headers=headers, data=body)
        return response.json()

