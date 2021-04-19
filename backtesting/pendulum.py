from ruler.Tool import Tool
from backtesting.FakeCandles import get_candles
from db.pgwrapper import PGWrapper


def get_candle_data():
    begin = '2019-10-01T8:00:00'
    end = '2021-04-19T01:00:00'
    begin = Tool.convert_time_utc(begin)
    end = Tool.convert_time_utc(end)
    return get_candles(begin, end, '1H')

def connect_db():
    db = 'candles'
    table = 'trx_usdt_1H'
    pg = PGWrapper(db, 'postgres', 'whocares')

    for data in get_candle_data():
        for timestamp, candle in data.items():
            candle.append(int(timestamp))
            pg.insert_list(table,
                        ['open', 'high', 'low', 'close', 'vol', 'volCcy', 'timestamp'],
                        candle)
            print(candle)
