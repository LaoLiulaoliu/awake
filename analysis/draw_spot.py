#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print(__name__, __package__)
import json
from .Draw import Draw


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
    """
    X = 'x'
    Y = 'y'
    scale = 1000
    draw = Draw()
    length = len(data[X])
    for i in range(length // scale):
        draw.draw_plot_xy(data[X][i * scale:(i + 1) * scale], list(map(float, data[Y][i * scale:(i + 1) * scale])))
        print(i * scale, (i + 1) * scale)


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
