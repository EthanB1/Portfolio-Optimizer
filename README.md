# Team-3-Project

### TEAM 3

#### Amar, Ethan, Kala, Scott (in Alphabetic order)

### Concept

The portfolio optimization tool is a dashboard which displays sample Tax Free Savings Account (TFSA) portfolios for the average Canadian at three different stages of life: ages 18-30, ages 30-44, and age 60 and above. Referencing Statistics Canada, we found the average TFSA account size per age group and used those figures as starting portfolio balances. 
![TFSA](Resources/Canadian%20TFSA%20statistics.jpg)

We developed the portfolio optimization tool to help Canadians find the ideal weights for securities in a portfolio for those who wish to build a TFSA, while also providing sample portfolios for those who want an example of a diversified ETF portfolio for their age group.

Our method for optimizing our sample portfolios involved prompting ChatGPT with description of a persons age, risk tolerance and starting balance to create examples of diversified, low fee portfolios of ETFs. We then pull the historical ETF data in the sample portfolio using yfinance and alpaca APIs. From there, we wrote a script that calculates portfolio beta, portfolio Sharpe ratio, and a function which maximizes the Sharpe ratio in the portfolio. This function produces optimal weights for a given portfolio that minimize volatility while maximising return. We then run a monte carlo simulation to project portfolio balances into the future using a 95% confidence ratio. Finally, we created a dashboard that displays and charts the performance of the portfolios, the Sharpe ratios and the outcomes of the monte carlo simulations. 

### Goals

Project object is to find a tool which would provide user 
invest their funds to get best return and at the same time keep their 
money safe. Use the most advanced technology which is both user 
friendly and cost effective Keep factors like, cost, return, 
transparency, adherence to compliances in place

### Challenges

Determine who the users Accordingly users are selected
in 3 age brackets show to get suitable portfolio options; we thought 
best portfolio should be diversified

### Limitations

Even with best efforts there could be limitations on our
projections since these are based on estimates using statistical tools 
like Monte Carlo simulation

### Techinal summary

#### Pull data from web

We pull historical market data of pre-set portfolio tickers, via various APIs available in open source community. 

The portfolios are staticaly defined in the presentation run code, and the data sources are hardcoded in the category classes, for now, until maybe next iteration when we add proper error handling, the asembling of any ticker would be allowed.

#### Cleanup and transform

We then clean-up/transform the data pulled, into a date indexed dataframe having daily adjusted closing prices as one column for each ticker in the portfolio. 

#### Optimal weights

We use scipy to calculate the optimal weights distribution amoungst the tickers. Based on this weights distribution, the historical performance of the portfolio is optimized, as well as the future investment.

#### Analyze and express

Allowing to pick one portfolio from a dropdown list, the attributes of the portfolio are shown in a dashboard, in forms of key performance indicators, diagrams and dataframes.

#### Monte Carlo Simulation

For each different category of portfolio, our Monte Carlo Simulation model simulates for 30, 20, and 10 years. We then show the simulation results in cumulative return and dollar amount from specific initial investment of 14K, 22K and 40K, matching the investment of a typical Canadian in 30, 45 and 60 years old.

#### Depandencies

* pandas
* datetime, time, numpy
* os, dotenv - used to hide keys and passwords
* requests, yfinance, alpaca_trade_api, pandas_datareader, fredapi - pull data
* scipy.optimize - calculate optimal weights
* hvplot.pandas, streamlit, streamlit_extras - presentation

#### Resources

* [Finance Modeling Prep](https://site.financialmodelingprep.com/financial-summary/XBB) - replace XBB in the url with any ticker. It is good place to find most tickers.
* [Pandas Data Reder](https://pandas-datareader.readthedocs.io/en/latest/remote_data.html#remote-data-alphavantage) - a good place to tap into multiple API sources.
* [St.Louis FRED](https://fred.stlouisfed.org/categories/115?cid=115&et=&pageID=1&t=) - site to get US treasury bonds data for the Risk Free Rate (RFR), and S&P 500. Get API key.
* [Alpaca Markets](https://app.alpaca.markets) - site to pull most tickers' historical data. Get API keys.

## References

* https://docs.streamlit.io/library/api-reference/data/st.column_config (streamlit line chart)
* https://genymoney.ca/average-savings-by-age-in-canada/(average tfsa for canadians)
* https://www.youtube.com/watch?v=9GA2WlYFeBU(optimized weights calculation)
* https://www.youtube.com/watch?v=Ynt7Etci1KU(info on streamlit)
* https://fred.stlouisfed.org/docs/api/fred/ (api for risk free rate )
* https://www.youtube.com/watch?v=Km2KDo6tFpQ(interactive dashboard for streamlit)
* https://extras.streamlit.app/(streamlit extras info)
* https://www.springfinancial.ca/blog/lifestyle/average-net-worth-by-age-canada