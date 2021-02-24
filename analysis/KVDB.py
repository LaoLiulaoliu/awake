#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import leveldb
import gevent.lock
import json


class KVDB(object):
    __sem = gevent.lock.BoundedSemaphore(1)

    def __new__(cls, *args, **kwargs):
        if not hasattr(KVDB, '_instance'):
            with KVDB.__sem:
                if not hasattr(KVDB, '_instance'):
                    KVDB._instance = object.__new__(cls)
        return KVDB._instance

    def __init__(self, name):
        self.db = leveldb.LevelDB(name)

    def put(self, key, value):
        """key is str
           value is dict
        """
        self.db.Put(key.encode(), json.dumps(value).encode())

    def update(self, key, value):
        """key is str
           value is dict
        """
        self.db.Put(key.encode(), json.dumps(value).encode())

    def get(self, key):
        """key is str
        """
        return self.db.Get(key.encode()).decode()

    def display(self):
        for key, value in self.db.RangeIter():
            print(key, value)

    def iterator_kv(self):
        for key, value in self.db.RangeIter():
            yield key.decode(), value.decode()

    def iter_from_to(self, key_from, key_to, reverse=False):
        for key, value in self.db.RangeIter(key_from=key_from, key_to=key_to, reverse=reverse):
            yield key.decode(), value.decode()

    def iter_keys(self):
        for key in self.db.RangeIter(include_value=False):
            print(key)

    def clear_db(self):
        """b.Delete(k) not really delete data，db.Write(b) do all operations
        """
        b = leveldb.WriteBatch()
        for k in self.db.RangeIter(include_value=False, reverse=True):
            b.Delete(k)
        self.db.Write(b)


if __name__ == '__main__':
    db = KVDB('2021-02-19T03-20-36')
    db.display()
