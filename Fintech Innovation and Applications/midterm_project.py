#import time

class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Bitfinex': {
                'pairs': ['BTC-USDT'],
            },
        }
        self.period = 1 * 60
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_cross_status = None
        self.close_price_trace = np.array([])
        self.ma_long = 150
        self.ma_short = 50
        self.UP = 1
        self.DOWN = 2

    def on_order_state_change(self,  order):
        Log("on order state change message: " + str(order) + " order price: " + str(order["price"]))

    def get_current_ma_cross(self):
        #s_ma_1 = talib.EMA(self.close_price_trace, self.ma_short)[-2]
        s_ma = talib.EMA(self.close_price_trace, self.ma_short)[-1]
        #l_ma_1 = talib.EMA(self.close_price_trace, self.ma_long)[-2]
        l_ma = talib.EMA(self.close_price_trace, self.ma_long)[-1]
        if np.isnan(s_ma) or np.isnan(l_ma):
            return None
        if s_ma > l_ma:  #and s_ma_1 < l_ma_1:
            return self.UP
        #if s_ma < l_ma  and s_ma_1 > l_ma_1:
        return self.DOWN


    # called every self.period
    def trade(self, information):
        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        target_currency = pair.split('-')[0]  #BTC
        base_currency = pair.split('-')[1]  #USDT
        base_currency_amount = self['assets'][exchange][base_currency] 
        target_currency_amount = self['assets'][exchange][target_currency] 
        
        # add latest price into trace
        close_price = information['candles'][exchange][pair][0]['close']
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        
        # only keep max length of ma_long count elements
        self.close_price_trace = self.close_price_trace[-self.ma_long:]
        
        # calculate current ma cross status
        cur_cross = self.get_current_ma_cross()
        if cur_cross is None:
            return []
        if self.last_cross_status is None:
            self.last_cross_status = cur_cross
            return []
        
        # calculate the amount to buy
        #amount = base_currency_amount/close_price

        
        # cross up
        if self.last_type == 'sell' and cur_cross == self.UP and self.last_cross_status == self.DOWN:
            Log('buying 1 unit of ' + str(target_currency))
            #Log('buying '+ str(amount) + ' unit of' + str(target_currency))
            self.last_type = 'buy'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': 1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
       
        elif self.last_type == 'buy' and close_price / (100000 - base_currency_amount ) >= 1.04 :
            Log('assets before selling: ' + str(self['assets'][exchange][base_currency]))
            self.last_type = 'sell'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': -target_currency_amount,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        '''
        elif self.last_type == 'buy' and close_price / (100000 - base_currency_amount ) <= 0.95 :
            Log('assets before selling: ' + str(self['assets'][exchange][base_currency]))
            self.last_type = 'sell'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': -target_currency_amount,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]

        '''
        '''
        # cross down
        elif self.last_type == 'buy' and cur_cross == self.DOWN and self.last_cross_status == self.UP:
            Log('assets before selling: ' + str(self['assets'][exchange][base_currency]))
            self.last_type = 'sell'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': -target_currency_amount,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        '''        
        self.last_cross_status = cur_cross
        return []