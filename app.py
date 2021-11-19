
#import required libraries

import os
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import hvplot.pandas

from bokeh.palettes import Oranges256 as oranges
from bokeh.sampledata.us_states import data as us_states
from bokeh.plotting import figure
from bokeh.io import output_notebook, show

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    layout="wide",
)
st.title("Identifying Emerging markets in the US")

@st.cache

def get_api_key():
    #load the API keys stored in .env file
    load_dotenv()

    # https://apps.bea.gov/api/signup/index.cfm to signup for API key for Bureau of Economic Analysis

    # https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf for user guide

    #get BEA API key from .env file
    bea_api_key=os.getenv("BEA_API_KEY")
    return bea_api_key

@st.cache
def get_Data_List(bea_api_key):
    # set up query URL
    bea_url = "http://apps.bea.gov/api/data?UserID=" + bea_api_key + "&method=GETDATASETLIST&ResultFormat=JSON" 

    #send request to BEA
    bea_response = requests.get(bea_url).json()["BEAAPI"]["Results"]
    return bea_response

@st.cache
def get_Data(bea_api_key):
    # this query will get the data for all states for the last five years for personal income per capita.
    bea_states_personal_income_linecode_query_url = "http://apps.bea.gov/api/data?UserID=" + bea_api_key + "&method=GetData&datasetname=Regional&TableName=SQINC1&GeoFIPS=STATE&LineCode=3&Year=LAST5&ResultFormat=JSON"

    #query for last five years personal income by state.
    personal_income_by_state_5year = pd.DataFrame(requests.get(bea_states_personal_income_linecode_query_url).json()["BEAAPI"]["Results"]["Data"])
    return personal_income_by_state_5year


# Read the API KEY
bea_api_key = get_api_key()

# get data list from bea 
bea_response = get_Data_List(bea_api_key)

# get the regional table dataframe
personal_income_by_state_5year = get_Data(bea_api_key)

# clip out the unnecessary columns
personal_income_by_state_5year=personal_income_by_state_5year[["GeoName", "TimePeriod", "DataValue"]]

# Used str.replace() to remove the ',' from the Income datavalue and convert to float from string
personal_income_by_state_5year['DataValue'] = personal_income_by_state_5year['DataValue'].str.replace(',', '').astype('float')

# Filter the dataframe to get just the states

list_of_states = [ 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
                  'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
                  'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 
                   'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
                   'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
                  'Wisconsin', 'Wyoming']

personal_income_state_filter = personal_income_by_state_5year['GeoName'].isin(list_of_states)
personal_income_filter_by_state = personal_income_by_state_5year[personal_income_state_filter]

# Setting the time period to be the index and converting the datatype from string to dateTime
personal_income_filter_by_state_2 = personal_income_filter_by_state
personal_income_filter_by_state = personal_income_filter_by_state.set_index('TimePeriod')
personal_income_filter_by_state.index = pd.to_datetime(personal_income_filter_by_state.index)

# Group the data by state and calculate the average personal income for every year from 2017 to current year

personal_income_filter_annual = personal_income_filter_by_state.groupby('GeoName').resample('A').mean()
personal_income_filter_annual = personal_income_filter_annual.reset_index()
personal_income_filter_annual['TimePeriod'] = personal_income_filter_annual['TimePeriod'].dt.date
personal_income_filter_annual = personal_income_filter_annual.set_index('TimePeriod')


st.header(" Annual Personal Income ranked in ascending order")
# Bar chart for states with an interactive slider
# SelectBox for selecting the timeperiod to view the percapita Personal Income
time = st.selectbox("Choose a Time Period:", personal_income_filter_annual.index.unique())

# Generating plotly express graphs based on the user selected year
fig = px.bar(personal_income_filter_annual.loc[time].sort_values('DataValue'),
             x = 'GeoName',
             y = 'DataValue' ,
             width = 1000,
             title = f'Annual Personal Income for all states in ascending order -{time}',
             labels = { 'GeoName': 'State', 'DataValue': 'Personal Income($)'}, # Axis labels to be displayed on the chart and while hovering
             color_discrete_sequence = ['pink']*len(personal_income_filter_annual)) 

# Extracting the data to display the limiting line
df = personal_income_filter_annual.loc[time].sort_values('DataValue') 

# Adding the line onto the plot
fig.add_shape(type = 'line',
                x0 = df['GeoName'][20], # Place the line at the 21st element to seperate the last 20 states
                y0 = -5000,
                x1 = df['GeoName'][20],
                y1 = max(df['DataValue']),
                line = dict(color = 'Red', width = 3, dash = 'dashdot'))
st.plotly_chart(fig)

#Plots for data pivoted by states

st.header("Personal Income for Fiscal Quarters from 2017 Q1 - 2021 Q2")
# Convert TimePeriod to datetime to get results in a sorted time manner
personal_income_filter_by_state_2['TimePeriod'] = pd.to_datetime(personal_income_filter_by_state_2['TimePeriod']).dt.date

# Pivoting the dataframe around GeoName and TimePeriod
personal_income_melt = personal_income_filter_by_state_2.melt(id_vars = ['GeoName', 'TimePeriod'])

# st.write(personal_income_melt)
# # PLots with x value = timeperiod
# layout_plots = personal_income_melt.hvplot.bar(
#     x='TimePeriod',
#     y='value',
#     by='variable',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()

# layout_plots = px.bar(personal_income_melt, 
#                         x='TimePeriod',
#                         y='value',
#                         color = 'GeoName',
#                         facet_col = "GeoName",
#                         facet_col_wrap = 6,
#                         facet_row_spacing = 0.03,
#                         width = 1500,
#                         height = 2400)

# st.plotly_chart(layout_plots)

# Line plot for percapita personal income for all the states for all the fiscal quarters. 
layout_plots_line = px.line(personal_income_melt, 
                        x='TimePeriod',
                        y='value',
                        color = 'GeoName',
                        width = 1000,
                        height = 800,
                        labels = { 'TimePeriod': 'Fiscal Quarter', 'value': 'Personal Income($)', 'GeoName':'State'},
                        title = "5 year Personal Income for all states")
                     
                        
st.plotly_chart(layout_plots_line)

#Sort the States by Personal Income
personal_income_sorted = personal_income_filter_by_state_2.sort_values(by = 'DataValue')

#Pivoting the table around Geoname and Timeperiod
personal_income_melt_2 = personal_income_sorted.melt(id_vars = ['GeoName', 'TimePeriod'])

st.header('US Map with Personal Income for Q2 of 2021')

# Dataframe grouped by state and extracted the last element from each group which is the personal income value for 2021Q2

personal_income_2021Q4 = personal_income_sorted.sort_values('TimePeriod').groupby('GeoName').last()

# loading US states boundary data which is available in bokeh as a part of bokeh.sampledata.us_states
us_states_df = pd.DataFrame(us_states).T


# reset index for merging
personal_income_2021Q4 = personal_income_2021Q4.reset_index()

# deleting states of Alaska, Hawaii and District of Columbia
us_states_df = us_states_df[~us_states_df["name"].isin(['Alaska', "Hawaii", "District of Columbia"])]

# Merge the two dataframes
us_states_df = us_states_df.merge(personal_income_2021Q4[["GeoName", "DataValue"]], how="left", left_on="name", right_on="GeoName")

# Sort the resulting dataframe by geoname to add the state codes for generating the choropleth graph
us_states_df = us_states_df.sort_values('GeoName')

# Add the state code column to the dataframe
us_states_df['code'] = ['AL','AZ','AR','CA','CO','CT','DE','FL','GA','ID',
                        'IL','IN','IA','KS','KY','LA','ME','MD','MA','MI',
                        'MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY',
                        'NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
                        'TX','UT','VT','VA','WA','WV','WI','WY']

# Hover text
us_states_df['text'] = us_states_df["GeoName"] + '<br>' + 'Per Capita PI = $' + us_states_df['DataValue'].astype(str)

# Generate the choropleth map
fig1 = go.Figure(data=go.Choropleth(
    locations=us_states_df['code'], # Spatial coordinates
    z = us_states_df['DataValue'], # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'blackbody' ,
    colorbar_title = "USD",
    autocolorscale=False,
    text=us_states_df['text'], # hover text
    marker_line_color='white'# line markers between states
    
  
))

fig1.update_layout(
        geo_scope='usa', # limite map scope to USA,
        title_text = " Map of US with Personal Income in Q2 of 2021",
         height = 800
         )#margin={"r":0,"t":0,"l":0,"b":0}

st.plotly_chart(fig1, use_container_width = True)


#begin process to filter states to focus analysis on. filter bottom 20 by personal income in 2020Q4.
lowest_20_states_df = us_states_df.nsmallest(20, "DataValue")

# unstack dataframe 
personal_income_filter_by_state = personal_income_filter_by_state.reset_index()
unstacked_personal_income_by_state = personal_income_filter_by_state.set_index(['GeoName', 'TimePeriod']).unstack(level=0)

# make new dataframe with the increase in personal income per state for this time period

personal_income_growth_2017to2021Q2 = ((unstacked_personal_income_by_state.transpose()["2021-04-01"] / unstacked_personal_income_by_state.transpose()["2017-01-01"]) - 1) * 100
personal_income_growth_2017to2021Q2_temp = personal_income_growth_2017to2021Q2.reset_index().sort_values(by = 0)

st.header("Percent growth personal income 2017Q1 to 2021Q2")

fig2 = px.bar(personal_income_growth_2017to2021Q2_temp,
              x = 'GeoName',
              y = 0,
             width = 1000,
             title = "Percent growth personal income 2017Q1 to 2021Q2 sorted in ascending order",
             labels = { 'GeoName': 'State', '0' : 'Percent Personal Income Growth(%)'}, # Axis labels to be displayed on the chart and while hovering
             color_discrete_sequence = ['pink']*len(personal_income_filter_annual)) 

personal_income_growth_2017to2021Q2_temp = personal_income_growth_2017to2021Q2_temp.reset_index(drop = True)
# Adding the line onto the plot
fig2.add_shape(type = 'line',
                x0 = personal_income_growth_2017to2021Q2_temp['GeoName'][20], # Place the line at the 21st element to seperate the last 20 states
                y0 = -2,
                x1 = personal_income_growth_2017to2021Q2_temp['GeoName'][20],
                y1 = 30,
                line = dict(color = 'Red', width = 3, dash = 'dashdot'))
st.plotly_chart(fig2)


st.header(" Personal Income with Percent Growth")

# Creating a new Dataframe to plot the two metrics
personal_income_vs_percentage_growth = pd.DataFrame()
personal_income_vs_percentage_growth['GeoName'] = personal_income_growth_2017to2021Q2_temp['GeoName']
personal_income_vs_percentage_growth['Percent_Growth'] = personal_income_growth_2017to2021Q2_temp[0]
personal_income_vs_percentage_growth = personal_income_vs_percentage_growth.merge(us_states_df[['GeoName', 'DataValue']], how = 'inner', on = 'GeoName')
personal_income_vs_percentage_growth = personal_income_vs_percentage_growth.sort_values(by = 'DataValue')

# Define a subplot figure to plot both the graphs together
sub_fig = make_subplots(specs = [[{"secondary_y": True}]])

# First generate the line figure for percentage growth
fig3 = px.line(x = personal_income_vs_percentage_growth['GeoName'],
               y = personal_income_vs_percentage_growth['Percent_Growth'],
               color_discrete_sequence = ['red']*len(personal_income_vs_percentage_growth)                    
               )

# Define a figure for plotting the bar graph for Per Capita Personal Income
fig4 = px.bar(x = personal_income_vs_percentage_growth['GeoName'],
              y = personal_income_vs_percentage_growth['DataValue'] ,
              color_discrete_sequence = ['pink']*len(personal_income_vs_percentage_growth),
              width = 1000
            ) 

# Define second axis for percent growth and define mode to plot markers alongwith the line graph
fig3.update_traces(yaxis = "y2",mode='markers+lines')

# Add both the figures on the sub plot figure
sub_fig.add_traces(fig4.data + fig3.data)
sub_fig.update_layout(width = 1000, height = 500, title_text = " Personal Income with Percentage Growth")
sub_fig.layout.xaxis.title = "State"
sub_fig.layout.yaxis.title = " Personal Income for 2021Q2"
sub_fig.layout.yaxis2.title = "Percentage Growth from 2017Q1 to 2021Q2"

st.plotly_chart(sub_fig)

# filter the rates of personal income growth list by states that are in the bottom 20 states on personal income

keys = list(lowest_20_states_df['name'])

#sort lowest to highest in rates of growth
personal_income_growth_2017to2021Q2_lower_end=personal_income_growth_2017to2021Q2["DataValue"][keys].sort_values()


#plot growth in the 5 year timeframe in personal incomes for bottom 20 states in personal income
fig5 = px.bar(personal_income_growth_2017to2021Q2_lower_end, 
              labels = {'GeoName' : 'State', 'value': 'Percent Growth Personal Incomes 2017-2021Q2' },
              color_discrete_sequence = ['pink']*len(personal_income_growth_2017to2021Q2_lower_end), 
              width = 1000,
               )
fig5.update_layout(title_text = "Percent Growth in Personal Income 2017-2021Q2 for 20 States with lowest Personal Income", showlegend = False )

st.plotly_chart(fig5)


#create keys for the 8 states with highest personal income growth out of the bottom 20 states in personal income
states_filter_2_keys = list(personal_income_growth_2017to2021Q2_lower_end.iloc[-8:].index)
states_filter_keys_code = ['MS', 'KY','MT', 'IN', 'GA', 'LA','NM','UT']


st.header("Target States")
fig6 = go.Figure(data=go.Choropleth(
    locations=states_filter_keys_code, # Spatial coordinates
    z = personal_income_growth_2017to2021Q2["DataValue"][states_filter_2_keys].sort_values(), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'viridis' ,
    colorbar_title = "Percentage",
    autocolorscale=False,
    #text=us_states_df['text'], # hover text
    marker_line_color='white'# line markers between states
    
 ))

fig6.update_layout(
        geo_scope='usa', # limite map scope to USA,
        title_text = " Map of US with target states and their percent growth from 2017Q1 - 2021Q2",
         height = 800
         #margin={"r":0,"t":0,"l":0,"b":0}
         )

st.plotly_chart(fig6,use_container_width = True)

st.write("These are the top 8 states chosen by growth out of the lower income states to focus on ")

#read csv file from kaggle
population_by_state_df = pd.read_csv(Path('Resources/pop_2010_2020.csv'))

#filter csv file to target years, set index to the state
population_by_state = population_by_state_df[['GeoName',
                                             '2016','2017','2018','2019','2020']]
population_by_state = population_by_state.set_index('GeoName')

#Inserted GDP by state & industy csv file
gdp_country_state = pd.read_csv(Path('Resources/GDP_ALL_AREAS_1997_2020.csv'))

# filter by the target 8 states
gdp_country_state=gdp_country_state[gdp_country_state["GeoName"].isin(states_filter_2_keys)]


# extract list of industries
industry_list=gdp_country_state["Description"].drop_duplicates().sort_values()


#Filtered the data to only include GeoName, Description, Years
gdp_state_5year = gdp_country_state[[
    'GeoName',
    'Description',
    '2016','2017','2018','2019','2020']]

# Replacing NA's to 0
gdp_state_5year = gdp_state_5year.replace(["(NA)", "(L)"], 0)
gdp_state_5year=gdp_state_5year.fillna(0)

#changing strings to floats
gdp_state_5year['2016'] = gdp_state_5year['2016'].astype('float')
gdp_state_5year['2017'] = gdp_state_5year['2017'].astype('float')
gdp_state_5year['2019'] = gdp_state_5year['2019'].astype('float')
gdp_state_5year['2020'] = gdp_state_5year['2020'].astype('float')
#grouped by Description to pick out All industry total
gdp_state_5year_filter = gdp_state_5year.groupby('Description')

gdp_all_industry_df = gdp_state_5year_filter.get_group('All industry total')

gdp_all_industry_df = gdp_all_industry_df.set_index(['GeoName','Description'])

# calculate the per capita amount. multiply by a million, the units the original data was delivered in.
gdp_capita_industry = gdp_all_industry_df / population_by_state * 1000000

# reset index for next step
gdp_capita_industry = gdp_capita_industry.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_industry = gdp_capita_industry.melt(['GeoName','Description'], var_name='Date', value_name='Value')

#st.write(gdp_capita_industry.tail())

# extract industry label
industry_label=gdp_capita_industry["Description"][0]

# drop Description column and unstack
unstacked_gdp_capita_industry = gdp_capita_industry.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
industry_growth_rank = ((unstacked_gdp_capita_industry["Value"].loc["2020"]/unstacked_gdp_capita_industry["Value"].loc["2016"] - 1) * 100).sort_values()

# review percent growths ranked
#st.write(industry_growth_rank)

# renamed the Geoname column to the industry label so it can be used to display on the graphs
gdp_capita_industry=gdp_capita_industry.rename(columns={'GeoName': industry_label})

st.header("GDP Per Capita for all industry for target states - 2016 to 2020")
industry_plot = px.bar(gdp_capita_industry, 
                        x='Date',
                        y='Value',
                        facet_col = "All industry total",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
industry_plot.update_layout()
st.plotly_chart(industry_plot)


#plot the states by their percent growth in this industry group for the last five years, in increasing order

industry_plot_2 = px.bar(industry_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of {industry_label}"},
                          color_discrete_sequence = ['red']*len(industry_growth_rank),
                          width = 1200
                       )

industry_plot_2.update_layout(title_text = f"Percent Growth for last five years for {industry_label}",
                                showlegend = False)

st.plotly_chart(industry_plot_2)



gdp_agriculture_df = gdp_state_5year_filter.get_group("  Agriculture, forestry, fishing and hunting")

gdp_agriculture_df = gdp_agriculture_df.set_index(['GeoName','Description'])

gdp_capita_agriculture = gdp_agriculture_df / population_by_state * 1000000

gdp_capita_agriculture = gdp_capita_agriculture.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_agriculture = gdp_capita_agriculture.melt(['GeoName','Description'], var_name='Date', value_name='Value')

# st.write(gdp_capita_agriculture.tail())

st.header("GDP Per Capita for Agriculture for target states - 2016 to 2020")
# #visualizing states gdp per capita Agriculture
agriculture_plot = px.bar(gdp_capita_agriculture, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
agriculture_plot.update_layout()
st.plotly_chart(agriculture_plot)

# drop Description column and unstack
unstacked_gdp_capita_agriculture = gdp_capita_agriculture.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
agriculture_growth_rank = ((unstacked_gdp_capita_agriculture["Value"].loc["2020"]/unstacked_gdp_capita_agriculture["Value"].loc["2016"] - 1) * 100).sort_values()

agriculture_plot_2 = px.bar(agriculture_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of Agriculture"},
                          color_discrete_sequence = ['red']*len(agriculture_growth_rank),
                          width = 1200
                       )

agriculture_plot_2.update_layout(title_text = f"Percent Growth for last five years for Agriculture",
                                showlegend = False)

st.plotly_chart(agriculture_plot_2)


#filtering out Healthcare df
gdp_healthcare_df = gdp_state_5year_filter.get_group("   Health care and social assistance")

gdp_healthcare_df = gdp_healthcare_df.set_index(['GeoName','Description'])

gdp_capita_healthcare = gdp_healthcare_df / population_by_state* 1000000

gdp_capita_healthcare = gdp_capita_healthcare.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_healthcare = gdp_capita_healthcare.melt(['GeoName','Description'], var_name='Date', value_name='Value')

#st.write(gdp_capita_healthcare.tail())
st.header("GDP Per Capita for Healthcare for target states - 2016 to 2020")
healthcare_plot = px.bar(gdp_capita_healthcare, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
healthcare_plot.update_layout()
st.plotly_chart(healthcare_plot)

# drop Description column and unstack
unstacked_gdp_capita_healthcare = gdp_capita_healthcare.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
healthcare_growth_rank = ((unstacked_gdp_capita_healthcare["Value"].loc["2020"]/unstacked_gdp_capita_healthcare["Value"].loc["2016"] - 1) * 100).sort_values()

healthcare_plot_2 = px.bar(healthcare_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of Healthcare"},
                          color_discrete_sequence = ['red']*len(healthcare_growth_rank),
                          width = 1200
                       )

healthcare_plot_2.update_layout(title_text = f"Percent Growth for last five years for Healthcare",
                                showlegend = False)

st.plotly_chart(healthcare_plot_2)

#filtering a df out for manufacturing
gdp_manufacturing_df = gdp_state_5year_filter.get_group("  Manufacturing")

gdp_manufacturing_df = gdp_manufacturing_df.set_index(['GeoName','Description'])

gdp_capita_manufacturing = gdp_manufacturing_df / population_by_state* 1000000

gdp_capita_manufacturing = gdp_capita_manufacturing.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_manufacturing = gdp_capita_manufacturing.melt(['GeoName','Description'], var_name='Date', value_name='Value')

#st.write(gdp_capita_manufacturing.tail())

st.header("GDP Per Capita for Manufacturing for target states - 2016 to 2020")
manufacturing_plot = px.bar(gdp_capita_manufacturing, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
manufacturing_plot.update_layout()
st.plotly_chart(manufacturing_plot)

# drop Description column and unstack
unstacked_gdp_capita_manufacturing = gdp_capita_manufacturing.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
manufacturing_growth_rank = ((unstacked_gdp_capita_manufacturing["Value"].loc["2020"]/unstacked_gdp_capita_manufacturing["Value"].loc["2016"] - 1) * 100).sort_values()

manufacturing_plot_2 = px.bar(manufacturing_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of manufacturing"},
                          color_discrete_sequence = ['red']*len(manufacturing_growth_rank),
                          width = 1200
                       )

manufacturing_plot_2.update_layout(title_text = f"Percent Growth for last five years for manufacturing",
                                showlegend = False)

st.plotly_chart(manufacturing_plot_2)
#filtering df for private gdp by state
gdp_private_df = gdp_state_5year_filter.get_group(' Private industries')

gdp_private_df = gdp_private_df.set_index(['GeoName','Description'])

gdp_capita_private = gdp_private_df / population_by_state* 1000000


gdp_capita_private = gdp_capita_private.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_private = gdp_capita_private.melt(['GeoName','Description'], var_name='Date', value_name='Value')

# st.write(gdp_capita_private.tail())
st.header("GDP Per Capita for Private Sector for target states - 2016 to 2020")
private_plot = px.bar(gdp_capita_private, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
private_plot.update_layout()
st.plotly_chart(private_plot)
# drop Description column and unstack
unstacked_gdp_capita_private = gdp_capita_private.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
private_growth_rank = ((unstacked_gdp_capita_private["Value"].loc["2020"]/unstacked_gdp_capita_private["Value"].loc["2016"] - 1) * 100).sort_values()

private_plot_2 = px.bar(private_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of Private Sector"},
                          color_discrete_sequence = ['red']*len(private_growth_rank),
                          width = 1200
                       )

private_plot_2.update_layout(title_text = f"Percent Growth for last five years for Private Sector",
                                showlegend = False)

st.plotly_chart(private_plot_2)
#filteting out df for Finance gdp by state
gdp_finance_df = gdp_state_5year_filter.get_group('  Finance, insurance, real estate, rental, and leasing')

gdp_finance_df = gdp_finance_df.set_index(['GeoName','Description'])

gdp_capita_finance = gdp_finance_df / population_by_state* 1000000

gdp_capita_finance = gdp_capita_finance.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_finance = gdp_capita_finance.melt(['GeoName','Description'], var_name='Date', value_name='Value')

# st.write(gdp_capita_finance.tail())
st.header("GDP Per Capita for Finance for target states - 2016 to 2020")
finance_plot = px.bar(gdp_capita_finance, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
finance_plot.update_layout()
st.plotly_chart(finance_plot)

# drop Description column and unstack
unstacked_gdp_capita_finance = gdp_capita_finance.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
finance_growth_rank = ((unstacked_gdp_capita_finance["Value"].loc["2020"]/unstacked_gdp_capita_finance["Value"].loc["2016"] - 1) * 100).sort_values()

finance_plot_2 = px.bar(finance_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of finance"},
                          color_discrete_sequence = ['red']*len(finance_growth_rank),
                          width = 1200
                       )

finance_plot_2.update_layout(title_text = f"Percent Growth for last five years for finance",
                                showlegend = False)

st.plotly_chart(finance_plot_2)
#filtering df for transportation gdp by state
gdp_transportation_df = gdp_state_5year_filter.get_group('  Transportation and warehousing')

gdp_transportation_df = gdp_transportation_df.set_index(['GeoName','Description'])

gdp_capita_transportation = gdp_transportation_df / population_by_state* 1000000

gdp_capita_transportation = gdp_capita_transportation.reset_index()

#melting the df arounf GeoName and Description
gdp_capita_transportation = gdp_capita_transportation.melt(['GeoName','Description'], var_name='Date', value_name='Value')
# st.write(gdp_capita_transportation.tail())

st.header("GDP Per Capita for Transportation for target states - 2016 to 2020")
transportation_plot = px.bar(gdp_capita_transportation, 
                        x='Date',
                        y='Value',
                        facet_col = "GeoName",
                        facet_col_wrap = 4,
                        facet_row_spacing = 0.1,
                        width = 1200,
                        height = 500,
                        labels = {'Date':"Fiscal Year", 'Value':'GDP per Capita'})
transportation_plot.update_layout()
st.plotly_chart(transportation_plot)

# drop Description column and unstack
unstacked_gdp_capita_transportation = gdp_capita_transportation.drop(columns=["Description"]).set_index(['GeoName', 'Date']).unstack(level=0)


# find percent growths
transportation_growth_rank = ((unstacked_gdp_capita_transportation["Value"].loc["2020"]/unstacked_gdp_capita_transportation["Value"].loc["2016"] - 1) * 100).sort_values()

transportation_plot_2 = px.bar(transportation_growth_rank,
                          labels = { 'GeoName': 'State', 'value': f"% growth of transportation"},
                          color_discrete_sequence = ['red']*len(transportation_growth_rank),
                          width = 1200
                       )

transportation_plot_2.update_layout(title_text = f"Percent Growth for last five years for transportation",
                                showlegend = False)

st.plotly_chart(transportation_plot_2)
#st.write(industry_list)

industry = st.selectbox("Choose a Industry to analyze:", gdp_country_state["Description"].drop_duplicates().sort_values())


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


st.header(" Industry Distribution by GDP in Target states")
listoflists = []
#listoflists.append(unstacked_gdp_capita_industry["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_agriculture["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_healthcare["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_manufacturing["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_private["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_finance["Value"].loc["2019"])
listoflists.append(unstacked_gdp_capita_transportation["Value"].loc["2019"])

pie_chart_data = pd.DataFrame(listoflists, 
                               columns = ['Georgia', 'Indiana', 'Kentucky', 'Louisiana', 'Mississippi', 'Montana', 'New Mexico', 'Utah'])
pie_chart_data['Industry'] = ['Agriculture', 'Healthcare', 'Manufacturing', 'Private Industries', 'Finance', 'Transportation']
pie_chart_data.set_index('Industry')

pie_fig1 = px.pie(pie_chart_data, values = 'Georgia', names = 'Industry', title = 'Geogia')
st.plotly_chart(pie_fig1,use_container_width = True)

pie_fig2 = px.pie(pie_chart_data, values = 'Indiana', names = 'Industry', title = 'Indiana')
st.plotly_chart(pie_fig2,use_container_width = True)

pie_fig3 = px.pie(pie_chart_data, values = 'Kentucky', names = 'Industry', title = ' Kentucky')
st.plotly_chart(pie_fig3,use_container_width = True)

pie_fig4 = px.pie(pie_chart_data, values = 'Louisiana', names = 'Industry', title = 'Louisiana')
st.plotly_chart(pie_fig4,use_container_width = True)

pie_fig5 = px.pie(pie_chart_data, values = 'Mississippi', names = 'Industry', title = ' Mississippi')
st.plotly_chart(pie_fig5,use_container_width = True)

pie_fig6 = px.pie(pie_chart_data, values = 'Montana', names = 'Industry', title = ' Montana')
st.plotly_chart(pie_fig6,use_container_width = True)

pie_fig7 = px.pie(pie_chart_data, values = 'New Mexico', names = 'Industry', title = 'New Mexico')
st.plotly_chart(pie_fig7,use_container_width = True)

pie_fig8 = px.pie(pie_chart_data, values = 'Utah', names = 'Industry', title = 'Utah')
st.plotly_chart(pie_fig8,use_container_width = True)

# specs = specs=[[{'type':'domain'}, {'type':'domain'}]]
# pie_fig = make_subplots(rows=1, cols=2, specs=specs)

# # Define pie charts
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Georgia'], name='Georgia'),1, 1)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Indiana'], name='Indiana'),1, 2)

# # Tune layout and hover info
# pie_fig.update_traces(hoverinfo='label+percent+name', textinfo='none')
# pie_fig.update_layout(title_text='Industry Distribution by GDP in Target States'
#            )

# pie_fig = go.Figure(pie_fig)
# st.plotly_chart(pie_fig,use_container_width = True)

# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Kentucky'], name='Kentucky',domain=dict(x=[0.5,0.75], y= [0,0.5])),1, 3)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Louisiana'], name='Louisiana',domain=dict(x=[0.75,1], y= [0.5,1])),1, 4)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Mississippi'], name='Mississippi',domain=dict(x=[0,0.25], y= [0,0.5])),2, 1)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Montana'], name='Monatana',domain=dict(x=[0.25,0.5], y= [0.5,1])),2, 2)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['New Mexico'], name='New Mexico',domain=dict(x=[0.5,0.75], y= [0,0.5])),2, 3)
# pie_fig.add_trace(go.Pie(labels=pie_chart_data['Industry'], values=pie_chart_data['Utah'], name='Utah',domain=dict(x=[0.75,1], y= [0.5,1])),2, 4)
