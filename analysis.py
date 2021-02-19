#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Draw import Draw
from DBHandler import DBHandler

def get_data():
    X = 'x'
    Y = 'y'
    data = {X: [], Y: []}
    draw = Draw()
    db = DBHandler('2021-02-19T03-20-36')
    
    for k, v in db.iterator_kv():
        data[X].append(k)
        data[Y].append(v)
    draw.draw_plot_xy(data, X, Y)

get_data()