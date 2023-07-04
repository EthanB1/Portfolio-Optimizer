from get_dataframes_60 import Portfolio_60
import pandas as pd
import datetime
import streamlit as st

port60 = Portfolio_60(5)

st.dataframe(port60.data, width=400, height=700,
             column_config={
        "portfolio": st.column_config.LineChartColumn(
            "closing price for 5 years",
            width="medium",
            y_min=0,
            y_max=100,
         ),
    }
            )