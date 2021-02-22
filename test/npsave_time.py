#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy as np


FNAME = 'd.npy'

def npsave(data, func):
    with open(FNAME, 'wb') as f:
        t = time.time()
        for i in range(1000):
            func(f, data)
        print(time.time() - t)  # 0.23


def np_test_save(data):
    f = open(FNAME, 'wb')
    np.save(f, data)

    f.seek(0, 0)  # simulate closing & reopening file
    np.save(f, np.zeros((2, 5)))

    with open(FNAME, 'rb') as fd:
        print(np.load(fd))
    f.close()


if __name__ == '__main__':
    d = np.arange(400).reshape(100, 4)
    npsave(d, np.save)  # 0.23
    npsave(d, np.savez)  # 0.33
    npsave(d, np.savetxt)  # 0.52

    np_test_save(d)
