import requests
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class BacktestBase(object):
    
    """
    Attributes
    ==========
    function: str
        dataset to be retrieved from alpha vantage API
    symbol: str
        RIC to be used
    market: str
        the exchange market of your choice
    price_label: str
        name of price column from dataset
    start: str
        start date for data selection
    end: str
        end date for data selection
    amount: float
        amount to be invested either once or per trade
    ftc: float
        fixed transaction costs per trade
    ptc: float
        proportional transaction costs per trade
    verbose: bool
        choose whether to display individual trades or not
    interval: str
        time interval for intraday data (default None)
        
    Methods
    =======
    get_data:
        retrieves and prepares the base data set
    plot_data:
        plots the closing price for the symbol
    get_date_price:
        returns the date and price for the given bar
    print_balance:
        prints out the current (cash) balance
    print_net_wealth:
        prints out the current net wealth (balance + investments)
    place_buy_order:
        places a buy order
    place_sell_order:
        places a sell order
    close_out:
        closes out a long or short position at end of time period
    """
    
    def __init__(self, function, symbol, price_label, start, end, amount, ftc=0.0, ptc=0.0, verbose=True, interval=None):
        
        self.function = function
        self.symbol = symbol
        self.price_label = price_label
        self.start = start
        self.end = end
        self.initial_amount = amount
        self.amount = amount
        self.ftc = ftc
        self.ptc = ptc
        self.units = 0
        self.position = 0
        self.trades = 0
        self.verbose = verbose
        self.interval = interval
        self.get_data()
        
        
    def get_data(self):
        
        base_url = 'https://www.alphavantage.co/query?'
        outputsize = 'full'
        api_key = '' #<INSERT API KEY>

        params = {'function' : self.function, 
                  'symbol' : self.symbol,
                  'outputsize' : outputsize,
                  'apikey' : api_key}

        response = requests.get(base_url, params=params)
        response_json = response.json()
        _, header = response.json()
        df = pd.DataFrame.from_dict(response_json[header], orient='index')

        df.index = pd.to_datetime(df.index)
        df.columns = [col.split(' ')[1] for col in df.columns] # rename columns

        for col in df.columns:
            df[col] = df[col].astype(float) # convert columns to floats

        df = df.sort_index() # sort starting from earliest date

        price_df = pd.DataFrame(df[self.price_label])
        price_df = price_df.rename(columns={self.price_label : 'price'})
        
        start = datetime.strptime(self.start, '%Y-%m-%d')
        end = datetime.strptime(self.end, '%Y-%m-%d') 
        price_df = price_df.loc[start:end]

        price_df['return'] = np.log(price_df / price_df.shift(1)) 

        self.data = price_df.dropna()
        
    
    def plot_data(self, cols=None):
        
        if cols is None:
            cols = ['price']

        plt.figure(figsize=(30,10))
        plt.plot(self.data.index, self.data[cols])
        
        
    def get_date_price(self, bar):
        
        date = self.data.index[bar]
        price = self.data.price.iloc[bar]
        
        return date, price
    
    
    def print_balance(self, bar):
        
        date, price = self.get_date_price(bar)
        print(f'{date} | current balance {self.amount:.2f}')
        
    
    def print_net_wealth(self, bar):
        
        date, price = self.get_date_price(bar)
        net_wealth = self.units * price + self.amount
        print(f'{date} | current net wealth {net_wealth:.2f}')
        
    
    def place_buy_order(self, bar, units=None, amount=None):
        
        date, price = self.get_date_price(bar)
        
        if units is None:
            units = int(amount / price)
            
        self.amount -= (units * price) * (1 + self.ptc) + self.ftc
        self.units += units
        self.trades += 1
        
        if self.verbose:
            print(f'{date} | BUYING {units} units at {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)
            
    
    def place_sell_order(self, bar, units=None, amount=None):
        
        date, price = self.get_date_price(bar)
        
        if units is None:
            units = int(amount / price)
            
        self.amount += (units * price) * (1 - self.ptc) - self.ftc
        self.units -= units
        self.trades += 1
        
        if self.verbose:
            print(f'{date} | SELLING {units} units at {price:.2f}')
            self.print_balance(bar)
            self.print_net_wealth(bar)
            
    
    def close_out(self, bar):
        
        date, price = self.get_date_price(bar)
        
        self.amount += self.units * price
        self.units = 0
        self.trades += 1
        
        if self.verbose:
            print(f'{date} | inventory {self.units} units at {price:.2f}')
            print('=' * 55)
        
        print(f'Final balance   [$] {self.amount:.2f}')
        perf = ((self.amount - self.initial_amount) / self.initial_amount) * 100
        print(f'Net performance [%] {perf:.2f}')
        print(f'Trades Executed [#] {self.trades:.2f}')
        print('=' * 55)
        
        
if __name__ == '__main__':
    
    bb = BacktestBase('DIGITAL_CURRENCY_DAILY', 'BTC', 'GBP', 'close', '2010-01-01', '2019-12-31', 1000, 0.0, 0.0, False, None)
    print(bb.data.head())
    bb.plot_data()
        
        
        
            