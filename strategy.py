from OkexSpot import OkexSpot

def test():
    spot = OkexSpot()
    r = spot.place_order('buy', 'BTC-USDT', 1000, 1)
    print(r)

    ret = spot.ticker('BTC-USDT')
    if 'best_ask' in ret:
        price = float( ret['best_ask'] )

test()
