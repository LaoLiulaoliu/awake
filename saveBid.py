#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from DBHandler import DBHandler
from OkexSpot import OkexSpot, INSTRUMENT

def init(name='test'):
    if not hasattr(init, '_db'):
        setattr(init, '_db', DBHandler(name))
    if not hasattr(init, '_spot'):
        setattr(init, '_spot', OkexSpot())
    return init._db, init._spot

def save(name=None):
    name = datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S') if name is None else name
    db, spot = init(name)

    while (True):
        t = time.time()
        r = spot.ticker(INSTRUMENT)
        db.put(r['timestamp'], {'last': r['last'], 'high_24h': r['high_24h'], 'low_24h': r['low_24h']})
        print(time.time() - t)

if __name__ == '__main__':
    save()