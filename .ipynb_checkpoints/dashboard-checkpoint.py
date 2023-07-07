from get_dataframes_30 import Portfolio_30
from get_dataframes_45 import Portfolio_45
from get_dataframes_60 import Portfolio_60
from monte_carlo_sim import monte_carlo_sim
import pandas as pd
import datetime
import streamlit as st
import os
import hvplot.pandas
import time

history_years = 5

st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="✅",
    layout="wide",
)

#@st.experimental_memo

# dashboard title
st.title(f"Portfolio {history_years}-Year Historical Analysis and Monte Carlo Simulation")

ports = { 'Portfolio for 60 years above investing $40K for 10 years': {
              'tickers': [ 'IEF', 'VCIT', 'NOBL', 'USMV' ], 
              'amount' : 40000, 
              'class': Portfolio_60,
              'sim_years' : 10 },
          'Portfolio for 30-44 years investing $22K for 20 years': {
              'tickers': ['VCN.TO', 'XUS.TO', 'XEF.TO', 'ZAG.TO'],
              'amount' : 22000,
              'class': Portfolio_45,
              'sim_years' : 20 },
          'Portfolio for 18-30 years investing $14K for 30 years': {
              'tickers': ['XSD','TAN','SOXX','XLK','VTI'],
              'amount' : 14000,
              'class': Portfolio_30,
              'sim_years' : 30 },
          'Portfolio for 30-44 years investing $22K for 20 years (alternative)': {
              'tickers': [ 'XIC.TO', 'VTI', 'IEFA', 'XBB' ],
              'amount' : 22000,
              'class': Portfolio_45,
              'sim_years' : 20 }
        }

drop_down = st.selectbox('Pick a portfolio', ports.keys())

port_class = ports[drop_down]['class']
port_tickers = ports[drop_down]['tickers']
port_amount = ports[drop_down]['amount']
port_sim_years = ports[drop_down]['sim_years']

port = port_class(port_tickers, history_years)

# create three columns
kpi1, kpi2, kpi3 = st.columns(3)

cum_return = port.get_return()['Portfolio Cummulative return'].iloc[-1][0]
sharpe_ratio = port.get_sharpe_ratio()['Portfolio Sharpe Ratio'][0]
amount_str = "${:,}".format(port_amount)

# fill in those three columns with respective metrics or KPIs
kpi1.metric(
    label="Cumulative Return ⏳",
    value=round(cum_return,5)
)

kpi2.metric(
    label="Sharpe Ratio 💍",
    value=round(sharpe_ratio,5)
)

kpi3.metric(
    label=f"If we had invested {amount_str} {history_years} years ago: ",
    value="${:,}".format(round(port_amount*cum_return,2))
)

# create two columns for charts
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    st.markdown("### Portfolio Return")
    st.line_chart(port.get_return()['Portfolio Cummulative return'].fillna(0))
   
with fig_col2:
    st.markdown("### Portfolio Beta over S&P500")
    st.line_chart(port.get_beta_SPX()['Rolling 60-day Beta on S&P500'].dropna())
                
df_col1, df_col2 = st.columns(2)
return_df = round(port.get_return()['Portfolio Cummulative return'] * port_amount)
return_df = return_df.rename(columns={ 'portfolio' : 'balance' })
return_df['balance'] = return_df['balance'].apply(lambda x: f"${x:,}")
return_df = pd.concat([return_df, port.get_return()['Portfolio Cummulative return']],axis=1)
return_df.rename(columns={'portfolio':'%'}, inplace=True)

# make all amounts show $ and comma
pd.options.display.float_format = '${:,}'.format

with df_col1:
    st.markdown("### Portfolio Data")
    st.dataframe(port.data.sort_index(ascending=False),
             width=500, height=300)
#             column_config={
#                "data": st.column_config.LineChartColumn(
#                "adjusted closing prices",
#                width="medium"
#                )}
#            )
with df_col2:
    st.markdown("### Portfolio Return")
    st.dataframe(return_df.sort_index(ascending=False),
             width=500, height=300)
#             column_config={
#                "balance": st.column_config.LineChartColumn(
#                f"${port_amount} growth",
#                width="medium"
#                )}
#            )

# creating a single-element container
placeholder = st.empty()

final_mean_last = 0
alpha_min_last = 0
alpha_max_last = 0

# near real-time / live feed simulation
for seconds in range(3):

    sim = monte_carlo_sim(port.data, port.weights, 22, 252*port_sim_years)
    sim_data = sim['cumulative_returns']

    # creating KPIs

    final_mean = sim_data.iloc[-1].mean()
    alpha_min = sim['confidence_interval'][0.025]
    alpha_max = sim['confidence_interval'][0.975]

    with placeholder.container():

        # create three columns
        kpi1, kpi2, kpi3 = st.columns(3)

        # fill in those three columns with respective metrics or KPIs
        kpi1.metric(
            label="Average Final Return ⏳",
            value=round(final_mean,5),
            delta=round(final_mean - final_mean_last,5)
        )
        
        kpi2.metric(
            label="0.05 Confidence Level min 💍",
            value=round(alpha_min,5),
            delta=alpha_min - alpha_min_last
        )
        
        kpi3.metric(
            label="0.05 Confidence Level max 💍",
            value=round(alpha_max,5),
            delta=alpha_max - alpha_max_last
        )
        
        final_mean_last = final_mean
        alpha_min_last = alpha_min
        alpha_max_last = alpha_max

        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown(f"### Monte Carlo Simulation for {port_sim_years} years - cumulative return")
            st.line_chart(sim_data)
        with fig_col2:
            st.markdown(f"### Monte Carlo Simulation in {port_sim_years} years - balance")
            st.line_chart(sim_data * port_amount)
            
        st.markdown("### Detailed Data View")
        st.dataframe(sim_data.sort_index(ascending=False))
        time.sleep(1)
        
print('end of for')