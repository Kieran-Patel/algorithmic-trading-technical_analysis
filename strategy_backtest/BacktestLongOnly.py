from BacktestBase import *


class BacktestLongOnly(BacktestBase):
    
    def run_sma_strategy(self, SMA1, SMA2):
        
        """
        SMA crossover strategy
        ======================
        BUY if short SMA crosses above long SMA.
        HOLD, and then SELL when short SMA crosses below long SMA
        """
        
        msg = f'\n\nRunning SMA strategy | SMA1={SMA1} & SMA2={SMA2}'
        msg += f'\nfixed costs {self.ftc} | proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount # reset initial capital
        
        self.data['SMA1'] = self.data['price'].rolling(SMA1).mean()
        self.data['SMA2'] = self.data['price'].rolling(SMA2).mean()
        
        for bar in range(SMA2, len(self.data)): #start value of SMA2 ensure there are SMA values available
            if self.position == 0:
                if self.data['SMA1'].iloc[bar] > self.data['SMA2'].iloc[bar]:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if self.data['SMA1'].iloc[bar] < self.data['SMA2'].iloc[bar]:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0
        self.close_out(bar)
        
        
    def run_momentum_strategy(self, momentum):
        
        """
        Momentum strategy
        =================
        BUY when rolling average (momentum) is positive.
        HOLD, and then SELL when rolling average is negative 
        """
        
        msg = f'\n\nRunning momentum strategy | {momentum} days'
        msg += f'\nfixed costs {self.ftc} | proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount # reset initial capital
        
        self.data['momentum'] = self.data['return'].rolling(momentum).mean()
        
        for bar in range(momentum, len(self.data)):
            if self.position == 0:
                if self.data['momentum'].iloc[bar] > 0:
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if self.data['momentum'].iloc[bar] < 0:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0
        self.close_out(bar)
        
        
    def run_mean_reversion_strategy(self, SMA, threshold):
        
        """
        Mean reversion strategy
        =======================
        BUY when current price is low enough relative to the SMA
        HOLD, and then SELL when current price has returned to the SMA level or above
        """
        
        msg = f'\n\nRunning mean reversion strategy | SMA={SMA} & thr={threshold}'
        msg += f'\nfixed costs {self.ftc} | proportional costs {self.ptc}'
        print(msg)
        print('=' * 55)
        
        self.position = 0
        self.trades = 0
        self.amount = self.initial_amount # reset initial capital
        
        self.data['SMA'] = self.data['price'].rolling(SMA).mean()
        
        for bar in range(SMA, len(self.data)):
            if self.position == 0:
                if (self.data['price'].iloc[bar] < self.data['SMA'].iloc[bar] - threshold):
                    self.place_buy_order(bar, amount=self.amount)
                    self.position = 1
            elif self.position == 1:
                if self.data['price'].iloc[bar] >= self.data['SMA'].iloc[bar]:
                    self.place_sell_order(bar, units=self.units)
                    self.position = 0
        self.close_out(bar)
        
        
if __name__ == '__main__':
    
    def run_strategies():
        
        lobt.run_sma_strategy(5,20)
        lobt.run_momentum_strategy(20)
        lobt.run_mean_reversion_strategy(30,3)
        
    lobt = BacktestLongOnly('TIME_SERIES_DAILY', 'AAPL', 'close', '2019-01-01', '2019-12-31', 1000, 10.0, 0.01, True, None)
    
    run_strategies()