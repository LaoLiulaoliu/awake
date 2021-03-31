import time
import numpy as np

SLEEP = 1


def np_view_growth():
    n = 100
    l = []
    for i in range(n):
        array_large = np.random.choice(1000, size=(7000, 7000))
        array_small = array_large[5, :5]
        l.append(array_small)
        time.sleep(SLEEP)

def copy_solve():
    n = 100
    l = []
    for i in range(n):
        array_large = np.random.choice(1000, size=(7000, 7000))
        array_small = array_large[5, :5].copy()
        l.append(array_small)
        time.sleep(SLEEP)

def tolist_solve():
    n = 100
    l = []
    for i in range(n):
        array_large = np.random.choice(1000, size=(7000, 7000))
        array_small = array_large[5, :5].tolist()  # copy a list, I think copy is better
        l.append(array_small)
        time.sleep(SLEEP)


def test_nps_assign():
    n = 100
    target = np.arange(50).reshape(10, 5)
    for i in range(n):
        array_large = np.random.choice(1000, size=(7000, 7000))
        target[0, :] = array_large[5, :5]  # memory also OK
        time.sleep(SLEEP)

copy_solve()