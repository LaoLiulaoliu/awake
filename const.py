RETRY = 10
TIME_PRECISION = 1000
MIN_60 = 3600000
MIN_42 = 2520000
MIN_30 = 1800000
MIN_12 = 720000

INSTRUMENT = {
    0: 'btc-usdt',
    1: 'eth-usdt',
    2: 'doge-usdt',
    3: 'alpha-usdt',
    4: 'flow-usdt',
    5: 'glm-usdt',
    6: 'luna-usdt',
    7: 'mask-usdt'
}
VALUTA_IDX = 3
API_VERSION = 3
LOG_DIR = '~/log/'

TREND_NAME = 'trend_{}.txt'
TREND_NAME_TIME = """f'trend_{datetime.utcnow().strftime("%Y-%m-%d")}.txt'"""
TRADE_NAME = 'trade_log_{}.txt'
TRADE_FINISHED = 'trade_finished.txt'
STATE_INDICATOR = 'state_indicator.txt'
