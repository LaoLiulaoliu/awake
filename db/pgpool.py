#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

# Add a connection pool for postgresql


import sys
import queue
import psycopg2
from collections import namedtuple
from contextlib import contextmanager


QueryResult = namedtuple('RowResult', ('columns', 'results'))

class PGPool(object):

    def __init__(self,
                 dbname='postgres',
                 user='postgres',
                 password='',
                 host='127.0.0.1',
                 port=5432,
                 poolsize=3,
                 maxretries=5,
                 debug=False,
                 fetch_size=400):
        """ .. :py:class::

            pg_hba.conf: host trust
        """
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.poolsize = poolsize
        self.maxretries = maxretries
        self.debug = debug
        self.fetch_size = fetch_size
        self.queue = queue.Queue(self.poolsize)
        self.connection_in_use = 0


    def clear(self):
        while not self.queue.empty():
            self.connection_in_use -= 1
            self.queue.get().close()

    def get(self):
        if self.queue.empty() or self.connection_in_use < self.poolsize:
            self.connection_in_use += 1
            return self._create_connection()
        return self.queue.get()

    def put(self, conn):
        if self.queue.full():
            conn.close()
        self.queue.put(conn)

    def _create_connection(self):
        """.. :py:method::

              If we hava several hosts, we can random choice one to connect
        """
        db = psycopg2.connect(database=self.dbname,
                            user=self.user, password=self.password,
                            host=self.host, port=self.port)
        if 'psycopg2.extras' in sys.modules:
            psycopg2.extras.register_hstore(db)
        return db

    @contextmanager
    def connection(self):
        yielded = False
        retry = 0
        while yielded is False and retry < self.maxretries:
            try:
                conn = self.get()
                cur = conn.cursor()
                yield cur
            except Exception as e:
                conn = None
                retry += 1
                print(e)
            else:
                yielded = True
                retry = 0
                conn.commit() # commit `insert`, `update` and `delete`
            finally:
                if conn is not None:
                    cur.close()
                    self.put(conn)

        if yielded is False:
            raise Exception('Could not obtain cursor, max retry {} reached.'.format(retry))


    def execute(self, query, vars=None, result=False):
        """.. :py:method::

        :param bool result: whether query return result
        :rtype: bool

        .. note::
            True for `select`, False for `insert` and `update`
        """
        with self.connection() as cur:
            if self.debug:
                print(cur.mogrify(query, vars))

            resp = cur.execute(query, vars)

            if result == False:
                return resp

            else:
                columns = [i[0] for i in cur.description]
                results = cur.fetchall()
                return QueryResult(columns, results)


    def execute_generator(self, query, vars=None, result=False):
        """.. :py:method::

        :param bool result: whether query return result
        :rtype: bool

        .. note::
            True for `select`, False for `insert` and `update`
        """
        with self.connection() as cur:
            if self.debug:
                print(cur.mogrify(query, vars))

            resp = cur.execute(query, vars)

            if result == True:
                columns = [i[0] for i in cur.description]
                results = cur.fetchmany(1000)
                while results:
                    yield QueryResult(columns, results)
                    results = cur.fetchmany(1000)


    def batch(self, queries):
        """.. :py:method::

        :param tuple queries: [(sql, vars), (sql, vars), ...]

        .. note::
            batch execute queries.
            only support `insert` and `update`, have more efficiency
        """
        with self.connection() as cur:
            for sql, vars in queries:

                if self.debug:
                    print(cur.mogrify(sql, vars))
                cur.execute(sql, vars)

