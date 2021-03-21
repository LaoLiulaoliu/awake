#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## 所有看起来有效的网格策略，都是在用长期风险换取短期收益 （看起来一直在赚钱，突然有一天本都亏没了）
## 大部分的趋势策略（诸如MACD，EMA这类的简单判定）用近期风险换取长期收益 （看起来一直在亏钱，突然有一天赚了一点点，然后继续亏）

# 人们都容易忽略长期风险，因为短期收益而欢喜

## 优化策略的方法
# 1、优化价格判定条件
# 2、优化持仓判定条件
# 3、优化交易表单的制作函数

import time
from sklearn.linear_model import LinearRegression

def make_MACD(Kline, short_period, long_period, mid_period):
    DIFF = make_DIF(Kline, short_period, long_period)
    DEA = make_DEA(DIFF, mid_period)
    MACDs = []
    for i in range(len(DEA)):
        MACDs.append(2 * (DEA[i] - DIFF[i]))
    return MACDs
    
def make_DIF(Kline, short_period, long_period):
    EMA_short = make_EMA(Kline, short_period)
    EMA_long = make_EMA(Kline, long_period)
    DIFs = []
    the_len = len(EMA_short)
    for i in range(the_len):
        DIFs.append(EMA_short[i - the_len] - EMA_long[i - the_len])
    return DIFs

def make_DEA(DIFF, mid_period):
    return make_EMA(DIFF, mid_period)
    
def make_EMA(Kline, period):
    this_Kline = Kline[-period:]
    Log(this_Kline)
    EMAs = []
    try:
        EMAs.append( this_Kline[0]['Close'] )
        for i in range(len(this_Kline) -1):
            EMAs.append( (2*this_Kline[i+1]['Close'] + (period - 1)*EMAs[i]) / (period + 1) )
    except:  # when calculate DIFs
        EMAs.append( this_Kline[0] )
        for i in range(len(this_Kline) -1):
            EMAs.append( (2*this_Kline[i+1] + (period - 1)*EMAs[i]) / (period + 1) )
            
    return EMAs



class Qushi():
    def __init__(self, mid_class, amount_N, price_N):
        '''
        设定好初始需要考虑的参数
        Args:
            mid_class: 所使用的交易所中间层
            amount_N：数量小数点限制
            price_N：价格小数点限制
            
        Attributes：
            amount_N：数量小数点限制
            price_N：价格小数点限制
            init_time：初始时间
            last_time：上一次执行操作的时间
            trade_list:交易请求的id
        '''
        self.jys = mid_class
        
        self.init_time = time.time()
        self.last_time = time.time()
        
        self.amount_N = amount_N
        self.price_N = price_N
        
        self.trade_list = []
    
    def refreash_data(self):
        '''
        用来从交易所获取最新的价格和数量信息
        
        Attributes：
            B：商品币数量
            money：计价币数量
            can_buy_B：当前理论可购买商品币数量
            Buy_price:当前市场上最近的一单挂单买价
            Sell_price：当前市场上最近的一单挂单卖价
        '''
        
        self.jys.refreash_data()
        self.B = self.jys.Amount
        self.money = self.jys.Balance
        self.Buy_price = self.jys.Buy
        self.Sell_price = self.jys.Sell
        self.can_buy_B = self.money/ self.Sell_price
        self.can_buy_B = round(self.can_buy_B, self.amount_N)
        self.can_sell_B = round(self.B, self.amount_N)
        
    def make_trade_by_dict(self, trade_dicts):
        '''
        用来批量完成交易订单
        
        Attributes：
            trade_list:已提交的交易请求的id
        '''
        for this_trade in trade_dicts:
            this_price = round(this_trade['price'], self.price_N )
            this_amount = round(this_trade['amount'], self.amount_N )
            this_trade_id = self.jys.create_order( this_trade['side'], this_price , this_amount ) 
            self.trade_list.append( this_trade_id )
    
    def condition_chicang(self, hands_num):
        '''
        根据持仓情况来做交易判定的条件
        Args:
            hands_num：表示交易一共几手（我们假设当前每次交易不高于一手）
            
        Attributes：
            min_trade_B: 一手最多交易的商品币数量
            min_trade_money: 一手最多交易的计价币数量
        
        '''
        self.min_trade_B = (self.can_buy_B + self.B) / hands_num
        self.min_buy_B = min(self.min_trade_B, self.can_buy_B) # 一直买，有可能资产不足
        self.min_sell_B = min(self.min_trade_B, self.B)
        
        # 如果吃掉别人卖单，这里可以用self.jys.Sell
        self.min_trade_money = self.min_trade_B * self.jys.Buy


    
    def condition_qushi(self, change_pct ):
        '''
        根据市场价格情况来做交易判定的条件
        Args:
            change_pct：表示价格变化多少来确定一次交易（假设根据之前一段时间均值判断）
            
        Returns：
            min_trade_B: 一手最多交易的商品币数量
            min_trade_money: 一手最多交易的计价币数量
        
        '''
        # 5min 一个蜡烛图，12个一小时，列表越往后时间越新，先忽略nan
        mean_price = sum( [x['Close'] for x in self.jys.ohlc_data[-12*24:]])/(12*24)
        # 假设追涨杀跌
        do_buy = self.jys.Buy > mean_price * (100.0 + change_pct) / 100.0
        # 两种计算方式略微不同: 1 / (1 + 0.2) = 0.83,  1 * (1 - 0.2) = 0.8
        do_sell = self.jys.Sell < mean_price / ((100.0 + change_pct )/100.0)
        
        if do_buy or do_sell:
            return 'Buy' if do_buy else 'Sell'
        else:
            return False


    def condition_qushi_macd(self, macd_threshold, short_period = 12, long_period = 26, mid_period = 9):
        '''
        根据市场价格情况来做交易判定的条件
        Args:
            short_period: MACD的EMA短周期
            long_period: MACD的EMA长周期
            mid_period: DIF的EMA周期
            macd_threshold: MACD预计变化百分之多少取信
        Returns：
            min_trade_B: 一手最多交易的商品币数量
            min_trade_money: 一手最多交易的计价币数量
        '''
        Kline = self.jys.ohlc_data(86400)
        MACD = make_MACD(Kline, short_period, long_period, mid_period)
        X = [[x+1, x+1] for x in range(mid_period)]
        x = [[MACD[i - 2], MACD[i - 1]] for i in range(2, mid_period)]
        y = MACD[2:]
        reg = LinearRegression().fit(X, y)
        next_macd = reg.predict( [[MACD[-2], MACD[-1]]] )
        mean_macd = sum(MACD) / len(MACD)
        
        more_than = (100 + macd_threshold) / 100
        less_than = (100 - macd_threshold) / 100
        
        rt = False
        if  next_macd > macd_threshold and MACD[0] < 0 :
            rt = 'Buy'
        elif next_macd < -macd_threshold and MACD[0] > 0:
            rt = 'Sell'
        
        return rt

    def make_trade_dicts(self, hands_num, change_pct ):
        self.condition_chicang(hands_num)
        rt = self.condition_qushi_macd( change_pct )
        this_trade_dicts = []

        # 如果一直涨，会一下买很多，设置两次买之间的条件，比如5min
        if rt == 'Buy':
            if self.min_buy_B > 10**-self.amount_N: # 一直买，有可能资产不足，大于最小（最好计算手续费在内）
                this_trade_dicts.append({
                    'side':'buy',
                    'price':self.jys.Buy, # 想吃别人单，用self.jys.Sell, 吃单手续费高
                    'amount':self.min_buy_B
                })
        elif rt == 'Sell':
            if self.min_sell_B > 10**-self.amount_N:
                this_trade_dicts.append({
                    'side':'sell',
                    'price':self.jys.Sell,
                    'amount':self.min_sell_B
                })
        else:
            return False
        return this_trade_dicts


def main():
    Set_amount_N = 4
    Set_price_N = 4
    
    hands_num = 20
    price_change_percentage = 2
    macd_threshold = 10
    
    test_mid = midClass(exchange)
    Log(test_mid.refreash_data())
    test_qushi = Qushi(test_mid , Set_amount_N, Set_price_N)
    
    while True:
        Sleep(1000)
        try:
            test_qushi.refreash_data()

            now_trade_dicts = test_qushi.make_trade_dicts(hands_num, macd_threshold) # use price_change_percentage before
            if now_trade_dicts:
                test_qushi.make_trade_by_dict(now_trade_dicts)
                now_trade_dicts = False
        except:
            pass
