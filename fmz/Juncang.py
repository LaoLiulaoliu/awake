#!/usr/bin/env python
# -*- coding: utf-8 -*-

# okex 2020-03-20 2021-03-02 balance 1000 stocks 0.05 fee 0.15
# 交易次数 114 浮动0.05  least 0.002 return 522 年化 54.8%  drawdown 10.3%  3904
# 交易次数 140 浮动0.02  least 0.002 return 538 年化 56.5%  drawdown 10.2%  3959
# 交易次数 152 浮动0.008  least 0.002 return 570 年化 60%  drawdown 9.5%  4007
# 交易次数 152 浮动0.005  least 0.001 return 489 年化 51%  drawdown 13%  3827

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
        if now_price == '---':
            return False

        self.total_money = self.money + self.B * now_price
        self.half_money = self.total_money / 2
        self.need_buy = (self.half_money - self.B * now_price) / now_price
        self.need_sell = (self.half_money - self.money) / now_price
        return True
    
    def do_juncang(self):
        if self.need_buy > 0.002:
            self.jys.create_order( 'buy', self.jys.Sell , self.need_buy ) 
            self.Buy_count += 1
        elif self.need_sell > 0.002:
            self.jys.create_order( 'sell', self.jys.Buy , self.need_sell ) 
            self.Sell_count += 1
        
        Log('Buy_times:', self.Buy_count, 'Sell_times:', self.Sell_count)
        Log('coin: ', self.B + self.money / self.jys.last, 'money: ', self.money + self.B * self.jys.last)
        
    
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
        if test_juncang.make_need_account_info():
            test_juncang.if_need_trade('price', 0.05)
