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
    page_title="Portfolio DataFrames and Analysis",
    page_icon="✅",
    layout="wide",
)

st.markdown("# Dataframes and Analysis")
st.sidebar.header("Dataframes and Analysis")

#@st.experimental_memo

# dashboard title
st.title("Portfolio DataFrames and Analysis")

ports = { 'Portfolio for 60 years and above investing $40K for 10 years': {
              'tickers': [ 'IEF', 'VCIT', 'NOBL', 'USMV' ], 
              'amount' : 40000, 
              'class': Portfolio_60,
              'sim_years' : 10 },
          'Portfolio for 30-44 year olds investing $22K for 20 years': {
              'tickers': ['VCN.TO', 'XUS.TO', 'XEF.TO', 'ZAG.TO'],
              'amount' : 22000,
              'class': Portfolio_45,
              'sim_years' : 20 },
          'Portfolio for 18-30 years olds investing $14K for 30 years': {
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

port = port_class(port_tickers, 5)
# create two columns for charts
fig_col1, fig_col2 = st.columns(2)



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

    st.markdown("#") 
    chart_data_col4 =  port.data  
    with chart_container(chart_data_col4):
        st.write('Porfolio Daily Returns')
    st.markdown('### Daily Returns')
    st.line_chart(chart_data_col4) 
    
                
