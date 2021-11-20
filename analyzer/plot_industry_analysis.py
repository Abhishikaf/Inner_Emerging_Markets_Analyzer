# Function to plot the GDP per capita for speficied industry for all target states for years 2016-2020
# The input arguments : gdp_state_5year_filter - 5 year gdp data for the states
#                       industry - name of industry to be anlyzed

# The function returns a unstacked dataframe containing the per capita data for the specified industry, to be used for future analysis


import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

from bokeh.palettes import Oranges256 as oranges
from bokeh.sampledata.us_states import data as us_states
from bokeh.plotting import figure
from bokeh.io import output_notebook, show

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_industry_analysis(gdp_state_5year_filter,population_by_state,industry):
    gdp_generic_df = gdp_state_5year_filter.get_group(industry)

    gdp_generic_df = gdp_generic_df.set_index(['GeoName','Description'])

    gdp_capita_generic = gdp_generic_df / population_by_state* 1000000

    gdp_capita_generic = gdp_capita_generic.reset_index()

    #melting the df arounf GeoName and Description
    gdp_capita_generic = gdp_capita_generic.melt(['GeoName','Description'], var_name='Date', value_name='Value')

    # drop Description column and unstack
    unstacked_gdp_capita_generic = gdp_capita_generic.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)

    # find percent growths. if the 2020 value is not available, do not include it and return a relevant title.
    if (unstacked_gdp_capita_generic["Value"].loc["2020"] == 0).sum() > 0:
        generic_growth_rank = ((unstacked_gdp_capita_generic["Value"].loc["2019"]/unstacked_gdp_capita_generic["Value"].loc["2016"] - 1) * 100).sort_values()
        text="2016 - 2019"
    else:
        generic_growth_rank = ((unstacked_gdp_capita_generic["Value"].loc["2020"]/unstacked_gdp_capita_generic["Value"].loc["2016"] - 1) * 100).sort_values()
        text="2016 - 2020"


    st.header(f"GDP Per Capita for {industry} for target states - {text}")
    generic_plot = px.bar(gdp_capita_generic, 
                            x='Date',
                            y='Value',
                            facet_col = "GeoName",
                            facet_col_wrap = 4,
                            facet_row_spacing = 0.1,
                            width = 1200,
                            height = 500,
                            labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
    generic_plot.update_layout()
    st.plotly_chart(generic_plot)



    generic_plot_2 = px.bar(generic_growth_rank,
                              labels = { 'GeoName': 'State', 'value': f"% growth of {industry}"},
                              color_discrete_sequence = ['red']*len(generic_growth_rank),
                              width = 1200
                           )

    generic_plot_2.update_layout(title_text = f"Percent Growth for {text} for: {industry}",
                                    showlegend = False)

    st.plotly_chart(generic_plot_2)

    return unstacked_gdp_capita_generic