#!/usr/bin/python
# -*- coding: utf-8 -*-

import http.client
import urllib
import json
import hashlib

import requests
import datetime
import hmac
import base64

from secret import *

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
        self.__apikey = API_KEY
        self.__passphrase = PASS_PHRASE
        self.__secretkey = SECRET_KEY

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

    def httpGet(self, endpoint, data=None):
        if data:
            endpoint = endpoint + self.parse_params_to_str(data)

        timestamp = self.timestamp()
        signature = self.signature(timestamp, 'GET', endpoint, '')
        headers = self.get_header(signature, timestamp)

        resp = self.session.request('GET', self.__url + endpoint, headers=headers, timeout=10)
        return json.loads(resp._content)



def buildMySign(params, secretKey):
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) +'&'
    data = sign+'secret_key='+secretKey
    return  hashlib.md5(data.encode("utf8")).hexdigest().upper()


def httpPost(url, resource, params):
     headers = {
            "Content-type" : "application/x-www-form-urlencoded",
     }
     conn = http.client.HTTPSConnection(url, timeout=10)
     temp_params = urllib.parse.urlencode(params)
     conn.request("POST", resource, temp_params, headers)
     response = conn.getresponse()
     data = response.read().decode('utf-8')
     params.clear()
     conn.close()
     return data

