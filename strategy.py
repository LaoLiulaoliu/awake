from okexSpot import OkexSpot

def test1():
    client = OkexSpot()
    client.trade('buy', 'BTC-USDT', 1000, 1)