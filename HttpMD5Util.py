#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于进行http请求，以及MD5加密，生成签名的工具类

import http.client
import requests
import urllib
import json
import hashlib
import time

class HttpMD5Util(object):
    def __init__(self):
        self.session = requests.sessions.Session()

    def httpGet(self, url, params='', jsonify=True):
        resp = self.session.request('GET', url, params, timeout=10)
        if jsonify:
            return json.loads(resp._content)
        else:
            return resp._content


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

