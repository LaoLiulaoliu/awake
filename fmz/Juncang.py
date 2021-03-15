#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class Juncang(object):
    def __init__(self, mid_class):
        self.jys = mid_class
        self.last_time = time.time()
        self.last_trade_price = self.jys.last
        self.Buy_count = 0
        self.Sell_count = 0
        
    def make_need_account_info(self):
        self.jys.refreash_data()
        self.B = self.jys.Amount
        self.money = self.jys.Balance
        now_price = self.jys.last
        
        self.total_money = self.B * now_price + self.money
        self.half_money = self.total_money / 2
        self.need_buy = (self.half_money - self.B * now_price) / now_price
        self.need_sell = (self.half_money - self.money) / now_price
    
    def do_juncang(self):
        if self.need_buy > 0.002:
            self.jys.create_order( 'buy', self.jys.low , self.need_buy ) 
            self.Buy_count += 1
        elif self.need_sell > 0.002:
            self.jys.create_order( 'sell', self.jys.high , self.need_sell ) 
            self.Sell_count += 1
        
        Log('Buy_times:', self.Buy_count , 'Sell_times:', self.Sell_count)
        
    
    def if_need_trade(self, condition, prama):
        if condition == 'time':
            if time.time() - self.last_time > prama:
                self.do_juncang()
                self.last_time = time.time()
        if condition == 'price':
            if abs((self.jys.last -  self.last_trade_price) / self.last_trade_price)  > prama:
                self.do_juncang()
                self.last_trade_price = self.jys.last

def main():
    test_mid = midClass(exchange)
    Log(test_mid.refreash_data())
    test_juncang = Juncang(test_mid)
    
    while True:
        Sleep(1000)
        test_juncang.make_need_account_info()
        test_juncang.if_need_trade('price', 0.05)
