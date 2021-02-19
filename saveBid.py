#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from DBHandler import DBHandler
from OkexSpot import OkexSpot, INSTRUMENT

def init(name='test'):
    if not hasattr(init, '_db'):
        setattr(init, '_db', DBHandler(name))
    if not hasattr(init, '_spot'):
        setattr(init, '_spot', OkexSpot())
    return init._db, init._spot

def save():
    name = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    db, spot = init(name)
    r = spot.ticker(INSTRUMENT)
    db.put(r['timestamp'], {'last': r['last'], 'high_24h': r['high_24h'], 'low_24h': r['low_24h']})

if __name__ == '__main__':
    save()