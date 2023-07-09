import os
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import yahoo_fin.stock_info as ys
import pandas_datareader.data as web
import numpy as np
from fredapi import Fred
from scipy.optimize import minimize
from datetime import datetime, timedelta
'''
def get_data_alpaca(tickers, from_date, to_date, alpaca_api):
    
    # Set timeframe to "1Day" for Alpaca API
    timeframe = "1Day"
            
    # Get number_of_years' worth of historical data for tickers
    data_df = alpaca_api.get_bars(
            tickers,
            timeframe,
            adjustment = 'all',
            start = from_date.isoformat(),
            end = to_date.isoformat()
    ).df
    
    if len(data_df) == 0:
        return data_df
    
    data_df.index = data_df.index.date
    
    return_df = pd.DataFrame()
    
    for ticker in tickers:
            ticker_df = data_df.loc[data_df['symbol']==ticker]['close']
            return_df = pd.concat( [return_df, ticker_df],
                        axis=1,
                        join='outer')
    
    return_df.columns = tickers

    return return_df 

def get_data_yahoo(tickers, from_date, to_date):

    return_df = pd.DataFrame()
    
    for ticker in tickers:
            data = ys.get_data(ticker, from_date, to_date)['adjclose']
            if len(data) == 0:
                return data
            data.index = data.index.date
            return_df = pd.concat([return_df, data], axis = 1, join="outer")

    return_df.columns = tickers
    
    # return data
    return return_df 
'''
def standard_deviation(weights, cov_matrix):
    variance = weights.T @ cov_matrix.T @ weights
    return np.sqrt(variance)
    
def expected_returns(weights, log_returns):
    return np.sum(log_returns.mean()*weights)*252

def sharpe_ratio(weights, log_returns,cov_matrix,risk_free_rate):
    return (expected_returns(weights,log_returns)-risk_free_rate) / standard_deviation(weights,cov_matrix)

def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)


class Portfolio:
    
    def __init__(self,
                 number_of_years = 5,
                 tickers = None
                ):
        """
        Provide number_of_years lookback for historical data
        Get historical data for number_of_years till today
        """
        # load env
        load_dotenv()
    
        self.number_of_years = number_of_years
        self.weights = []

        # get portfolio historical data    
        
        # Load Alpaca keys required by the APIs
        alpaca_api_key = os.getenv('ALPACA_API_KEY')
        alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')

        # Create the Alpaca API object
        alpaca_api = tradeapi.REST(
           alpaca_api_key,
           alpaca_secret_key,
           api_version = 'v2'
        )
    
        self.alpaca_api = alpaca_api
        
        # set the start,end date - as pd.timestamp
        today_date = pd.to_datetime('today').normalize()   
        today = pd.Timestamp(today_date,tz='America/New_York')
        start = today - pd.Timedelta(365*number_of_years, 'd')
    
        # prep for Yahoo - as datetime.datetime.timestamp
        end_date = datetime.today()
        start_date = end_date - timedelta(days = number_of_years*365)

        self.alpaca_from = start
        self.alpaca_to = today
        self.yahoo_from = start_date
        self.yahoo_to = end_date
        
        if tickers != None: 
            self.tickers = tickers
            self.data = self.get_data_alpaca( tickers ) 
            if len(self.data) == 0:
                self.data = self.get_data_yahoo( tickers )
       
        else:
            self.tickers = []
            self.data = pd.DataFrame()
            
    def gen_port(self):
        
        if len(self.data) == 0:
            self.data = None
            self.weights = None
            self.daily_return = None
            return None

        self.weights = self.get_optimal_weights()
        
        # calculate daily return of tickers
        daily_return = self.data.pct_change().fillna(0).dot(self.weights)
        
        # calculate and store weighted daily return of the portfolio
        self.daily_return = pd.DataFrame( { 'portfolio': daily_return })
        
        return True

            
    def get_data(self, ticker):
             
        # get ticker historical data
        self.tickers.append(ticker)
        data = self.get_data_alpaca( [ticker] ) 
        if len(data) == 0:
            data = self.get_data_yahoo( [ticker] )
        if len(data) == 0:
            return None
        
        if len(self.data) == 0:
            self.data = data
        else:
            self.data = pd.concat([self.data,data],axis=1,join='outer')
            
        return data
        
    def get_return(self):
        """
        ## return portfolio cumulative historical percentage changes dataframe
        """
        return (1+self.daily_return).cumprod()
    
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
        self.beta_spx = pd.DataFrame(self.beta_spx)
        self.beta_spx.columns = ['beta']
        
        return self.beta_spx
    
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
    
        return self.sharpe_ratio
    
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
    
    def get_data_alpaca(self, tickers):
    
        # Set timeframe to "1Day" for Alpaca API
        timeframe = "1Day"
            
        # Get number_of_years' worth of historical data for tickers
        try:
            data_df = self.alpaca_api.get_bars(
                tickers,
                timeframe,
                adjustment = 'all',
                start = self.alpaca_from.isoformat(),
                end = self.alpaca_to.isoformat()
            ).df
        except HTTPError:
            return pd.DataFrame()
    
        if len(data_df) == 0:
            return data_df
    
        data_df.index = data_df.index.date
    
        return_df = pd.DataFrame()
    
        for ticker in tickers:
            ticker_df = data_df.loc[data_df['symbol']==ticker]['close']
            return_df = pd.concat( [return_df, ticker_df],
                        axis=1,
                        join='outer')
    
        return_df.columns = tickers

        return return_df 

    def get_data_yahoo(self, tickers):

        return_df = pd.DataFrame()
    
        for ticker in tickers:
            data = ys.get_data(ticker, self.yahoo_from, self.yahoo_to)['adjclose']
            if len(data) == 0:
                return data
            data.index = data.index.date
            return_df = pd.concat([return_df, data], axis = 1, join="outer")

        return_df.columns = tickers
    
        return return_df 