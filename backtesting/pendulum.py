from datetime import datetime
from collections import OrderedDict

from ruler.Tool import Tool
from const import TIME_PRECISION
from backtesting.FakeCandles import get_candles
from db.pgwrapper import PGWrapper


def get_candles_insert_db(pg, table, begin, end, gap):
    datas = OrderedDict()
    for data in get_candles(begin, end, gap):
        for timestamp, candle in data.items():
            timestamp = int(timestamp)
            datas[timestamp] = candle
            candle.append(timestamp)
            pg.insert_list(table,
                           ['open', 'high', 'low', 'close', 'vol', 'volCcy', 'timestamp'],
                           candle)
    return datas


def get_min_max_begin_end(begin, end):
    min_begin = Tool.convert_time_utc('2019-10-01T09:00:00', TIME_PRECISION)
    if begin is None:
        begin = min_begin
    else:
        begin = Tool.convert_time_utc(begin)
        begin = begin if begin > min_begin else min_begin

    max_end = int(datetime.now().timestamp() * TIME_PRECISION)
    if end is None:
        end = max_end
    else:
        end = Tool.convert_time_utc(end)
        end = end if end < max_end else max_end
    return begin, end


def load_candles(name='trx', gap='1H', begin=None, end=None):
    table = f'{name}_usdt_{gap}'
    begin, end = get_min_max_begin_end(begin, end)

    pg = PGWrapper('candles', 'postgres', 'whocares')
    candle_data = OrderedDict()

    min_time, max_time = pg.select(table, 'min(timestamp), max(timestamp)')[0]
    if min_time is None or max_time is None:
        candle_data = get_candles_insert_db(pg, table, begin, end, gap)
    else:
        select_min_time = min_time if begin < min_time else begin
        select_max_time = max_time if end > max_time else end

        if begin < min_time:
            candle_data = get_candles_insert_db(pg, table, begin, min_time, gap)

        if select_min_time < select_max_time:
            r = pg.select(table,
                          'timestamp, open, high, low, close, vol, volCcy',
                          f'timestamp>={select_min_time} and timestamp<={select_max_time}')
            print(r)

        # if end > max_time:
        #     candle_data.update(get_candles_insert_db(pg, table, max_time, end, gap))
