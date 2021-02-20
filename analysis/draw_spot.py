#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from .Draw import Draw

print(__name__, __package__)


def convert_time_str(time_str):
    return round(datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp() * 10)


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
    scale = 18000  # an hour
    head, tail = 0, 0
    draw = Draw()
    times = list(map(convert_time_str, data[X])) if 'T' in data[X][0] else list(map(int, data[X]))

    for i, t in enumerate(times):
        if t - times[head] > scale:
            tail = i
            draw.draw_plot_xy(times[head:tail], list(map(float, data[Y][head:tail])))
            head = i


def dump_data(key):
    data = get_data(key)
    with open('a.txt', 'w') as fd:
        json.dump(data, fd)


def load_and_draw():
    with open('a.txt', 'r') as fd:
        data = json.load(fd)
    draw_data(data)


if __name__ == '__main__':
    # dump_data('2021-02-19T08-44-22')
    load_and_draw()