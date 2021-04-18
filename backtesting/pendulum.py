from ruler.Tool import Tool
from backtesting.FakeCandles import get_candles
from db.pgwrapper import PGWrapper


def get_candle_data():
    begin = '2017-12-01T21:00:00'
    end = '2021-04-16T17:00:00'
    end = '2019-10-01T08:00:00'
    begin = Tool.convert_time_utc(begin)
    end = Tool.convert_time_utc(end)
    return get_candles(begin, end, '1H')

def connect_db():
    db = 'candles'
    table = 'eth_usdt_1H'
    pg = PGWrapper(db, 'postgres', 'whocares')

    for data in get_candle_data():
        for timestamp, candle in data.items():
            candle.append(int(timestamp))
            pg.insert_list(table,
                        ['open', 'high', 'low', 'close', 'vol', 'volCcy', 'timestamp'],
                        candle)
            print(candle)
