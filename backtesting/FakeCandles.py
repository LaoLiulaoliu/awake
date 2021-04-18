import time
from collections import OrderedDict
from const import INSTRUMENT, VALUTA_IDX
from api.OkexSpotV5 import OkexSpotV5


spot5 = OkexSpotV5(use_trade_key=True)

def get_candles(before, after='', bar='15m'):
    """ ts, o, h, l, c, vol, volCcy
    现货 BTC-USDT 交易货币-计价货币
    vol: 交易货币折算的交易量
    volCcy: 计价货币折算的交易量

    合约
    vol: unit 合约张数
    volCcy: unit 合约币总数
    """
    before, after = str(before), str(after)
    data = OrderedDict()
    last_time = after

    if after == '':
        r = spot5.candles(INSTRUMENT[VALUTA_IDX].upper(), bar)
        for i in r['data']:
            data[i[0]] = i[1:]
        else:
            last_time = i[0]

    while True:
        r = spot5.candles_history(INSTRUMENT[VALUTA_IDX].upper(), bar, after=last_time)
        last_time = None

        # if r['data'] == []:
        #     print(r)
        for i in r['data']:
            data[i[0]] = i[1:]
        else:
            last_time = i[0]
        if last_time < before:
            return data
        yield data
        data = OrderedDict()
        time.sleep(0.1)
