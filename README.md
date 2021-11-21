# Identifying Emerging Markets in United Staes

## Project Proposal: Inner Emerging Economies Analysis

This project is proposed to use financial technology analysis tools to find investment opportunities for emerging markets within the United States.
We are defining Emerging Markets to refer to US states which have lower than average GDP per capita, but high rates of GDP growth in recent years.
The first step of the analysis will attempt to narrow down a shorter list of US states to focus the analysis on, and will use a combination of data about GDP per capita, GDP growth, and cost of living. The next step will be to analyze some sectors of these states to find which have been growing in recent years and have a good potential for continued growth.
Some of the data sources we have identified include BEA.gov and kaggle.com but more may be included. Some sectors we are interested in analyzing include tech, healthcare, finance, agriculture, manufacturing, transportation. The sectors that appear to have higher rates of recent growth in the states targetted for analysis will be highlighted.
We will also explore a few secondary economic metrics. Some of the group's ideas include infrastructure, pension outlays, and happiness surveys. The ones which appear to be useful analytically we will include in the final presentation.
The data is intended to be used to help investors identify markets to start companies in or expand existing operations into. The end result will be a presentation where investors can look at this data in an easy to use visual format.


---
## Implementation: The Emerging Economy App


We conceived this project in order to facilitate decisions involving investment in Emerging Markets within the United States.
The idea of this Emerging Markets analysis is to encourage investment in US states with lower average incomes. Out of those states, we used data to find a smaller target group of lower income states that have the highest growth rates in recent years. We created the app using streamlit

    The application can be used to easily view bar charts and rankings of growth in the last five years of growth of any industry for these target states.

    Investors planning on starting businesses or expanding branches of existing businesses will be able to use this to identify opportunities in industries they are focused on.
    
    Whether you are looking for the emerging state with the highest growth rate in a sector, or looking for potentials in sectors that took a hit in 2020 but are likely to rebound, you will be able to quickly visualize the change in recent years.

---
## Data Sources:

We used the United Staes Bureau of Economic Analysis API to get the last 5 year data of Personal Income in all the states. 

* [Bea.gov]( https://apps.bea.gov/API/signup/index.cfm) - Bureau of Economic Analysis

Furthermore, the population data to calculate the per capita growth in the states was obtained by donwloading a .csv file from the United States Cencus Bureau at:
* [Census.gov](https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/state/totals/) - United Staes Census Bureau

Lastly, the GDP for each industry in all the states in the US was obtained by downloading a .csv file from Kaggle.com:
* [Kaggle.com](https://www.kaggle.com/davidbroberts/us-gdp-by-state-19972020/version/1) - A huge repository of community published data & code.

---
## Applications and Hypotheses:

* Test a hypothesis:
    Is there a similar ranking within these states of overall growth and manufacturing growth?

* Answer questions:<br>
    Which industries in these states seem to have taken bigger hits from 2020 with recovery opportunity, which seemed more resilient?<br>
    Hypotheses related to this question:<br>
        - Jobs with more work from home opportunity would have not taken as much of a hit<br>
	    - Jobs involving travel, retail, restaurants, would have taken more of a hit<br>
	    - Delivery services would have increased<br>

* Identify markets with good investment opportunities:<br>
		- State with highest growth in an industry the investor is involved in<br>
        - State that took the biggest hit in 2020 in an industry, but is expected to recover<br>
        - Is there a similar ranking within these states of overall growth and manufacturing growth?<br>
        - Which industries in these states seem to have taken bigger hits from 2020, which seemed more resilient.

---

## Analysis:

## An overview of our Streamlit Dashboard

Annual Personal Income for all the states ranked in ascending order. The selectbox lets you select a year, to view the personal incomes for the states for that fiscal year. The red line on the map divides the map into two parts, the left of which identifies the 20 poorer states where we want to focus<br>
<br>
![Annual Personal Income](images/streamlit_1.png)<br>
<br>
A general overview of the trends for Personal Income for all states for the past five year period. There are obvious bumps from the rounds of stimulus checks but there is still an upward general trend.<br>

![Personal Income for all states](images/streamlit_2.png)<br>


A choropleth map of the United states, color coded using the personal income data from 2021 Q2. The darker color represent the states with lower personal income<br>

![US map with personal income from 2021 Q2](images/streamlit_3.png)<br>

Percent Growth for all the states from 2017Q1 to 2021Q2 ranked in ascending order<br>

![Percent Growth](images/streamlit_4.png)<br>

Personal Income plotted with percent growth for all the states. It shows an interesting trend. One of our hypotheses was that states with high personal income will have a higher growth percentage and vice versa. Overall, we expected the line plot of percent growth to be linear with a couple of anomalies. But we see there are some high income states like New Hampshire and Connecticut which show a very low rate of growth. Similarly there are some low income states like New Mexico and Utah which show an unprecedented growth rate. <br> 
![Personal Income with Growth Rate](images/streamlit_5.png)<br>


The following graph shows the singled out 20 of the lowest ranking States in personal income, then ranked based on the rate of growth of personal incomes in each one for the past five-year period<br>

![20 Low Income States](images/streamlit_6.png)<br>

Chrolopleth Map of the targeted eight states with the highest rate of growth in personal incomes for the five year time period. The target states are:

* Georgia
* Indiana
* Kentucky
* Louisiana
* Mississippi
* Montana
* New Mexico
* Utah<br>

![Choropleth map of targeted states](images/streamlit_7.png)<br>

Following shows rankings of growth in the target states in the last five years in all the insustries, using bar charts. We see Utah has the highest growth percentage in the last 5 years. Based on our analysis, we can identify Utah as one or the more profitable state to invest in. <br>

![Analysis of all Industries](images/streamlit_8.png)<br>

We identified 6 fast growing sectors to test our hypotheses and identify states for investments in that sector. The sectors we analyzed are:
* Agriculture
* Healthcare
* Manufacturing
* Private Sector
* Finance
* Transportation<br>

![Sector Analysis](images/streamlit_9.png)<br>

We added another selectbox, where the user can select any industry they want, and can get a gdp per capita analysis of that sector for the last five years in the target state, alongwith the growth rank of the target states for that sector based on the percent growth for the five year period. Our data set had missing values for some sectors for the year 2020, so the program was modified to filter out year 2020 if no data was available, to  avoid the resulting skew. <br>

![User defined Sector Analysis](images/streamlit_10.png)<br>

One of our Hypotheses was that it is the manufacturing industry that drive the overall growth of a state. We can see from the following bar charts, that the overall growth percentage rankof a state is quite different from the manufacturing growth rate rank. <br>

![Hypotheses testing](images/streamlit_11.png)<br>

The other Hypotheses that we tested was that:<br>
    -Jobs with more work from home opportunity would have not taken as much of a hit in 2020<br>
    -Jobs like transportation would have taken a bigger hit.<br>

This Hypothese tested out to be true as is visible in the following image:<br>

![Hypotheses testing2](images/streamlit_12.png) <br>

---
## Future Additions / Next Steps
* Updating the program to work for new data as it comes out
* Finding a list of stocks associated with a particular sector and include in our analysis
* Use some more parameters to filter the data and identify target states
* Allow the user to set some parameters in the beginning
* Analyze some non financial metrics like happiness for the target states
* Include some Pie graphs to identify the percentage pie of various sectors in each state

---
## Technologies

This project uses python 3.7 along with the following packages:

* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) - Web based user interface for data analysis.

* [pandas](https://github.com/pandas-dev/pandas) - Data analysis and manipulation library.

* [streamlit](https://streamlit.io/) - The fastest way to build and share data apps

* [plotly](https://plotly.com/) -  Developing standardds for AI and data science apps
---

## Installation Guide

Please install the following before starting the application

```python
  pip install pandas
  pip install plotly
  pip install streamlit
  pip install hvplot

```

Confirm installation by running:
```python
  conda list plotly
  conda list streamlit
```
---

## Usage
To use the inner_emerging_markets_analyzer tool, please download the folder in VS code and run it from command line using the following command

```python
streamlit run app.py
```

---

## Contributors

Preston Hodsman (hodsman@yahoo.com)
Thomas Leahy (thomasleahy6@gmail.com)
Abhishika Fatehpuria (abhishika@gmail.com)


---

## License

MIT
