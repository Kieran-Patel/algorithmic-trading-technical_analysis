import numpy as np
import pandas as pd
from sklearn import linear_model
from datetime import datetime


def select_data(data, start, end):
   
    # need to add condition for when it's intraday and so formatting is different
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    data_subset = data.loc[start:end]
    
    return data_subset


def prepare_features(data, start, end, lags):
     
    data_subset = select_data(data, start, end)
    data_subset = data_subset.copy()
    
    feature_columns = []
    
    for lag in range(1, lags + 1):
        col = f'lag_{lag}'
        data_subset[col] = data_subset['return'].shift(lag)
        feature_columns.append(col)

    data_subset.dropna(inplace=True) # because shift used above in for loop
    return data_subset, feature_columns


def fit_model(data, model, start, end, lags):
    
    data_subset, feature_columns = prepare_features(data, start, end, lags)
    
    # this application of linear regression is rubbish since you should be predicting price, not buy vs sell
    if model == 'linear':
        reg = linear_model.LinearRegression()
        reg = reg.fit(data_subset[feature_columns], np.sign(data_subset['return']))
        
    elif model == 'logistic':
        reg = linear_model.LogisticRegression(C=1e6, solver='lbfgs', multi_class='ovr', max_iter=1000)
        reg = reg.fit(data_subset[feature_columns], np.sign(data_subset['return']))
        
    elif model == 'OLS':
        reg = np.linalg.lstsq(data_subset[feature_columns], np.sign(data_subset['return']), rcond=None)[0]
        
    return reg
        

def run_Reg_strategy(data, start_in, end_in, start_out, end_out, amount, tc, model, lags=3):
        
    reg = fit_model(data, model, start_in, end_in, lags)
    
    data_subset, feature_columns = prepare_features(data, start_out, end_out, lags)
    
    if model in ('linear','logistic'):
        prediction = reg.predict(data_subset[feature_columns])
    elif model == 'OLS':
        prediction = np.sign(np.dot(data_subset[feature_columns], reg))
        
    data_subset['prediction'] = prediction
    data_subset['strategy'] = data_subset['prediction'] * data_subset['return']
    
    trades = data_subset['prediction'].diff().fillna(0) != 0
    data_subset.loc[trades,'strategy'] -= tc
    
    data_subset['creturns'] = amount * data_subset['return'].cumsum().apply(np.exp)
    data_subset['cstrategy'] = amount * data_subset['strategy'].cumsum().apply(np.exp)
    
    aperf = data_subset['cstrategy'].iloc[-1]
    operf = aperf - data_subset['creturns'].iloc[-1]
        
    return data_subset, round(aperf, 2), round(operf, 2)
    
    