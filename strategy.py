from okexSpot import OkexSpot

def test():
    client = OkexSpot()
    r = client.trade('buy', 'BTC-USDT', 1000, 1)
    print(r)

test()