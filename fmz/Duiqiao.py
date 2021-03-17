#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy as np

class Duiqiao():
    """消耗大量手续费，需要零手续费账户
    """
    def __init__(self, midClass, amount_N, price_N):
        self.jys = midClass
        self.done_amount = 0
        self.init_time = time.time()
        self.last_time = time.time()
        self.amount_N = amount_N
        self.price_N = price_N
        
    def trade_duiqiao(self, trade_dict):
        """买入少，挂单，先买后卖
           卖出少，挂单，先卖后买
        """
        self.jys.create_order( 'buy', trade_dict['price'] , trade_dict['amount'] ) 
        self.jys.create_order( 'sell',trade_dict['price'] , trade_dict['amount'] ) 
        self.done_amount += trade_dict['amount']
        self.last_time = time.time()
        
    def make_duiqiao_trade_dict(self, set_amount, every_time_amount):
        self.jys.refreash_data()
        
        trade_price = ( self.jys.Sell + self.jys.Buy ) / 2
        trade_price = round(trade_price, self.price_N)
        if trade_price > self.jys.Buy and trade_price < self.jys.Sell:
            # else有depth，可能被别人trade       
            self.B = self.jys.Amount
            self.money = self.jys.Balance
            self.can_buy_B = self.money / trade_price
            
            every_time_amount *= every_time_amount * np.random.random() # 不被人发现规律
            trade_dict = {'do_trade': self.B > every_time_amount and self.can_buy_B > every_time_amount,
                          'price': trade_price,
                          'amount': every_time_amount}
            return trade_dict
        
    def deal_with_frozen(self):
        undo_orders = self.jys.get_orders()
        if len( undo_orders) > 0:
            for i in undo_orders:
                self.jys.cancel_order(i['Id'])

def main():
    Set_amount_N = 4
    Set_price_N = 4
    set_amount = 10
    every_time_amount = 0.1
    
    test_mid = midClass(exchange)
    Log(test_mid.refreash_data())
    test_duiqiao = Duiqiao(test_mid, Set_amount_N, Set_price_N)
    
    while test_duiqiao.done_amount < set_amount:
        test_duiqiao.deal_with_frozen()
        Sleep(np.random.randint(1, 60) * 1000) # 不被人发现规律, else 更大盘子让你踏空, 先卖给你再抛售，让你卖不出
        trade_dict = test_duiqiao.make_duiqiao_trade_dict(set_amount, every_time_amount)
        if trade_dict['do_trade']:
            test_duiqiao.trade_duiqiao( trade_dict )
            
    Log(test_duiqiao.done_amount)
    Log(test_duiqiao.B)