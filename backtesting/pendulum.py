from ruler.Tool import Tool
from backtesting.FakeCandles import get_candles
from backtesting.pgwrapper import PGWrapper


def get_candle_data():
    begin = '2021-04-15T21:00:00'
    end = '2021-04-16T01:00:00'
    begin = Tool.convert_time_utc(begin)
    end = Tool.convert_time_utc(end)
    return get_candles(begin, end, '1H')

def connect_db():
    db = 'candles'
    table = 'eth_usdt_1H'
    pg = PGWrapper(db)

    data = get_candle_data()
    while True:
        try:
            timestamp, candle = data.popitem(last=True)
            values = dict(zip(['open', 'high', 'low', 'close', 'vol', 'volCcy'], candle))
            values['timestamp'] = int(candle[0])
            print(values)
            # pg.insert(table, values)
        except KeyError:
            break