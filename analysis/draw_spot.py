#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from runner.Tool import Tool
from runner.Blaze import Blaze
from .Draw import Draw

print(__name__, __package__)


def get_data(key):
    from .DBHandler import DBHandler
    X = 'x'
    Y = 'y'
    data = {X: [], Y: []}
    db = DBHandler(key)

    for k, v in db.iterator_kv():
        data[X].append(k)
        data[Y].append(json.loads(v)['last'])
    return data


def draw_data(data):
    """
    need change Y to float, or else, it will disorder
    cut the data tail which not exceed 1 hour
    """
    X = 'x'
    Y = 'y'
    scale = 1800000  # half an hour
    head, tail = 0, 0
    draw = Draw()
    if isinstance(data[X][0], float):
        times = data[X]
    else:
        times = list(map(Tool.convert_time_str, data[X])) if 'T' in data[X][0] else list(map(int, data[X]))

    for i, t in enumerate(times):
        if t - times[head] > scale:
            tail = i
            h = datetime.utcfromtimestamp(times[head] * 0.001).strftime("%Y-%m-%dT%H:%M:%S")
            t = datetime.utcfromtimestamp(times[tail] * 0.001).strftime("%Y-%m-%dT%H:%M:%S")
            draw.draw_plot_xy(times[head:tail], list(map(float, data[Y][head:tail])), f'{h} {t}')
            head = i


def dump_data(key):
    data = get_data(key)
    with open('a.txt', 'w') as fd:
        json.dump(data, fd)


def load_and_draw():
    with open('a.txt', 'r') as fd:
        data = json.load(fd)
    draw_data(data)


def draw_trend_txt(fname):
    def get_data(iterator):
        timestamps = []
        prices = []
        for i, data in iterator:
            timestamps.append(data[0])
            prices.append(data[1])

        return timestamps, prices

    trend = Blaze(fname, 2)
    timestamps, prices = trend.reload(reverse=False, callback=get_data)
    data = {'x': timestamps, 'y': prices}
    draw_data(data)


if __name__ == '__main__':
    # dump_data('2021-02-19T08-44-22')
    load_and_draw()
