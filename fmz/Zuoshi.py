#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time


class Zuoshi(object):
    """刷量，别人把一单成交，要用更加不合理价格买回来（均仓时），会有损失。优化：1.上涨卖出和买入价格略调高，下跌也是，需要判断趋势；2.假设不做对敲，走到中心就不下降了。
做市策略是提供流动性，而不是得到更多收益。
实盘做市吃游离单，回测不会有游离单。

买不了，都变成币了；卖不了，都变成钱了。全卖完了，一上涨就亏了，要加入均仓。均仓里面空闲资金可以做对敲。
    """
    def __init__(self, mid_class, amount_N, price_N, gua_num):
        """
        param amount_N: round amount
        param price_N:  round price
        param gua_num: 提高利用率，同时做多个盘口。
        """
        self.jys = mid_class
        self.done_amount = {'pan_kou':0, 'dui_qiao':0}
        self.init_time = time.time()
        self.last_time = time.time()
        self.amount_N = amount_N
        self.price_N = price_N
        self.wait_time = 60
        
        self.traded_pair = {'pan_kou':[], 'dui_qiao':[]}
        self.undo_state = []
        self.had_gua_times = {i: 0 for i in range(gua_num)}
            
    
    def refreash_data(self):
        
        self.jys.refreash_data()
        self.B = self.jys.Amount
        self.money = self.jys.Balance
        self.can_buy_B = self.money/ self.jys.Buy
        self.mid_price = ( self.jys.Sell + self.jys.Buy )/2
        
        return 
    
        
    def make_trade_by_dict(self, trade_dicts):
        for trade_dict in trade_dicts:
            if trade_dict['do_trade']:
                buy_id = self.jys.create_order( 'buy', trade_dict['buy_price'] , trade_dict['amount'] ) 
                sell_id = self.jys.create_order( 'sell',trade_dict['sell_price'] , trade_dict['amount'] ) 
                
                if trade_dict['buy_price'] == trade_dict['sell_price']:
                    self.done_amount['dui_qiao'] += trade_dict['amount']
                    self.traded_pair['dui_qiao'].append({'buy_id': buy_id, 'sell_id': sell_id, 'init_time':time.time(),
                                                         'amount':trade_dict['amount'],'guadan_times_id':trade_dict['guadan_times_id'] })
                else:
                    
                    self.traded_pair['pan_kou'].append({'buy_id': buy_id, 'sell_id': sell_id, 'init_time':time.time(),
                                                        'amount':trade_dict['amount'],'guadan_times_id':trade_dict['guadan_times_id'] })
                    
                self.last_time = time.time()
        
    def make_duiqiao_trade_dict(self, set_amount, every_time_amount):
        
        trade_price = self.mid_price
        trade_price = round(trade_price, self.price_N)
        
        if trade_price > self.jys.Buy and trade_price< self.jys.Sell:            
            do_trade = self.B > every_time_amount
            do_trade = do_trade and self.can_buy_B > every_time_amount
            trade_dict = {'do_trade':do_trade,
                          'buy_price': trade_price,
                          'sell_price':trade_price,
                          'amount':every_time_amount,
                         'guadan_times_id':0}
            
            return [trade_dict]
        
    def deal_with_frozen(self):
        undo_orders = self.jys.get_orders()
        if len( undo_orders) > 0:
            for i in undo_orders:
                self.jys.cancel_order(i['Id'])
                
    def make_pankou_dict(self, price_range , min_price_len, every_time_amount ):
        trade_dicts = []
        mid_price =  self.mid_price
        price_alphas = {}
        for i in (self.had_gua_times):
            price_alphas[i] = price_range - self.had_gua_times[i] * min_price_len* random.randint(0,5) 
            if price_alphas[i] < 0:
                price_alphas[i] = 0
                self.had_gua_times[i] = 0
            
        for guadan_times_id in price_alphas:        
            price_alpha = price_alphas[guadan_times_id]
            
            buy_price = mid_price - price_alpha
            buy_price = round(buy_price, self.price_N)
            can_buy_B =  self.money/buy_price
            
            sell_price = mid_price + price_alpha
            sell_price = round(sell_price, self.price_N)
            
            
            do_dict = (self.B > every_time_amount )and (can_buy_B > every_time_amount)
#             Log(do_dict)

            amount = every_time_amount

            trade_dict = {    'do_trade':do_dict,
                              'buy_price': buy_price,
                              'sell_price':sell_price,
                              'amount':every_time_amount,
                             'guadan_times_id':guadan_times_id}
            trade_dicts.append(trade_dict)
            return trade_dicts

    
    def check_if_traded( self , now_times):
        for traded_id in self.traded_pair['pan_kou']:
            try:
                this_buy_state = self.jys.exchange.GetOrder(traded_id['buy_id'])
            except:
                self.jys.cancel_order( traded_id['sell_id'] )
                self.traded_pair['pan_kou'].remove( traded_id )
            try:
                this_sell_state = self.jys.exchange.GetOrder(traded_id['sell_id'])
            except:
                self.jys.cancel_order( traded_id['buy_id'] )
                self.traded_pair['pan_kou'].remove( traded_id )
            
            
            if { this_sell_state['Status'], this_buy_state['Status'] } == {0, 0}:
                if now_times% 50 ==0 :
                    Log(this_buy_state['Status'], this_sell_state['Status'], now_times% 50 )
#                 if ( time.time() - traded_id['init_time'] )/1000/60 > self.wait_time: # 回测取不到当时时间
                    self.jys.cancel_order( traded_id['buy_id'] )
                    self.jys.cancel_order( traded_id['sell_id'] )
                    self.had_gua_times[traded_id['guadan_times_id']] += random.randint(1,3) 
                    self.traded_pair['pan_kou'].remove( traded_id )

            elif {this_sell_state['Status'], this_buy_state['Status'] } == { 1, 0}:
                if now_times% 50 ==0 :
                    Log(this_buy_state['Status'], this_sell_state['Status'], now_times% 50 )
#                 if ( time.time() - traded_id['init_time'] )/1000/60 > self.wait_time:
                    if this_buy_state['Status'] == 0:
                        self.jys.cancel_order( traded_id['buy_id'] )
                        self.undo_state.append(['buy', this_buy_state['Status']])
                        self.traded_pair['pan_kou'].remove( traded_id )
                    elif this_sell_state['Status'] == 0:
                        self.jys.cancel_order( traded_id['sell_id'] )
                        self.undo_state.append(['sell', this_sell_state['Status']])
                        self.traded_pair['pan_kou'].remove( traded_id )
                
            elif {this_sell_state['Status'], this_buy_state['Status'] } == {1,1}:
                Log(this_buy_state['Status'], this_sell_state['Status'], traded_id['amount']  )
                self.done_amount['pan_kou'] += traded_id['amount'] 
                self.traded_pair['pan_kou'].remove( traded_id )
            else:
                Log(this_buy_state,this_sell_state)
                Log('2id:',this_buy_state['Status'], this_sell_state['Status'] )
                Log(traded_id)
                

                
        self.half_B = 0.5* (self.can_buy_B + self.B)
        condition_tsd = (condition_ratio/100 )*2*self.half_B
        
        need_sell_amount = self.B - self.half_B
        need_buy_amount = self.can_buy_B - self.half_B
        
        if need_sell_amount > condition_tsd :
            self.jys.create_order( 'sell',self.jys.Sell, need_sell_amount ) 
        elif need_buy_amount > condition_tsd:
            self.jys.create_order( 'buy', self.jys.Buy , need_buy_amount ) 
                
                
def main():
    
    times = 0
    
    Set_amount_N = 4
    Set_price_N = 4
    set_amount = 1000
    gua_N = 5
    
    price_range = 50
    min_price_len = 1
    every_time_amount = 0.01
    juncany_ratio_on_percentage = 2
    
    test_mid = midClass(exchange)
    Log(test_mid.refreash_data())
    test_zuoshi = Zuoshi(test_mid, Set_amount_N, Set_price_N, gua_N)
    
    while( test_zuoshi.done_amount['pan_kou'] < set_amount):
        
        test_zuoshi.check_if_traded(times)
        Sleep(1000)
        test_zuoshi.refreash_data()
        
        if times%100 == 1:
            test_zuoshi.juncang( juncany_ratio_on_percentage )
        else:
            if len( test_zuoshi.traded_pair['pan_kou'] ) < gua_N:
                trade_dicts = test_zuoshi.make_pankou_dict( price_range , min_price_len, every_time_amount )
                test_zuoshi.make_trade_by_dict( trade_dicts )
                Log( test_zuoshi.done_amount['pan_kou']  )

        times += 1
        
    Log('B and can_buy_B:', test_zuoshi.B, test_zuoshi.can_buy_B)
