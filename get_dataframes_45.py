import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import hvplot.pandas
import pandas_datareader.data as web
import numpy as np
from fredapi import Fred
from scipy.optimize import minimize
from datetime import datetime, timedelta
import yfinance as yf

def getyfinance(tickers, from_date, to_date):
    
    
    
    
    # Reorganize the DataFrame
    # Separate ticker data
    # Concatenate the ticker DataFrames
    
    return_df = pd.DataFrame()
    
    for ticker in tickers:
        data = yf.download(ticker, start = from_date,end = to_date)['Close']
        return_df = pd.concat([return_df, data], axis = 1, join="outer")
    return_df.columns = tickers
    
    # return data
    return return_df 

def standard_deviation(weights, cov_matrix):
    variance = weights.T @ cov_matrix.T @ weights
    return np.sqrt(variance)
    
def expected_returns(weights, log_returns):
    return np.sum(log_returns.mean()*weights)*252

def sharpe_ratio(weights, log_returns,cov_matrix,risk_free_rate):
    return (expected_returns(weights,log_returns)-risk_free_rate) / standard_deviation(weights,cov_matrix)

def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)

class Portfolio_45:
    """
    This portfolio intends to serve people 45 years old to invest for <number_of_years>\n
    We show the same <number_of_years> historical information to justify the portfolio
    
    ...
    
    Instancing: 
    -----------
    (number_of_years)
    
    Properties: 
    -----------
      > number_of_years - all data are based on
      > weights - a list of weighting add-up to 1
      > tickers - a list of tickers (of which data available at Alpaca Market
      > data - dataframe of adjusted closing prices of the original tickers, index as datetime.date
      
    Methods:
    --------
      > get_return() - portfolio cumulative return 
      > get_beta_SPX() - portfolio calculated Beta on S&P 500 Index
      > get_sharpe_ratio() - portfolio calcuated sharge_ratio
    """
    
    def __init__(self,
                 tickers = [ 'XIC', 'VTI', 'IEFA', 'XBB' ],
                 number_of_years = 5
                ):
        """
        Provide number_of_years lookback for historical data
        Get historical data for number_of_years till today
        """
        # load env
        load_dotenv()
    
        self.number_of_years = number_of_years

        # this portfolio is recommended by ChatGPT for person 60 years old
        self.tickers = tickers
            
        # set the start,end date
        
        
        end_date = datetime.today()
        start_date = end_date - timedelta(days = number_of_years*365)
             
        # get portfolio historical data
        self.data = getyfinance( self.tickers, start_date, end_date ) 

        self.weights = self.get_optimal_weights()
        
        # calculate daily return of tickers
        daily_return = self.data.pct_change().fillna(0).dot(self.weights)
        
        # calculate and store weighted daily return of the portfolio
        self.daily_return = pd.DataFrame( { 'portfolio': daily_return })
        
    def get_return(self):
        """
        ## return portfolio cumulative historical percentage changes dataframe
        """
        return { 'Portfolio Cummulative return': (1+self.daily_return).cumprod() }
    
    def get_beta_SPX(self):
        """
        ## calculate the portfolio beta against S&P 500 index
        - To get S&P 500 index historical data, tried but could not find any API:
        > Alpaca,
        > yahoo_fin,
        > Alpaca neither, 
        > Nasdaq API (via postman) https://data.nasdaq.com/api/v3/datasets/WIKI/SPX.json?api_key=
        
        ## Download from: https://www.nasdaq.com/market-activity/index/spx/historical is manual\n
        pip install pandas_datareader
        """
        # read SPX date from the downloaded csv
        from_date = self.data.index[0]
        to_date = self.data.index[len(self.data)-1]
        spx_df = web.DataReader(['sp500'], 'fred', from_date, to_date)
        
        # change the index type from Timestamp to Date
        spx_df.index = spx_df.index.date
        
        # calculate and store S&P 500 daily return
        self.spx_df = spx_df.pct_change().fillna(0)
        
        cov_df = pd.concat([self.daily_return, self.spx_df], axis=1, join='inner').fillna(0)
        
        # Calculate 60 day rolling covariance of the portfolio
        covariance = cov_df['portfolio'].rolling(window=60).cov(cov_df['sp500'])
        
        # Calculate 60 day rolling variance of S&P 500
        variance_spx = cov_df['sp500'].rolling(window=60).var()
        
        # Computing beta
        self.beta_spx = covariance / variance_spx
        
        return { 'Rolling 60-day Beta on S&P500' : self.beta_spx }
    
    def get_sharpe_ratio(self):
        """
        ## calculate and return sharpe ration of the portfolio using annual standard deviation,\n
        average return for a year, and US 3-Month T-Bill latest rate as the risk free rate
        """

        # get RFR - according to investopedia (https://www.investopedia.com/terms/r/risk-freerate.asp)
        # US 3-month T-bill is usually used as the Risk Free Rate for US market
        # get that

        fred_api_key = os.getenv('FRED_STLOUIS_API_KEY')
        fred = Fred(api_key=fred_api_key)
        gs3m = fred.get_series('GS3M')/100
        
        # use latest gs3m as the RFR
        RFR = gs3m[-1]
        
        # Calculate the annualized standard deviation (252 trading days)
        annual_std = self.daily_return.std() * np.sqrt(252)
        
        # calculate and store sharpe ratio
        self.sharpe_ratio = ( (self.daily_return.mean() * 252) - RFR )/annual_std
    
        return { 'Portfolio Sharpe Ratio': self.sharpe_ratio }
    
    def get_optimal_weights(self):
        log_returns = np.log(self.data / self.data.shift(1)).dropna()
        cov_matrix = log_returns.cov() * 252

        fred_api_key = os.getenv('FRED_STLOUIS_API_KEY')
        fred = Fred(api_key=fred_api_key)
        ten_year_treasurey_rate = fred.get_series_latest_release('GS10')/100
        risk_free_rate = ten_year_treasurey_rate.iloc[-1]
        
        constraints = {'type':'eq','fun':lambda weights:np.sum(weights)-1}
        bounds = [(0,0.5) for _ in range(len(self.tickers))]
        
        initial_weights = np.array([1/len(self.tickers)]*len(self.tickers))
        
        #optimize the weights to maximize sharpe ratio
        optimized_results = minimize(neg_sharpe_ratio, initial_weights, 
                                     args=(log_returns, cov_matrix, risk_free_rate), 
                                     method='SLSQP', constraints=constraints, bounds=bounds)
        optimal_weights = optimized_results.x
        return optimal_weights
