#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class midClass():
    def __init__(self, this_exchange):
        '''
        初始化数据填充交易所的信息，首次获取价格，首次获取account信息
        设定好密钥……

        Args:
            this_exchange: FMZ的交易所结构

        '''
        self.init_timestamp = time.time()
        self.exchange = this_exchange
        self.name = self.exchange.GetName()
        self.jyd = self.exchange.GetCurrency()

    def get_account(self):
        '''
        获取账户信息

        Returns:
            获取信息成功返回True，获取信息失败返回False
        '''
        self.Balance = '---'
        self.Amount = '---'
        self.FrozenBalance = '---'
        self.FrozenStocks = '---'

        try:
            self.account = self.exchange.GetAccount()

            self.Balance =  self.account['Balance']
            self.Amount = self.account['Stocks']
            self.FrozenBalance =  self.account['FrozenBalance']
            self.FrozenStocks = self.account['FrozenStocks']
            return True
        except:
            return False

    def get_ticker(self):
        '''
        获取市价信息

        Returns:
            获取信息成功返回True，获取信息失败返回False
        '''
        self.high = '---'
        self.low = '---'
        self.Sell =  '---'
        self.Buy =  '---'
        self.last =  '---'
        self.Volume = '---'

        try:
            self.ticker = self.exchange.GetTicker()

            self.high = self.ticker['High']
            self.low = self.ticker['Low']
            self.Sell =  self.ticker['Sell'] # 卖一价 ask
            self.Buy =  self.ticker['Buy'] # 买一价 bid
            self.last =  self.ticker['Last'] # 最后成交价
            self.Volume = self.ticker['Volume'] # 最近成交量
            return True
        except:
            return False


    def get_depth(self):
        '''
        获取深度信息

        Returns:
            获取信息成功返回True，获取信息失败返回False
        '''
        self.Ask = '---'
        self.Bids = '---'

        try:
            self.Depth = self.exchange.GetDepth()
            self.Ask = self.Depth['Asks']
            self.Bids = self.Depth ['Bids']
            return True
        except:
            return False



    def get_ohlc_data(self, period = PERIOD_M5):
        '''
        获取K线信息

        Args:
            period: K线周期，PERIOD_M1 指1分钟, PERIOD_M5 指5分钟, PERIOD_M15 指15分钟,
            PERIOD_M30 指30分钟, PERIOD_H1 指1小时, PERIOD_D1 指一天。
        '''
        self.ohlc_data = exchange.GetRecords(period)



    def create_order(self, order_type, price, amount):
        '''
        post一个挂单信息

        Args:
            order_type：挂单类型，'buy'指挂买单，'sell'指挂卖单
            price：挂单价格
            amount:挂单数量

        Returns:
            挂单Id号，可用以取消挂单
        '''
        if order_type == 'buy':
            try:
                order_id = self.exchange.Buy( price, amount)
            except:
                return False

        elif order_type == 'sell':
            try:
                order_id = self.exchange.Sell( price, amount)
            except:
                return False

        return order_id

    def cancel_order(self, order_id):
        '''
        取消一个挂单信息

        Args:
            order_id：希望取消的挂单ID号

        Returns:
            取消挂单成功返回True，取消挂单失败返回False
        '''
        return self.exchange.CancelOrder(order_id)

    def refreash_data(self):
        '''
        刷新信息

        Returns:
            刷新信息成功返回 'refreash_data_finish!' 否则返回相应刷新失败的信息提示
        '''

        if not self.get_account():
            return 'false_get_account'

        if not self.get_ticker():
            return 'false_get_ticker'
        # if not self.get_depth():
        #     return 'false_get_depth'
        # try:
        #     self.get_ohlc_data()
        # except:
        #     return 'false_get_K_line_info'

        return 'refreash_data_finish!'

