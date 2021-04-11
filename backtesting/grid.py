import logging
import gevent
import time
import numpy as np
from datetime import datetime

from const import INSTRUMENT, VALUTA_IDX, TIME_PRECISION, TRADE_NAME
from monitor.ding import alarm

from .FakeState import FakeState
from .FakeTrade import FakeTrade
from .FakeTrend import FakeTrend


INIT_MONEY = 1240
INIT_COIN = 730
STOP_LOSS_RATIO = 0.4

low_price = 1.0
high_price = 2.5
SPACING_PRICE = 0.004
AVERAGE_ASK_BID_SIZE = 7.5  # also refer to min_size
effective_number_of_bits = 3

GRID_NUM = int((high_price - low_price) / SPACING_PRICE)
BOARD_LOT = 1  # max(round(INIT_COIN / GRID_NUM, effective_number_of_bits), AVERAGE_ASK_BID_SIZE)
COIN_UNIT, MONEY_UNIT = list(map(str.upper, INSTRUMENT[VALUTA_IDX].split('-')))
SLEEP = 0

logger = logging.getLogger()


def place_pair_orders(state, last_trade_price, enobs):
    available = state.get_available()
    coin = available[COIN_UNIT]
    money = available[MONEY_UNIT]

    buy_price = round(last_trade_price - SPACING_PRICE, enobs)
    sell_price = round(last_trade_price + SPACING_PRICE, enobs)
    size = 1  # round(np.random.normal(BOARD_LOT, 0.5), enobs)
    if coin > size and buy_price < money:
        order_ids = state.trade.place_batch_orders([
            {'price': buy_price, 'size': size, 'side': 'buy', 'instrument_id': INSTRUMENT[VALUTA_IDX]},
            {'price': sell_price, 'size': size, 'side': 'sell', 'instrument_id': INSTRUMENT[VALUTA_IDX]}
        ])

        # logger.info(f'buy_price: {buy_price}, size: {size}, id: {order_ids[0]}; sell_price: {sell_price}, size: {size}, id: {order_ids[1]}')

        if 0 in order_ids:
            for i, oid in enumerate(order_ids):
                if oid != 0:
                    state.trade.cancel_order(oid)
                    state.delete_canceled_orders([oid])
                    side = 'buy' if i == 0 else 'sell'
                    logger.info(f'{side} failed, buy_price: {buy_price}, sell_price: {sell_price}, size: {size}')
            return

        return [int(time.time() * TIME_PRECISION), order_ids[0], order_ids[1]]
    return


def grid_init_orders(state, last_trade_price, enobs):
    while True:
        r = place_pair_orders(state, last_trade_price, enobs)
        if r is None:
            gevent.sleep(SLEEP)
        else:
            return r


def stop_loss(money_remain, ratio=STOP_LOSS_RATIO):
    while True:
        if money_remain < INIT_MONEY * ratio:
            alarm(f'money remain: {money_remain}, init money: {INIT_MONEY}. Sleep 900s and operate by hand')
            gevent.sleep(900)
        else:
            break


def strategy(state, enobs=3):
    """ Need ticker, account, order in websocket API, please set in awake.py

    When the price fluctuates rapidly, use ticker price will cause inversion of buy_price and sell_price,
    Use deal price passed by order API.
    """
    init_price = 0
    final_price = 0

    for i, r in state.get_latest_trend():
        last_time, last_trade_price, best_ask, best_bid = r
        buy_sell_pair = grid_init_orders(state, float(last_trade_price), enobs)
        init_price = float(last_trade_price)
        break

    for i, r in state.get_latest_trend():
        last_time, last_trade_price, best_ask, best_bid = r
        final_price = float(last_trade_price)
        state_order_id, last_trade_price, order_state = state.get_order_change(float(last_trade_price))
        if state_order_id == 0 and last_trade_price == 0 and order_state == 0:
            continue

        available = state.get_available()
        coin = available[COIN_UNIT]
        money = available[MONEY_UNIT]

        stop_loss(money)
        timestamp, buy_order_id, sell_order_id = buy_sell_pair

        if state_order_id == buy_order_id:
            buy_state = order_state
            sell_state = 0
        elif state_order_id == sell_order_id:
            buy_state = 0
            sell_state = order_state
        else:
            logger.info(f'irrelevant order: {state_order_id}, state: {order_state}')
            continue  # other irrelevant order
        success = True
        # logger.info(f'{timestamp} changed {0 if buy_order_id == state_order_id else 1} order, state: {buy_state} : {sell_state}, id: {buy_order_id} : {sell_order_id}')

        # modify failed, hold still, then buy lower sell higher.
        # buy or sell failed, logic chain breaking,
        # cancel another trade pair, wait and boot on again.
        if buy_state == 2:
            logger.info(f'dealed buy  {last_trade_price}')
            while True:
                buy_price = round(last_trade_price - SPACING_PRICE, enobs)
                sell_price = round(last_trade_price + SPACING_PRICE, enobs)

                if buy_price < money:
                    order_id = state.trade.place_buy_order(buy_price, BOARD_LOT)
                    logger.info(f'deal buy, new buy:    {buy_price}')
                    if order_id == 0:
                        state.trade.cancel_order(sell_order_id)  # if not cancel, this order may auto-deal later
                        logger.info('deal buy, place new buy error')  # low probability occurrence
                        gevent.sleep(SLEEP)
                        success = False
                        continue
                    else:
                        if success is True:
                            r = state.trade.modify_order(sell_order_id, sell_price, BOARD_LOT)
                            logger.info(f'deal buy, modify sell {sell_price}, order_id: {r}')
                            buy_sell_pair[0] = int(time.time() * TIME_PRECISION)
                            buy_sell_pair[1] = order_id
                            break
                        else:
                            r = place_pair_orders(state, last_trade_price, enobs)
                            if r is None:
                                success = False
                                logger.info('deal buy, place pair order fail')  # low probability occurrence
                                continue
                            else:
                                buy_sell_pair = r
                                success = True
                                logger.info('deal buy, place pair order success')  # low probability occurrence
                                break
                else:
                    state.trade.cancel_order(sell_order_id)
                    logger.info(f'deal buy, cancel sell: {sell_order_id}')  # low probability occurrence
                    gevent.sleep(SLEEP)
                    success = False
                    continue

        elif sell_state == 2:
            logger.info(f'dealed sell {last_trade_price}')
            while True:
                buy_price = round(last_trade_price - SPACING_PRICE, enobs)
                sell_price = round(last_trade_price + SPACING_PRICE, enobs)

                if coin > BOARD_LOT:
                    order_id = state.trade.place_sell_order(sell_price, BOARD_LOT)
                    logger.info(f'deal sell, new sell   {sell_price}')
                    if order_id == 0:
                        state.trade.cancel_order(buy_order_id)
                        logger.info('deal sell, place new sell error')
                        gevent.sleep(SLEEP)
                        success = False
                        continue
                    else:
                        if success is True:
                            r = state.trade.modify_order(buy_order_id, buy_price, BOARD_LOT)
                            logger.info(f'deal sell, modify buy {buy_price}, order_id {r}')
                            buy_sell_pair[0] = int(time.time() * TIME_PRECISION)
                            buy_sell_pair[2] = order_id
                            break
                        else:
                            r = place_pair_orders(state, last_trade_price, enobs)
                            if r is None:
                                success = False
                                logger.info('deal sell, place pair order fail')
                                continue
                            else:
                                buy_sell_pair = r
                                success = True
                                logger.info('deal sell, place pair order success')
                                break
                else:
                    state.trade.cancel_order(buy_order_id)
                    logger.info(f'deal sell, cancel buy: {buy_order_id}')
                    gevent.sleep(SLEEP)
                    success = False
                    continue
    return init_price, final_price


def precent(source, target):
    return abs(source - target) / source

def grid():
    print({COIN_UNIT: INIT_COIN, MONEY_UNIT: INIT_MONEY})

    trend = FakeTrend('2021-03-24', '2021-04-10')
    trade = FakeTrade(TRADE_NAME.format(VALUTA_IDX))
    state = FakeState(trend, trade)

    state.set_unit(COIN_UNIT, MONEY_UNIT)
    state.set_available(INIT_COIN, INIT_MONEY)

    init_price, final_price = strategy(state, 3)

    available = state.get_available()
    final_coin = available[COIN_UNIT]
    final_money = available[MONEY_UNIT]

    init = INIT_MONEY + INIT_COIN * init_price
    final = final_money + final_coin * final_price
    print(f'init money: {init}, final money: {final}, {100 * precent(init, final)}')