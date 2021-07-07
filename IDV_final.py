# importing all the necesarry libraries

import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# reading csv file into dataframe

df = pd.read_csv('D:/study/Masters/sem-2/IDV/assignments/mini_project/datasets/owid-covid-data_new.csv')

for col in df.columns:
    df[col] = df[col].astype(str)
    
    
#creating a new dataframe with required dimensions

df1 = df[['iso_code','continent','location','date','new_deaths','new_cases','new_tests','hospital_beds_per_thousand']].copy()

# Printing the datatypes of the dimensions extracted from the dataset file before pre-processing

print(df1.dtypes)

# Dataset shape: Number of rows extracted from the dataset file before pre-processing

print(df1.shape)


# Data pre-processing: Cleaning up the data to remove null values/junk values in dataset

df1.loc[df.new_tests=='nan','new_tests'] = '0'
df1.loc[df.new_cases=='nan','new_cases'] = '0'
df1.loc[df.new_deaths=='nan','new_deaths'] = '0'
df1.loc[df.hospital_beds_per_thousand=='nan','hospital_beds_per_thousand'] = '0'
df1 = df1[df1.iso_code != 'nan']
df1 = df1[df1.continent != 'nan']


# Showing that there are no null/junk values

df1.apply(lambda x:sum(x.isnull()),axis=0)


# Calculating the month for each row in the dataset

month_no = ['01','02','03','04','05','06','07','08','09','10','11','12']
month_name = ['January','February','March','April','May','June','July','August','September','October','November',
              'December']
month = []
month_number = []
for ele in df1['date']:
    ele1 = ele[5]+ele[6]
    for i in range(12):
        if(ele1 == month_no[i]):
            month.append(month_name[i])
            month_number.append(int(month_no[i]))

            
# Adding the month name and month number as new columns to the dataframe

df1['month_n'] = month
df1['month_num'] = month_number


# Eliminating December month from our scope. Considering data from Jan, 2020.

df1 = df1[df1.month_num != 12]

# Converting deaths and cases into integer

df1['new_tests'] = df1['new_tests'].astype('str')
df1['new_deaths'] = df1['new_deaths'].astype('float64')
df1['new_deaths'] = df1['new_deaths'].astype('int')

df1['new_cases'] = df1['new_cases'].astype('float64')
df1['new_cases'] = df1['new_cases'].astype('int')

df1['new_tests'] = df1['new_tests'].astype('float64')
df1['new_tests'] = df1['new_tests'].astype('int')

df1['hospital_beds_per_thousand'] = df1['hospital_beds_per_thousand'].astype('float64')


# Group by based on continent, country and month. Aggregating new deaths, new cases,new tests and hospital beds.

df1 = df1.groupby(['iso_code','continent','location','month_n','month_num']).agg({'new_deaths':'sum','new_cases':'sum','new_tests':'sum','hospital_beds_per_thousand':'sum'})
df1.reset_index(inplace = True)


# Adding rows for months not present in the original dataset.
# For example: If Germany doesnt have any data for Jan month, we add a row with values 0. This is needed for
# cumilation purpose 

for iso in df1['iso_code'].unique():
    for i in range(1,7):
        val = ((df1['iso_code'].str.contains(iso)) & (df1['month_num'] == i)).any()
        if not val:
            df_temp = pd.DataFrame({"iso_code":[iso],"continent":[''],"location":[''],"date":[''],"new_deaths":[0],
                                    "new_cases":[0],"new_tests":[0],"hospital_beds_per_thousand":[0.0],"month_n":[''],
                                    "month_num":[i]})
            
            df1 = df1.append(df_temp,ignore_index = True)     
            
            
# Adding three new columns into DF1 for holdin cumilative data of deaths, cases and tests.
 

df1['cumil_deaths'] = ''
df1['cumil_cases'] = ''
df1['cumil_tests'] = ''
sum_deaths = 0

# Cumilative code for new_deaths

for item in df1['iso_code'].unique():
    sum_deaths = 0
    for i in range(1,7):
        val_deaths = df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'new_deaths'].iloc[0]
        sum_deaths = sum_deaths + val_deaths
        df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'cumil_deaths'] = sum_deaths

# Cumilative code for new_cases
        
for item in df1['iso_code'].unique():
    sum_cases = 0
    for i in range(1,7):
        val_cases = df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'new_cases'].iloc[0]
        sum_cases = sum_cases + val_cases
        df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'cumil_cases'] = sum_cases

# Cumilative code for new_tests

for item in df1['iso_code'].unique():
    sum_tests = 0
    for i in range(1,7):
        val_tests = df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'new_tests'].iloc[0]
        sum_tests = sum_tests + val_tests
        df1.loc[((df1['month_num'] == i) & (df1['iso_code'].str.contains(item))),'cumil_tests'] = sum_tests
        
        
# Changing datatypes of cumilated tests, deaths and cases before plotting 

df1['cumil_tests'] = df1['cumil_tests'].astype('int')
df1['cumil_deaths'] = df1['cumil_deaths'].astype('int')
df1['cumil_cases'] = df1['cumil_cases'].astype('int')


#Dataset Shape after pre-processing

print(df1.dtypes)

#Dataset for LineGraph
dff2 = df1.copy()
dff2 = dff2[dff2["month_num"] == 6]
#display(dff2)
dff3 = dff2[['iso_code','location','month_num','cumil_deaths','cumil_cases','cumil_tests']].copy()
#display(dff3)


# Dash starts here. 
# Code deals with the HTML part to create the front end of the dash.
app = dash.Dash(__name__)

# Header of the web page

app.layout = html.Div([
    html.H1("COVID-19 Data Visualization", style = {'text-align':'center'}),
    
# Adding slider(months), two dropdowns(interest, scope) and a radiobutton(cumilated and non-cumilated)
# on the frontend screen.
    
    dcc.Slider(id = "slct_slide",
               min = 1,
               max = 6,
               value = 4,
               marks = {
                   1: {'label': 'Jan'},
                   2: {'label': 'Feb'},
                   3: {'label': 'Mar'},
                   4: {'label': 'Apr'},
                   5: {'label': 'May'},
                   6: {'label': 'Jun'}},
               step = None
              ),
    html.Div([
        dcc.Dropdown(id = "slct_tab",
                     options = [
                         {"label":"Deaths","value":"deaths"}, #value has to be column name
                         {"label":"Cases","value":"affected_cases"},
                         {"label":"Tests","value":"tests"}],

                     multi = False,
                     value = "deaths",
                     optionHeight=25,
                     searchable=True,
                     clearable=True,
                     style = {'width':"80%", 'margin-top': '25px'}
                    )],style={"margin-left": '1000px'}),
    html.Div([     
        dcc.Dropdown(id="slct_scope",
                       options=[{"label":"World","value":"world"},
                               {"label":"Europe","value":"europe"}],
                       value="world",
                       multi = False,
                       optionHeight=25,
                       searchable=True,
                       clearable=True,
                       style = {'width':"40%", 'margin-top': '5px'})],style={"margin-right": '10px'}),
    html.Div([
        dcc.RadioItems(id="slct_cumil",
                      options=[{'label': 'Cummulative Data', 'value': 'cumil'},
                               {'label': 'NonCummulative Data', 'value': 'non_cumil'}],
                      value='non_cumil')], style={"width": '40%','margin-top': '25px'}),
  
    html.Div(id = "output_container",children = []),
    html.Br(),
    dcc.Graph(id = 'my_covid',figure = {}),
    html.Br(),
    dcc.Graph(id='line_graph', figure={})
])

# Callback to bridge the front and the back end

@app.callback(
    [Output(component_id = 'output_container', component_property = 'children'),
     Output(component_id = 'my_covid', component_property = 'figure'),
     Output(component_id = 'line_graph', component_property = 'figure')],
    [Input(component_id = 'slct_slide', component_property = 'value'),
     Input(component_id = 'slct_tab', component_property = 'value'),
     Input(component_id = 'slct_scope', component_property = 'value'),
     Input(component_id = 'slct_cumil', component_property = 'value')]
)

# Backend code. Creating the various maps.

def update_graph(option_slctd, data_slctd,scope_slctd,cumil_slctd):
    print(option_slctd)
    print(data_slctd)
    print(scope_slctd)
    print(cumil_slctd)
    #cumil_slctd=False
    dff1 = df1.copy()
    dff1 = dff1[dff1["month_num"] == option_slctd]
    container = "The data chosen by user is {0} and the geographical scope is {1}".format(data_slctd,scope_slctd)
    
    if(cumil_slctd == 'non_cumil'):
        
        
    
        if data_slctd == "deaths":
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "new_deaths",
            hover_data=['location', 'new_deaths','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
            
        elif data_slctd == "affected_cases":
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "new_cases",
            hover_data=['location', 'new_cases','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
            
        else: 
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "new_tests",
            hover_data=['location', 'new_tests','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
            
            
    
    else: 

    
        if data_slctd == "deaths":
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "cumil_deaths",
            hover_data=['location', 'cumil_deaths','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
            
        elif data_slctd == "affected_cases":
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "cumil_cases",
            hover_data=['location', 'cumil_cases','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
            
        else: 
            fig = px.choropleth(
            data_frame= dff1,
            locationmode='ISO-3',
            locations='iso_code',
            scope=scope_slctd,
            color= "cumil_tests",
            hover_data=['location', 'cumil_tests','hospital_beds_per_thousand'],
            color_continuous_scale=px.colors.diverging.Geyser)
    
    
    #LineGraph
    if data_slctd == "deaths":
        img = px.line(dff3, x=dff3['location'], y=dff3['cumil_deaths'], title='Line Graph for Total Deaths')
        #img.show()
    elif data_slctd == "affected_cases":
        img = px.line(dff3, x=dff3['location'], y=dff3['cumil_cases'], title='Line Graph for Total Affected Cases')
    else:
        img = px.line(dff3, x=dff3['location'], y=dff3['cumil_tests'], title='Line Graph for Total Tests')

    return container,fig,img

if __name__ == '__main__':
    app.run_server(port = 8000)
    
    
    

