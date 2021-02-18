from okexSpot import OkexSpot

def test():
    client = OkexSpot()
    r = client.place_order('buy', 'BTC-USDT', 1000, 1)
    print(r)

    ret = client.ticker('BTC-USDT')
    if 'best_ask' in ret:
        price = float( ret['best_ask'] )

test()
