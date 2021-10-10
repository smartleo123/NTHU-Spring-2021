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
            'Binance': {
                'pairs': ['BTC-USDT'],
            },
        }
        self.period = 17* 60
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_cross_status = None
        self.close_price_trace = np.array([])
        self.high_price_trace = np.array([])
        self.low_price_trace = np.array([])
        self.price_len = 50
        # self.ma_short = 5
        self.UP = 1
        self.DOWN = 2
        self.INIT_AMOUNT = 50000
        self.HOLD_AMOUNT = 20000


    def on_order_state_change(self,  order):
        Log("on order state change message: " + str(order) + " order price: " + str(order["price"]))

    def get_current_aroon_cross(self):
        # Log(str(self.high_price_trace))
        # Log(str(self.low_price_trace))

        macd, macdsignal, macdhist = talib.MACD(self.close_price_trace, fastperiod=12, slowperiod=26, signalperiod=9)
        # Log(str(macd) + "/" +str(macdsignal))
        # aroondown, aroonup = talib.AROON(self.high_price_trace, self.low_price_trace, timeperiod=14)
        # Log(str(self.high_price_trace)+"high")
        # aroonosc = talib.AROONOSC(self.high_price_trace, self.low_price_trace, timeperiod=14)[-1]
        # Log(str(aroondown[-1])+' / '+str(aroonup[-1]))
        if np.isnan(macd[-1]) or np.isnan(macdsignal[-1]):
            return None #, None
        if macd[-1] > macdsignal[-1]:
            return self.UP
        elif macd[-1] < macdsignal[-1]:
            return self.DOWN
        return None


    # called every self.period
    def trade(self, information):

        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        target_currency = pair.split('-')[0]  #ETH
        base_currency = pair.split('-')[1]  #USDT
        base_currency_amount = self['assets'][exchange][base_currency]  #現在本金
        target_currency_amount = self['assets'][exchange][target_currency] 
        # add latest price into trace
        close_price = information['candles'][exchange][pair][0]['close']
        high = information['candles'][exchange][pair][0]['high']
        low = information['candles'][exchange][pair][0]['low']
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        # only keep max length of ma_long count elements
        self.close_price_trace = self.close_price_trace[-self.price_len:]

        self.high_price_trace = np.append(self.high_price_trace, [float(high)])
        self.high_price_trace = self.high_price_trace[-self.price_len:]

        self.low_price_trace = np.append(self.low_price_trace, [float(low)])
        self.low_price_trace = self.low_price_trace[-self.price_len:]
        # calculate current ma cross status
        cur_cross = self.get_current_aroon_cross()
        if cur_cross is None:
            return []
        if self.last_cross_status is None:
            self.last_cross_status = cur_cross
            return []
        # cross up
        if self.last_type == 'sell' and cur_cross == self.UP and self.last_cross_status == self.DOWN:
            Log('buying 1 unit of ' + str(target_currency))
            self.last_type = 'buy'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': base_currency_amount/close_price-0.000001,
                    'price': low,
                    'type': 'LIMIT',
                    'pair': pair,
                }
            ]
        # cross down
        elif self.last_type == 'buy' and cur_cross == self.DOWN and self.last_cross_status == self.UP:
            Log('assets before selling: ' + str(self['assets'][exchange][base_currency]))
            self.last_type = 'sell'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': exchange,
                    'amount': -target_currency_amount,
                    'price': high,
                    'type': 'LIMIT',
                    'pair': pair,
                }
            ]

        self.last_cross_status = cur_cross
        return []