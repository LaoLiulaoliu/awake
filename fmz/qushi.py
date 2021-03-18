
class qushi_class():
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
        self.can_buy_B = _N(self.can_buy_B, self.amount_N )
        self.can_sell_B = _N(self.B, self.amount_N )
        
    def make_trade_by_dict(self, trade_dicts):
        '''
        用来批量完成交易订单
        
        Attributes：
            trade_list:已提交的交易请求的id
        '''
        for this_trade in trade_dicts:
            this_trade_id = self.jys.create_order( this_trade['side'], this_trade['price'] , this_trade['amount'] ) 
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
        self.min_buy_B = min(self.min_trade_B, self.can_buy_B)
        self.min_sell_B = min(self.min_trade_B, self.B)
        
        self.min_trade_money = self.min_trade_B* self.jys.Buy


    
    def condition_qushi(self, change_pct ):
        '''
        根据市场价格情况来做交易判定的条件
        Args:
            change_pct：表示价格变化多少来确定一次交易（假设根据之前一段时间均值判断）
            
        Returns：
            min_trade_B: 一手最多交易的商品币数量
            min_trade_money: 一手最多交易的计价币数量
        
        '''
        mean_price = sum( [x['Close'] for x in self.jys.ohlc_data[-12*24:]])/(12*24)
        do_buy = self.jys.Buy > mean_price* (100.0 + change_pct )/100.0
        do_sell = self.jys.Sell < mean_price/ ((100.0 + change_pct )/100.0)
        
        if do_buy or do_sell:
            rt = 'Buy' if do_buy else 'Sell'
            return rt
        else:
            return False
    
    def make_trade_dicts(self, hands_num, change_pct ):
        self.condition_chicang(hands_num)
        rt = self.condition_qushi( change_pct )
        this_trade_dicts = []
        if rt:
            if rt == 'Buy':
                if self.min_buy_B > 10**-self.amount_N:
                    this_trade_dicts.append({
                        'side':'buy',
                        'price':self.jys.Buy,
                        'amount':self.min_buy_B
                    })
            else:
                if self.min_sell_B > 10**-self.amount_N:
                    this_trade_dicts.append({
                        'side':'sell',
                        'price':self.jys.Sell,
                        'amount':self.min_sell_B
                    })
            return this_trade_dicts
        else:
            return False


def main():
    
    Set_amount_N = 4
    Set_price_N = 4
    
    hands_num = 20
    price_change_percentage = 2
    
    test_mid = mid_class(exchange)
    Log(test_mid.refreash_data())
    test_qushi = qushi_class(test_mid , Set_amount_N, Set_price_N)
    
    while True:
        
        Sleep(1000)
        try:
            test_qushi.refreash_data()

            now_trade_dicts = test_qushi.make_trade_dicts(hands_num, price_change_percentage)
            if now_trade_dicts:
                test_qushi.make_trade_by_dict(now_trade_dicts)
                now_trade_dicts = False
        except:
            pass