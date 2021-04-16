from ruler.Tool import Tool
from backtesting.FakeCandles import get_candles
from db.pgwrapper import PGWrapper


def get_candle_data():
    begin = '2021-04-15T21:00:00'
    end = '2021-04-16T01:00:00'
    begin = Tool.convert_time_utc(begin)
    end = Tool.convert_time_utc(end)
    return get_candles(begin, end, '1H')

def connect_db():
    db = 'candles'
    table = 'eth_usdt_1H'
    pg = PGWrapper(db, 'postgres', 'whocares')

    data = get_candle_data()
    while True:
        try:
            timestamp, candle = data.popitem(last=True)
            candle.append(int(timestamp))
            pg.insert_list(table,
                        ['open', 'high', 'low', 'close', 'vol', 'volCcy', 'timestamp'],
                        candle)
        except KeyError:
            break