import numpy as np
import pandas as pd
from sklearn import linear_model
from datetime import datetime


def run_SMA_strategy(data, start, end, amount, tc, SMA1, SMA2):
    
    data = data.copy()
    
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d') 
    data = data.loc[start:end]
    
    data['SMA1'] = data['price'].rolling(SMA1).mean()
    data['SMA2'] = data['price'].rolling(SMA2).mean()
    data.dropna(inplace=True)
    
    data['position'] = np.where(data['SMA1'] > data['SMA2'], 1, -1)
    data['strategy'] = data['position'].shift(1) * data['return']
    data.dropna(inplace=True) # needed for shift, opposed to np.where
    
    trades = data['position'].diff().fillna(0) != 0
    data.loc[trades,'strategy'] -= tc
    
    data['creturns'] = amount * data['return'].cumsum().apply(np.exp)
    data['cstrategy'] = amount * data['strategy'].cumsum().apply(np.exp)
    
    aperf = data['cstrategy'].iloc[-1]
    operf = aperf - data['creturns'].iloc[-1]
        
    return data, round(aperf, 2), round(operf, 2)


def run_Mom_strategy(data, start, end, amount, tc, momentum=1):
    
    data = data.copy()
    
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    data = data.loc[start:end]
    
    data['momentum'] = data['return'].rolling(momentum).mean()
    data.dropna(inplace=True)

    data['position'] = np.sign(data['momentum'])
    data['strategy'] = data['position'].shift(1) * data['return']
    data.dropna(inplace=True) # needed for shift, opposed to np.sign
    
    trades = data['position'].diff().fillna(0) != 0 
    data.loc[trades,'strategy'] -= tc

    data['creturns'] = amount * data['return'].cumsum().apply(np.exp)
    data['cstrategy'] = amount * data['strategy'].cumsum().apply(np.exp)
    
    aperf = data['cstrategy'].iloc[-1]
    operf = aperf - data['creturns'].iloc[-1]

    return data, round(aperf, 2), round(operf, 2)


def run_MR_strategy(data, start, end, amount, tc, SMA, threshold):
    
    data = data.copy()
    
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d') 
    data = data.loc[start:end]
    
    data['SMA'] = data['price'].rolling(SMA).mean()
    data['distance'] = data['price'] - data['SMA']
    data.dropna(inplace=True)
    
    data['position'] = np.where(data['distance'] > threshold, -1, np.nan) # sell signals
    data['position'] = np.where(data['distance'] < -threshold, 1, data['position']) # buy signals
    data['position'] = np.where(data['distance'] * data['distance'].shift(1) < 0, 0, data['position']) # price and SMA cross over
    
    data['position'] = data['position'].ffill().fillna(0)
    data['strategy'] = data['position'].shift(1) * data['return']
    data.dropna(inplace=True) # needed for shift, opposed to np.sign
    
    trades = data['position'].diff().fillna(0) != 0
    data.loc[trades,'strategy'] -= tc
    
    data['creturns'] = amount * data['return'].cumsum().apply(np.exp)
    data['cstrategy'] = amount * data['strategy'].cumsum().apply(np.exp)
    
    aperf = data['cstrategy'].iloc[-1]
    operf = aperf - data['creturns'].iloc[-1]
        
    return data, round(aperf, 2), round(operf, 2)    