from get_dataframes_30 import Portfolio_30
from get_dataframes_45 import Portfolio_45
from get_dataframes_60 import Portfolio_60
from monte_carlo_sim import monte_carlo_sim
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.chart_container import chart_container
from markdownlit import mdlit
import pandas as pd
import datetime
import streamlit as st
import os
import hvplot.pandas
import time

st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="✅",
    layout="wide",
)

#@st.experimental_memo

# dashboard title
st.title("Real-Time / Live Portfolio Dashboard")

ports = { 'Portfolio for 60 years above [ IEF, VCIT, NOBL, USMV ] starting $40K': {
              'tickers': [ 'IEF', 'VCIT', 'NOBL', 'USMV' ], 
              'amount' : 40000, 
              'class': Portfolio_60,
              'sim_years' : 10 },
          'Portfolio for 30-44 years [ XIC, VTI, IEFA, XBB ] starting $22K': {
              'tickers': ['XIC','VTI','IEFA','XBB'],
              'amount' : 22000,
              'class': Portfolio_45,
              'sim_years' : 20 },
          'Portfolio for 18-30 years [ XSD, TAN, SOXX, XLK, VTI ] starting $14K': {
              'tickers': ['XSD','TAN','SOXX','XLK','VTI'],
              'amount' : 14000,
              'class': Portfolio_30,
              'sim_years' : 30 }
        }

drop_down = st.selectbox('Pick a portfolio', ports.keys())

port_class = ports[drop_down]['class']
port_tickers = ports[drop_down]['tickers']
port_amount = ports[drop_down]['amount']
port_sim_years = ports[drop_down]['sim_years']

port = port_class(port_tickers, 5)
 
# create three columns
kpi1, kpi2, kpi3 = st.columns(3)

cum_return = port.get_return()['Portfolio Cummulative return'].iloc[-1][0]
sharpe_ratio = port.get_sharpe_ratio()['Portfolio Sharpe Ratio'][0]

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
    label="A/C Balance ＄",
    value=f"$ {round(port_amount*cum_return,2)} "
)

# create two columns for charts
fig_col1, fig_col2 = st.columns(2)

with fig_col1:
    chart_data_col1 = port.get_return()['Portfolio Cummulative return'].fillna(0)
    with chart_container(chart_data_col1):
        st.write ("Analysis of Portfolio Returns using Cummulative returns")
    st.markdown("### Portfolio Return")
    st.line_chart(chart_data_col1)
   
with fig_col2:
    # chart_data_col2 = port.get_beta_SPX()['Rolling 60-day Beta on S&P500'].dropna()
    # with chart_container(chart_data_col2):
    #     st.write("Analysis of Portfolio Beta over S&P 500")
    st.markdown("### Portfolio Beta")
    st.line_chart(port.get_beta_SPX()['Rolling 60-day Beta on S&P500'].dropna())
#create another two columns for charts 
fig_col3, fig_col4 = st.columns(2)
with fig_col3:   
               
    st.markdown("### Portfolio Data")
    filtered_df = dataframe_explorer(port.data.sort_index(ascending=False))
    st.dataframe(filtered_df,
                width=700, height=400,
                column_config={
                    "portfolio": st.column_config.LineChartColumn(
                    "adjusted closing prices",
                    width="medium",
                    y_min=0,
                    y_max=100
                    )}
                )
with fig_col4:
    st.write() 
    chart_data_col4 =  port.data.sort_index(ascending=False)  
    with chart_container(chart_data_col4):
        st.write('Porfolio Daily Returns')
    st.markdown('### Daily Returns')
    st.line_chart(chart_data_col4) 
# creating a single-element container
placeholder = st.empty()
final_mean_last = 0
alpha_min_last = 0
alpha_max_last = 0

# near real-time / live feed simulation
for seconds in range(20):

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
            st.markdown("### Monte Carlo Simulation - cumulative return")
            st.line_chart(sim_data)
        with fig_col2:
            st.markdown("### Monte Carlo Simulation - balance")
            st.line_chart(sim_data * port_amount)
            
        st.markdown("### Detailed Data View")
        st.dataframe(sim_data)
        time.sleep(1)
        mdlit(
    (
        """
??? Bonus
    @(🖥️)(A Link to our Team Github)(https://github.com/EthanB1/Team-3-Project)
"""
    )
)