#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse


def signature():
    timestamp = str(round(time.time() * 1000))
    secret = 'SEC9e536853396a0913cca3fc4ac56d4aa7aa759e1893f8692776d9f41856def31d'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return f'&timestamp={timestamp}&sign={sign}'


def alarm(msg_str):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=XXXX'
    data = json.dumps({'msgtype': 'text', 'text': {'content': '[awake] ' + msg_str}})
    r = requests.post(url + signature(),
                      data=data,
                      headers={'Content-Type': 'application/json'})
