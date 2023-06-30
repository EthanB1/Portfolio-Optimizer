from datetime import datetime, timedelta
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import hvplot.pandas

def get_data60(number_of_years):
            
    # load env
    load_dotenv()
    
    # Load Alpaca keys required by the APIs
    alpaca_api_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')

    # Create the Alpaca API object
    alpaca_api = tradeapi.REST(
        alpaca_api_key,
        alpaca_secret_key,
        api_version = 'v2'
    )
    
    # Set timeframe to "1Day" for Alpaca API
    timeframe = "1Day"
            
    # set the start,end date
    today = datetime.today() - timedelta(days=1)
    start = today - timedelta(days=365*number_of_years)

    today = pd.Timestamp('2023-06-28',tz='America/New_York')
    start = today - pd.Timedelta(365*number_of_years, 'd')
    
    tickers = [ 'IEF', 'VCIT', 'NOBL', 'USMV' ]
    #tickers = ['AGG','SPY']
    # Get number_of_years' worth of historical data for tickers
    data_df = alpaca_api.get_bars(
        tickers,
        timeframe,
        start = start.isoformat(),
        end = today.isoformat()
    ).df
    
    data_df.index = data_df.index.date
    
    # Reorganize the DataFrame
    # Separate ticker data
    ief_df = data_df.loc[data_df['symbol']=='IEF']
    vcit_df = data_df.loc[data_df['symbol']=='VCIT']
    nobl_df = data_df.loc[data_df['symbol']=='NOBL']
    usmv_df = data_df.loc[data_df['symbol']=='USMV']

    # Concatenate the ticker DataFrames
    return_df = pd.concat([ief_df['close'],vcit_df['close'],nobl_df['close'],usmv_df['close']],
                          axis=1,join="inner",keys=['IEF','VCIT','NOBL','USMV'])

    
    # return data
    return { 'weight' : [0.4, 0.3, 0.2, 0.1], 'data': return_df }