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
    page_title="Monte Carlo Sim",
    page_icon="📈",
    layout="wide",
)
st.markdown("# Monte Carlo Sim")
st.sidebar.header("Monte Carlo Sim")


#@st.experimental_memo

# dashboard title
st.title("Real-Time / Live Portfolio Dashboard")

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


st.header("Monte Carlo performance")
# creating a single-element container
placeholder = st.empty()
final_mean_last = 0
alpha_min_last = 0
alpha_max_last = 0

# near real-time / live feed simulation
for seconds in range(5):

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
        time.sleep(1)