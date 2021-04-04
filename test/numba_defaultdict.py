import time
import numba
import functools
import numpy as np
from collections import defaultdict
from numba.typed import Dict


def time_decoator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = time.time()
        ret = func(*args, **kwargs)
        print(time.time() - t)
        return ret
    return wrapper


# https://github.com/numba/numba/issues/6439
# numba Dict lot slower
# prices_dict = Dict.empty(key_type=numba.types.int64, value_type=numba.types.int64)
@numba.jit(nopython=True)
def calculate_price_key_value(buy_price, sell_price, enobs):
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)
    return buy_key, buy_value, sell_key, sell_value

def best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
    """
    buy_prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    buy_key, buy_value, sell_key, sell_value = calculate_price_key_value(buy_price, sell_price, enobs)

    if (buy_key in buy_prices and buy_value in buy_prices[buy_key]) or \
       (sell_key in sell_prices and sell_value in sell_prices[sell_key]):
        return False
    else:
        if buy_key in buy_prices and len(buy_prices[buy_key]) > 0:
            buy_prices[buy_key].add(buy_value)
        else:
            buy_prices[buy_key] = {buy_value}

        if sell_key in sell_prices and len(sell_prices[sell_key]) > 0:
            sell_prices[sell_key].add(sell_value)
        else:
            sell_prices[sell_key] = {sell_value}

        return True


def calculate_price_key_value_collections(buy_price, sell_price, enobs):
    buy_key = int(buy_price * 10 ** (enobs - 1))
    buy_value = int(buy_price * 10 ** enobs)
    sell_key = int(sell_price * 10 ** (enobs - 1))
    sell_value = int(sell_price * 10 ** enobs)
    return buy_key, buy_value, sell_key, sell_value

def best_buy_sell_price_collections_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs):
    """
    buy_prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    buy_key, buy_value, sell_key, sell_value = calculate_price_key_value_collections(buy_price, sell_price, enobs)

    if buy_value in buy_prices[buy_key] or sell_value in sell_prices[sell_key]:
        return False
    else:
        buy_prices[buy_key].add(buy_value)
        sell_prices[sell_key].add(sell_value)
        return True


def fill_prices_collections():
    prices = defaultdict(set)
    for i in range(1000, 2999):
        key = int(i / 10.)
        prices[key].add(i)
    return prices

def find_best_price_collections(price, prices, enobs):
    """
    prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    key = int(price * 10 ** (enobs - 1))
    value = int(price * 10 ** enobs)
    return value in prices[key]


def fill_prices():
    prices = dict()
    for i in range(1000, 2999):
        key = int(i / 10.)
        if key in prices:
            prices[key].add(i)
        else:
            prices[key] = {i}
    return prices

def find_best_price(price, prices, enobs):
    """
    prices: {186: [1861, 1865, 1868], 191: [1911, 1913]}
    """
    key = int(price * 10 ** (enobs - 1))
    value = int(price * 10 ** enobs)
    if key in prices:
        return value in prices[key]
    else:
        prices[key] = {value}

@time_decoator
def test_time_collections():
    prices = fill_prices()
    t = time.time()
    for i in range(1000):
        price = round(np.random.normal(2, 0.5), 3)
        find_best_price(price, prices, 3)
    print(f'defaultdict cost: {time.time() - t}')

@time_decoator
def test_time():
    prices = fill_prices_collections()
    t = time.time()
    for i in range(1000):
        price = round(np.random.normal(2, 0.5), 3)
        find_best_price_collections(price, prices, 3)
    print(f'dict cost: {time.time() - t}')

@time_decoator
def real_code_collection_test(enobs=3):
    buy_prices = fill_prices_collections()
    sell_prices = fill_prices_collections()
    for i in range(1000):
        buy_price = round(np.random.normal(2, 0.5), 3)
        sell_price = round(np.random.normal(2, 0.5), 3)
        best_buy_sell_price_collections_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs)


@time_decoator
def real_code_numba_test(enobs=3):
    buy_prices = fill_prices()
    sell_prices = fill_prices()
    for i in range(1000):
        buy_price = round(np.random.normal(2, 0.5), 3)
        sell_price = round(np.random.normal(2, 0.5), 3)
        best_buy_sell_price_duplicate(buy_price, buy_prices, sell_price, sell_prices, enobs)

# test_time_collections()
# test_time()

real_code_collection_test()
real_code_numba_test()