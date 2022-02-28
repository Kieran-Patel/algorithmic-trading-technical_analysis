import requests
import numpy as np
import pandas as pd


def get_data(symbol, price_label, function, interval=None):
    
    base_url = 'https://www.alphavantage.co/query?'
    outputsize = 'full'
    api_key = '' #<INSERT API KEY>
    
    params = {'function' : function, 
              'symbol' : symbol, 
              'interval' : interval,
              'outputsize' : outputsize, 
              'apikey' : api_key}
        
    response = requests.get(base_url, params=params)
    response_json = response.json()
    _, header = response.json()
    df = pd.DataFrame.from_dict(response_json[header], orient='index')

    df.index = pd.to_datetime(df.index)
    
    df.columns = [i.split(' ')[1] for i in df.columns] # rename columns

    for col in df.columns:
        df[col] = df[col].astype(float) # convert columns to floats

    df = df.sort_index() # sort starting from earliest date
        
    price_df = pd.DataFrame(df[price_label])
    price_df = price_df.rename(columns={price_label : 'price'})
        
    price_df['return'] = np.log(price_df / price_df.shift(1)) 
    price_df.dropna(inplace=True)
        
    return price_df