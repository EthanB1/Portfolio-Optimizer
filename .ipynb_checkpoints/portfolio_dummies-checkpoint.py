"""
This is a dummy inplace of two functions that return two plots to show on the dashboard
get_data(number_of_years): return df of historical data
get_tickers(number_of_years): return dictionary { market: 'stock', tickers: ['AGG','SPY'], weights: [0.5,0.5]}
"""
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from MCForecastTools1 import MCSimulation
import hvplot.pandas

def get_tickers(number_of_years):
    
    return { "market": "stock", "tickers": ['AGG','SPY'], "weights": [0.4,0.6] }
            
def get_data(number_of_years, tickers):
            
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
    today = pd.Timestamp('2023-06-16',tz='America/New_York')
    start = today - pd.Timedelta(365*number_of_years, 'd')
    
    # Get number_of_years' worth of historical data for tickers
    data_df = alpaca_api.get_bars(
        tickers,
        timeframe,
        start = start.isoformat(),
        end = today.isoformat()
    ).df
    
    # Reorganize the DataFrame
    # Separate ticker data
    agg_df = data_df.loc[data_df['symbol']=='AGG']
    spy_df = data_df.loc[data_df['symbol']=='SPY']

    # Concatenate the ticker DataFrames
    df_stock_data = pd.concat([agg_df,spy_df],axis=1,join="inner",keys=['AGG','SPY'])

    # return data
    return df_stock_data
            
def portfolio_returns(number_of_years, initial_amount):
    """
    portfolio_returns(data_df,number_of_years): return sim_df, using Alpaca data from the homework 
    """
     
    # get data, tickers and weights from other module files
    
    ticker_dic = get_tickers(number_of_years)
    data_df = get_data(number_of_years, ticker_dic['tickers'])
    
    # Configuring a Monte Carlo simulation to forecast 30 years cumulative returns
   
    MC_sim = MCSimulation(
        portfolio_data = data_df,
        weights = ticker_dic['weights'],
        num_simulation = 500,
        num_trading_days = 252*number_of_years
    )
    
    # calculate simulation, please need to get rid of the displays of the sim journey
    sim = MC_sim.calc_cumulative_return() 
    
    # generate three time lines of return: median, min, max
    sim_df = pd.DataFrame( { 'median': sim.median(axis=1), 'min': sim.min(axis=1), 'max': sim.max(axis=1) } )
    
    # do some tidy up so that the x is dates
    
    # return the plots
    return [sim_df, sim_df*initial_amount]