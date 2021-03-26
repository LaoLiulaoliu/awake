#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from ruler.Tool import Tool
from storage.Numpd import Numpd
from .Draw import Draw
from const import TIME_PRECISION

print(__name__, __package__)


def get_leveldb_data(key):
    from .KVDB import KVDB
    X = 'x'
    Y = 'y'
    data = {X: [], Y: []}
    db = KVDB(key)

    for k, v in db.iterator_kv():
        data[X].append(k)
        data[Y].append(json.loads(v)['last'])
    return data


def draw_leveldb_data(data):
    """
    need change Y to float, or else, it will disorder
    cut the data tail which not exceed 1 hour
    """
    X = 'x'
    Y = 'y'
    scale = 18000  # half an hour
    head, tail = 0, 0
    draw = Draw()
    if isinstance(data[X][0], float):
        times = data[X]
    else:
        times = list(map(Tool.convert_time_str, data[X])) if 'T' in data[X][0] else list(map(int, data[X]))

    for i, t in enumerate(times):
        if t - times[head] > scale:
            tail = i
            h = datetime.utcfromtimestamp(times[head] * 0.001).strftime('%Y-%m-%dT%H%M%S')
            t = datetime.utcfromtimestamp(times[tail] * 0.001).strftime('%Y-%m-%dT%H%M%S')
            draw.draw_plot_xy(times[head:tail], list(map(float, data[Y][head:tail])), f'{h} {t}')
            head = i


def get_leveldb_and_draw(key):
    data = get_leveldb_data(key)
    draw_leveldb_data(data)


def flush_trend_nearly_one_hour(self, trend):
    self.flush_trend += 1
    if 8191 & self.flush_trend == 0:
        self.flush_trend = 1
        trend.flush()


def draw_trend_txt(fname, col_dim=4):
    timestamps = []
    prices = []
    cnt = 0
    head = 0
    scale = 3600 * TIME_PRECISION  # half an hour

    draw = Draw()
    trend = Numpd(fname, col_dim)
    if col_dim == 2:
        trend.trend_load()
    elif col_dim == 4:
        trend.trend_full_load()

    for i, data in trend.iterator(reverse=True):
        timestamp = int(data[0] / TIME_PRECISION)
        price = data[1]
        timestamps.append(timestamp)
        prices.append(price)
        cnt += 1

        if 31 & cnt == 0:
            if timestamps[head] - timestamp > scale:
                f = datetime.utcfromtimestamp(timestamps[cnt - 1]).strftime('%Y-%m-%dT%H:%M:%S')
                t = datetime.utcfromtimestamp(timestamps[head]).strftime('%Y-%m-%dT%H:%M:%S')
                draw.draw_plot_xy(
                    list(reversed(timestamps[head:cnt])),
                    list(reversed(prices[head:cnt])),
                    f'{f} {t}')  # (]
                head = cnt


if __name__ == '__main__':
    draw_trend_txt('TREND_0.txt', 2)
