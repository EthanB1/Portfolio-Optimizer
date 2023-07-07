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
    page_icon="📊",
    layout="wide",
)

st.markdown("# Portfolio Returns")
st.sidebar.header("Portfolio Returns")

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