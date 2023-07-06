import pandas as pd
import numpy as np

def monte_carlo_sim( data, weights, number_of_sim=500, num_trading_days=252 ):
    """
    The function takes data as the historical dataframe of tickers, with datetime.date as the index, adjusted closing price as columns
    """
    last_prices = data[-1:].values.tolist()[0]
    daily_returns = data.pct_change()
    mean_returns = daily_returns.mean().tolist()
    std_returns = daily_returns.std().tolist()

    results = []

    for n in range(number_of_sim):
        simvals = [[p] for p in last_prices]
        for s in range(len(last_prices)):
            for i in range(num_trading_days):
                simvals[s].append(simvals[s][-1] * (1 + np.random.normal(mean_returns[s], std_returns[s])))
        sim_df = pd.DataFrame(simvals).T.pct_change()
        sim_df = sim_df.dot(weights)
        results.append((1 + sim_df.fillna(0)).cumprod())

    cumulative_returns = pd.concat(results, axis=1)

    confidence_interval = cumulative_returns.iloc[-1, :].quantile(q=[0.025, 0.975])
    
    return { 'cumulative_returns' : cumulative_returns, 'confidence_interval' : confidence_interval }
