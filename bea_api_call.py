#import required libraries

from datetime import date
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


st.title("Identifying Emerging markets in the US")

#load the API keys stored in .env file
load_dotenv()

# https://apps.bea.gov/api/signup/index.cfm to signup for API key for Bureau of Economic Analysis

# https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf for user guide

#get BEA API key from .env file
bea_api_key=os.getenv("BEA_API_KEY")

# set up query URL
bea_url = "http://apps.bea.gov/api/data?UserID=" + bea_api_key + "&method=GETDATASETLIST&ResultFormat=JSON" 

#send request to BEA
bea_response = requests.get(bea_url).json()["BEAAPI"]["Results"]

# #review response
# bea_response

# this query will get the data for all states for the last five years for personal income per capita.

bea_states_personal_income_linecode_query_url = "http://apps.bea.gov/api/data?UserID=" + bea_api_key + "&method=GetData&datasetname=Regional&TableName=SQINC1&GeoFIPS=STATE&LineCode=3&Year=LAST5&ResultFormat=JSON"

#query for last five years personal income by state.
personal_income_by_state_5year = pd.DataFrame(requests.get(bea_states_personal_income_linecode_query_url).json()["BEAAPI"]["Results"]["Data"])


#review the results of the query
# st.write(" First 5 rows of the data obtained by querying for last five years personal income by state ")
# st.write(personal_income_by_state_5year.head())


# clip out the unnecessary columns
personal_income_by_state_5year=personal_income_by_state_5year[["GeoName", "TimePeriod", "DataValue"]]
# st.write(" Data with only the necessary columns of data")
# st.write(personal_income_by_state_5year.head())

# Used str.replace() to remove the ',' from the Income datavalue and convert to float from string

personal_income_by_state_5year['DataValue'] = personal_income_by_state_5year['DataValue'].str.replace(',', '').astype('float')
# st.write(" Data after convertng the Data Value col to float from String object")
# st.write(personal_income_by_state_5year.head())


# Filter the dataframe to get just the states

list_of_states = [ 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
                  'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
                  'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 
                   'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
                   'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
                  'Wisconsin', 'Wyoming']

personal_income_state_filter = personal_income_by_state_5year['GeoName'].isin(list_of_states)
personal_income_filter_by_state = personal_income_by_state_5year[personal_income_state_filter]
# st.write(" Data after filtering out just the states from the original DataFrame")
# st.write(personal_income_filter_by_state.head())



# Setting the time period to be the index and converting the datatype from string to dateTime
personal_income_filter_by_state_2 = personal_income_filter_by_state
personal_income_filter_by_state['TimePeriod'] = pd.to_datetime(personal_income_filter_by_state['TimePeriod']).dt.date
personal_income_filter_by_state = personal_income_filter_by_state.set_index('TimePeriod')
# personal_income_filter_by_state.index = pd.to_datetime(personal_income_filter_by_state.index)

# check resulting dataframe
# st.write(" Data after convertng the TimePeriod col to DateTime format")
# st.write(personal_income_filter_by_state.head())

# Group the data by state and calculate the average personal income for every year from 2017 to current year

personal_income_filter_annual = personal_income_filter_by_state.groupby('GeoName').resample('A').mean()
# st.write(" Data after annualising and grouping by states")
# st.write(personal_income_filter_annual)


# Bar chart for states with an interactive slider
time = st.selectbox("Time Period:", personal_income_filter_by_state.index.unique())
st.write("Time Period Selected is:", time)
fig = px.bar(personal_income_filter_by_state.loc[time].sort_values('DataValue'), x = 'GeoName', y = 'DataValue' , width = 1500)
st.plotly_chart(fig)

personal_income_filter_annual.sort_values('DataValue').hvplot.bar(groupby = 'TimePeriod', x = 'GeoName', rot = 90)

#Plots for data pivoted by states

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

layout_plots_line = px.line(personal_income_melt, 
                        x='TimePeriod',
                        y='value',
                        color = 'GeoName',
                        width = 1000)
                     
                        
st.plotly_chart(layout_plots_line)

#Sort the States by Personal Income
personal_income_sorted = personal_income_filter_by_state_2.sort_values(by = 'DataValue')

#Pivoting the table around Geoname and Timeperiod
personal_income_melt_2 = personal_income_sorted.melt(id_vars = ['GeoName', 'TimePeriod'])

#st.write(personal_income_melt_2)
# # Plots with x_value = states
# layout_plots_2 = personal_income_melt_2.hvplot.bar(
#     x='GeoName',
#     y='value',
#     by='variable',
#     width=400,
#     height=200,
#     stacked=True,
#     groupby='TimePeriod',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout().cols(3)

# layout_plots_2

# layout_plots_2 = px.bar(personal_income_melt_2, 
#                         x='GeoName',
#                         y='value',
#                         #color = 'TimePeriod',
#                         facet_col = "TimePeriod",
#                         facet_col_wrap = 4,
#                         facet_row_spacing = 0.03,
#                         width = 1500,
#                         height = 2400)

#st.plotly_chart(layout_plots_2)

# layout_plots_line_2 = px.bar(personal_income_melt_2, 
#                         x='GeoName',
#                         y='value',
#                         color = 'TimePeriod',
#                         width = 1000)
                     
                        
# st.plotly_chart(layout_plots_line_2)
# Dataframe grouped by state and extracted the last element from each group which is the personal income value for 2021Q4

personal_income_2021Q4 = personal_income_sorted.groupby('GeoName').last()
#personal_income_2021Q4

# loading US states boundary data which is available in bokeh as a part of bokeh.sampledata.us_states
us_states_df = pd.DataFrame(us_states).T


# reset index for merging
personal_income_2021Q4 = personal_income_2021Q4.reset_index()
#personal_income_2021Q4

# deleting states of Alaska, Hawaii and District of Columbia
us_states_df = us_states_df[~us_states_df["name"].isin(['Alaska', "Hawaii", "District of Columbia"])]

# us_states_df["lons"] = us_states_df.lons.values.tolist()
# us_states_df["lats"] = us_states_df.lats.values.tolist()
#us_states_df = us_states_df.reset_index() # Needed initially, not after the index is already reset
#personal_income_2021Q4 = personal_income_2021Q4.reset_index()

# Merge the two dataframes
us_states_df = us_states_df.merge(personal_income_2021Q4[["GeoName", "DataValue"]], how="left", left_on="name", right_on="GeoName")
us_states_df = us_states_df.sort_values('GeoName')
us_states_df['code'] = ['AL','AZ','AR','CA','CO','CT','DE','FL','GA','ID',
                        'IL','IN','IA','KS','KY','LA','ME','MD','MA','MI',
                        'MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY',
                        'NC','ND','OH','OK','OR','PA','RI','SC','SD','TN',
                        'TX','UT','VT','VA','WA','WV','WI','WY']

# st.write(us_states_df)
#result_merge = pd.concat([us_states_df,personal_income_2021Q4], axis = 1 )

# us_states_datasource = {}
# us_states_datasource["lons"] = us_states_df.lons.values.tolist()
# us_states_datasource["lats"] = us_states_df.lats.values.tolist()
# us_states_datasource["name"] = us_states_df.name.values.tolist()
# us_states_datasource["StateCodes"] = us_states_df.index.values.tolist()
# us_states_datasource["DataValue"] = us_states_df.DataValue.values.tolist()


# Creating the plot
# fig = px.choropleth(locations=us_states_datasource['name'], locationmode="USA-states",
#                      color=us_states_datasource['DataValue'], scope="usa")
# st.write(fig)

# st.write(type(us_states_datasource['DataValue']))
import plotly.graph_objects as go

fig1 = go.Figure(data=go.Choropleth(
    locations=us_states_df['code'], # Spatial coordinates
    z = (us_states_df['DataValue']/max(us_states_df['DataValue'])), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'solar',
    colorbar_title = "USD",
))

fig1.update_layout(
        geo_scope='usa', # limite map scope to USA
)

st.write(fig1)
# fig = figure(plot_width=900, plot_height=500,
#              title="Personal Income by state for 2020Q4",
#              x_axis_location=None, y_axis_location=None,
#              tooltips=[
#                         ("State", "@name"), ("DataValue", "@DataValue"), ("(Long, Lat)", "($x, $y)")
#                       ]
#             )
# #fig.grid.grid_line_color = None

# fig.patches("lons", "lats", source=us_states_datasource,
#             fill_color={'field': 'DataValue'},     # 'transform': LogColorMapper(palette=oranges[::-1])
#             fill_alpha=0.7, line_color="white", line_width=0.5)

# st.write(fig)


# # #begin process to filter states to focus analysis on. filter bottom 20 by personal income in 2020Q4.
# # lowest_20_states_df = us_states_df.nsmallest(20, "DataValue")

# # # show results - bottom 20 states by personal income
# # display(lowest_20_states_df[['name', 'DataValue']])

# # # unstack dataframe 
# # personal_income_filter_by_state = personal_income_filter_by_state.reset_index()
# # unstacked_personal_income_by_state = personal_income_filter_by_state.set_index(['GeoName', 'TimePeriod']).unstack(level=0)


# # # review unstacked dataframe
# # display(unstacked_personal_income_by_state)


# # # make new dataframe with the increase in personal income per state for this time period

# # personal_income_growth_2017to2021Q1 = ((unstacked_personal_income_by_state.transpose()["2021-04-01"] / unstacked_personal_income_by_state.transpose()["2017-01-01"]) - 1) * 100
# # personal_income_growth_2017to2021Q1


# # chart of all states rate of growth from 2017 to 2021Q1
# #personal_income_growth_2017to2021Q1.hvplot(kind="bar", title="Percent growth personal income 2017 to 2021Q1", xlabel="State", ylabel="Percent Personal Income Growth").opts(xrotation=90)

# # filter the rates of personal income growth list by states that are in the bottom 20 states on personal income

# # keys = list(lowest_20_states_df['name'])
# # i1 = df1.set_index(keys).index
# # rpt[rpt['STK_ID'].isin(stk_list)]
# #personal_income_growth_2017to2021Q1_lower_end=personal_income_growth_2017to2021Q1[personal_income_growth_2017to2021Q1["GeoName"].isin(list(lowest_20_states_df['name']))]

# #Inserted GDP by state & industy csv file
# gdp_country_state = pd.read_csv(Path('Resources/GDP2N__ALL_AREAS_1997_2020.csv'))


# #Filtered the data to only include GeoName, Description, Years
# gdp_state_10year = gdp_country_state[[
#     'GeoName',
#     'Description',
#     '2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']]

# #dropped NAN values
# gdp_state_10year.set_index('GeoName').dropna().head()


# #grouped by Description to pick out All industry total
# gdp_state_10year_filter = gdp_state_10year.groupby('Description')

# gdp_all_industry_df = gdp_state_10year_filter.get_group('All industry total')

# gdp_all_industry_df.head()


# #melting the df arounf GeoName and Description
# gdp_all_industry = gdp_all_industry_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #changing all values to integers
# gdp_all_industry["Value"] = pd.to_numeric(gdp_all_industry["Value"], downcast="integer")

# gdp_all_industry.tail()

# #Plotting visual
# gdp_all_industry.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()

# #Creating a df for agriculture gdp in all states
# gdp_agriculture_df = gdp_state_10year_filter.get_group("  Agriculture, forestry, fishing and hunting")

# #Melting df around GeoName and Description
# gdp_agriculture= gdp_agriculture_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #changing values to intergers
# gdp_agriculture['Value'] = pd.to_numeric(gdp_agriculture["Value"], downcast="integer")

# gdp_agriculture.tail()

# #visualizing states ag gdp
# gdp_agriculture.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()

# #filtering out Healthcare df
# gdp_healthcare_df = gdp_state_10year_filter.get_group("   Health care and social assistance")

# #melting df around GeoName and Description
# gdp_healthcare = gdp_healthcare_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #Turning values into integers
# gdp_healthcare['Value'] = pd.to_numeric(gdp_healthcare["Value"], downcast="integer")

# gdp_healthcare.tail()


# #visualizing healthcare gdp by state
# gdp_healthcare.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()


# #filtering a df out for manufacturing
# gdp_manufacturing_df = gdp_state_10year_filter.get_group("  Manufacturing")

# #melting df around GeoName and Description
# gdp_manufacturing= gdp_manufacturing_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #changing values to integers
# gdp_manufacturing['Value'] = pd.to_numeric(gdp_manufacturing["Value"], downcast="integer")

# gdp_manufacturing.tail()


# #visualizing manufactuing gdp by state
# gdp_manufacturing.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()


# #filtering df for private gdp by state
# gdp_private_df = gdp_state_10year_filter.get_group(' Private industries')


# #melting df around GeoName and Description
# gdp_private= gdp_private_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #turning values to integers
# gdp_private['Value'] = pd.to_numeric(gdp_private["Value"], downcast="integer")

# gdp_private.tail()

# #visualizing private sector gdp by state
# gdp_private.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()

# #filteting out df for Real Estate gdp by state
# gdp_real_estate_df = gdp_state_10year_filter.get_group('    Real estate')

# #melting df around GeoName and Description
# gdp_real_estate = gdp_real_estate_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #changing values to integers
# gdp_real_estate['Value'] = pd.to_numeric(gdp_real_estate["Value"], downcast="integer")

# gdp_real_estate.tail()



# #visualizing real estate gdp by state
# gdp_real_estate.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()

# #filtering df for transportation gdp by state
# gdp_transportation_df = gdp_state_10year_filter.get_group('  Transportation and warehousing')

# #melting df around GeoName and Description
# gdp_transportation = gdp_transportation_df.melt(['GeoName', 'Description'], var_name='Date', value_name='Value').set_index('GeoName')

# #changing values to integers
# gdp_transportation['Value'] = pd.to_numeric(gdp_transportation["Value"], downcast="integer")

# gdp_transportation.tail()



# #visualizing transportation gdp by state
# gdp_transportation.hvplot.bar(
#     x='Date',
#     y='Value',
#     by='Description',
#     width=300,
#     height=150,
#     stacked=True,
#     groupby='GeoName',
#     legend=False,
#     xlabel='',
#     bar_width=1.0,
#     rot = 90
# ).layout()







