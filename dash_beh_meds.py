import dash # v 1.16.2
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html  # v 1.1.1
# import dash_auth
import base64
import calendar
import datetime
from datetime import date, datetime, timedelta
# from datetime import *
import time 
from flask import Flask
import glob
import pandas as pd
import plotly.express as px # plotly v 5.2.1
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

import io
import re

from read_workbook import get_month_dataframe 

#setup Dash app 
app = dash.Dash(__name__, title='Behavior Medication Dashboard', external_stylesheets=[dbc.themes.DARKLY], prevent_initial_callbacks=True)

def dashboard():
    #import necessary files 
    pd.set_option('display.max_columns', 200)
    
    #NOTE; dataframe (dfmean) needs to be passed as an input here


    print(datetime.now())

    #get date
    # Textual month, day and year
    today = date.today()
    today = today.strftime("%B %d, %Y")
    today_fmt = pd.to_datetime(today)

    #get unique list of names for individuals
    # names = list(df['Name'].unique()) #zach - why call unique
    # names = sorted(names)

    #format date variables
    year = datetime.today().strftime('%Y')
    month = datetime.today().strftime('%m')
    day = datetime.today().strftime('%d')
    #------------------------------------------------------------------------
    #design layout of UI
    app.layout = html.Div([
                    #div containing labels and input functions 
                    html.Div([
                        #add CFD logo and label for resident selection
                        dbc.Row(
                                [
                                dbc.Col(
                                    html.Img(src="/assets/cfdlogo1.png"),
                                    style={'margin-top':20,'margin-left':20,'margin-bottom':0},
                                    width={'size': 6,'offset':0, 'order':1},
                                        ),    
                                
                                # dbc.Col(
                                #     html.Label('Select Resident'), 
                                #     style={'font-size': '18px','margin-top': 10,'margin-bottom':0},
                                #     width={'size': 2,'offset':9, 'order':3},
                                #         ),     
                                ]
                                ),
                        #row containing label and resident select
                            dcc.Store(id='stored-data', storage_type='session'),
                            
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                        # dbc.Row(
                        #         [
                        #         dbc.Col(
                        #             # replace with file widget
                        #             dcc.Dropdown(id="slct_pt",
                        #                         options=[
                        #                             {'label':i,'value':i} for i in names
                        #                             ],
                        #                         clearable=False,
                        #                         value='Ballantine-Kaplan, Eli', #zach - hardcoded name
                        #                         ),  
                        #             style={'margin-top':0},
                        #             width={'size': 2,'offset':9, 'order':2},
                        #                 ),
                        #         ]
                        #         ),
                        #row conaining date widget, aggregate selection 
                        dbc.Row(
                                [
                                
                                dbc.Col(
                                dcc.Dropdown(id="slct_tme",
                                            options=[
                                                {'label': 'Monthly', 'value': 'mon'},
                                                {'label': 'Weekly', 'value': 'wk'},
                                                {'label': 'Daily', 'value': 'day'},
                                                {'label': 'Shift', 'value': 'shift'},
                                                {'label': 'Rolling', 'value': 'roll'},
                                                ],
                                            value='mon',
                                            style={'margin-left': 40, 'margin-top': 10,'margin-bottom':0},
                                            clearable=False,
                                            placeholder="Monthly"
                                            ),  
                                style={},
                                width={'size': 3,'offset':0, 'order':1},
                                    ),
                                
                                dbc.Col(
                                            html.Label('Select Shift: '), 
                                            style={'font-size': '18px','margin-top': 30,},
                                            width={'size': 1,'offset':3, 'order':2},
                                            ),     
                                
                                dbc.Col(
                                    dcc.DatePickerRange(
                                            id='my-date-picker-range',
                                            calendar_orientation='horizontal',
                                            with_portal = False,
                                            clearable=False,
                                            number_of_months_shown = 1,
                                            min_date_allowed=date(2015, 1, 1),
                                            max_date_allowed=date(int(year), int(month), int(day)),
                                            initial_visible_month=date(int(year), int(month), int(day)),
                                            start_date=date((int(year)-1), int(month), int(day)),
                                            end_date=date(int(year), int(month), int(day)),

                                            persistence=True,
                                            persisted_props=['start_date'],
                                            persistence_type='session',  # session, local, or memory. Default is 'local'

                                            updatemode='bothdates',
                                        ),
                                            style={'margin-top': 20,},
                                            width={'size':2,'offset':2, 'order':3},
                                        ),
                                    
                                    html.Div(id='output-container-date-picker-range'),
                                ]
                                ),
                            #row containing select chart type, select shift, select aggregation
                            dbc.Row(
                                    [
                                    dbc.Col(
                                        dcc.RadioItems(
                                                id = 'slct_agg',
                                                options=[
                                                    {'label': 'Average per Shift', 'value': 'mean'},
                                                    {'label': 'Count Per Shift', 'value': 'sum'},
                                                ],
                                                value='mean',
                                                style={'display': 'inline-block','margin-top':10},
                                                inputStyle={"margin-left": "10px", "margin-right": "10px"}
                                                        ),width={'size': 3, 'offset':1,'order':3},
                                            ),

                                    dbc.Col(
                                        dcc.Checklist(
                                                id = 'slct_sft',
                                                options=[
                                                    {'label': '7:00 AM', 'value': '7-3'},
                                                    {'label': '3:00 PM', 'value': '3-11'},
                                                    {'label': '11:00 PM', 'value': '11-7'}
                                                        ],
                                                value=['7-3', '3-11', '11-7'],
                                                style={'display': 'inline-block', 'margin-top':10},
                                                inputStyle={"margin-left": "10px", "margin-right": "10px"}
                                                    ),width={'size': 2, 'offset':0,'order':2},
                                            ),

                                    dbc.Col(
                                    dcc.RadioItems(
                                            id = 'slct_gph',
                                            options=[
                                                {'label': 'Behavior Data - Bar', 'value': 'bar'},
                                                {'label': 'Behavior Data - Line', 'value': 'line'},
                                                {'label': 'Behavior Data - Trend (Linear)', 'value': 'ols'},
                                                {'label': 'Behavior Data - Trend (Polynomial)', 'value': 'poly'},
                                            ],
                                            value='bar',
                                            style={'margin-left':80,'display': 'inline-block','margin-top':10},
                                            inputStyle={"margin-left": "10px", "margin-right": "10px"}
                                                )
                                        ,width={'size': 6, 'offset':0, 'order':1},
                                            
                                        ),
                                    ]
                                    ),
                                ],
                            className="banner"),

            #2 rows containing graphs
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id='beh_meds_bar',figure={}),
                            width={'size': 10,'offset':1, 'order':1}
                        ),
                    ),

            dbc.Row(
                [
                dbc.Col(
                dcc.RadioItems(
                        id = 'slct_scl',
                        options=[
                            {'label': 'Medication Data - Log Scale   ', 'value': 'log'},
                            {'label': 'Medication Data - Linear Scale', 'value': 'lin'},
                        ],
                        value='log',
                        style={'margin-left':80,'display': 'inline-block',},
                        inputStyle={"margin-left": "10px", "margin-right": "10px"}
                        )
                    ,width={'size': 6, 'offset':0,},
                        
                        ),
                    
                    ]
                    ),

            dbc.Row(
                    dbc.Col(
                    dcc.Graph(id='beh_meds_line',figure={}),
                            width={'size': 10,'offset':1, 'order':1}
                        ),
                    ),
            html.Div(id='output-div'),
            html.Div(id='output-datatable'),
            
            ],
        )
    
    ##############################
    
    def parse_contents(contents, filename, date, store_data):
        content_type, content_string = contents.split(',')
        
        decoded = base64.b64decode(content_string)
        stored_df = pd.DataFrame(store_data)
        # print("YO", stored_df)
        try:
            workbook_xl = pd.ExcelFile(io.BytesIO(decoded))
            # print(workbook_xl)
            
            #aggregates all months data into a single data frame
            def get_all_months(workbook_xl):
                months = ['July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June']
                xl_file = pd.ExcelFile(workbook_xl)
                
                months_data = []
                for month in months:
                    months_data.append(get_month_dataframe(xl_file, month))
                    # print(months_data)
                return pd.concat(months_data)
            
            #run get all months function and produce behavior dataframe 
            df = get_all_months(workbook_xl)
            print(df.head())
            #convert episode values to float and aggregate mean per shift 
            df['value'] = df['value'].astype(float)
            dfmean = df.groupby(['Date', 'Shift','variable'],sort=False,)['value'].mean().round(2).reset_index()
            dfmean = pd.concat([stored_df, dfmean])
        
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([
            dcc.Store(id='stored-data', data=dfmean.to_dict('records')),
                        ])

    @app.callback(dash.dependencies.Output('output-datatable', 'children'),
                dash.dependencies.Input('upload-data', 'contents'),
                dash.dependencies.State('upload-data', 'filename'),
                dash.dependencies.State('upload-data', 'last_modified'),
                dash.dependencies.State('stored-data','data'))

    def update_output(list_of_contents, list_of_names, list_of_dates, store_data):
        if list_of_contents is not None:
            children = [
                parse_contents(c, n, d, store_data) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            return children
    
    ##############################
    # ------------------------------------------------------------------------------
    # set input and output dependencies
    @app.callback(
        [
        dash.dependencies.Output(component_id='beh_meds_bar', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_line', component_property='figure')
        ],
        [
        dash.dependencies.Input('my-date-picker-range', 'start_date'), # zach - why positional only here?
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
        # dash.dependencies.Input(component_id='slct_pt', component_property='value'),
        dash.dependencies.Input(component_id='slct_agg', component_property='value'),
        dash.dependencies.Input(component_id='slct_tme', component_property='value'),
        dash.dependencies.Input(component_id='slct_gph', component_property='value'),
        dash.dependencies.Input(component_id='slct_scl', component_property='value'),
        dash.dependencies.Input(component_id='slct_sft', component_property='value'),
        dash.dependencies.Input('stored-data', 'data'),
        ]
    )
    # --------------------------------------------------------------------------------
    # define function to control graphical outputs
    def update_graph(start_date,end_date,agg,time,beh_gph,scale,shift,data):
        patient = 'patient'

        print(shift)
        
        df_workbook = pd.DataFrame(data)
        
        #rename Target and Episode_Count columns 
        df_workbook.rename(columns={'variable':'Target','value':'Episode_Count'},inplace=True)
        
        #NOTE; need to align final date of behavior with final date of medication
        
        ''' Function that takes inputs from front end, consolidates and filters data based 
            on specific information request and displays graphically for end user '''

        #select data subset by individual 
        dfq = df_workbook
        print(dfq)
        
        # print(dfq.head())
        dfmeds = [] # df_meds

        #select whether to aggrate by mean or count 
        if agg == 'mean':
            tally = "Average"
        else:
            tally = "Count"
        print(time)
        #select date format 
        if time == 'mon':
            date_frmt = "Yr_Mnth"
        elif time == 'wk' or time == 'day':
            date_frmt = "Date"
        elif time == 'shift':
            date_frmt = "Date_Time"
            
        elif time == 'roll':
            date_frmt = "Rolling"
        else:
            date_frmt = "Year"
        
        #select shift 
        dfq = dfq.loc[dfq['Shift'].isin(shift)]

        #BEH DATA ------------------------------------------------------------------------------------------------------
        #read date range from UI and filter behavior dataset 
        flt_beh = (dfq['Date'] >= start_date) & (dfq['Date'] <= end_date)
        dfq = dfq.loc[flt_beh]
        # print(dfq.head())
        #format date variables for grouping requirements
        dfq['Year'] = pd.DatetimeIndex(dfq['Date']).year
        dfq['Month'] = pd.DatetimeIndex(dfq['Date']).month
        dfq['Month_Formated'] = dfq['Month'].apply(lambda x: calendar.month_abbr[x])
        dfq['Yr_Mnth'] = dfq['Month_Formated'] + "-" + dfq['Year'].astype(str)
        dfq['Rolling'] = 'Rolling'
        dfq = dfq.replace('Self-injury', 'Self-Injury')
        dfq = dfq.replace('SIB', 'Self-Injury')
        # print(dfq.head())

        #NOTE; dataframes are aggregated here per selection of timeframe 
        #determine groupings for various graphical outputs
        if time == 'mon' and agg == 'mean':
            dfm = dfq.groupby(['Yr_Mnth','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
            dfg = dfm
        elif time == 'mon' and agg == 'sum':
            dfm = dfq.groupby(['Yr_Mnth','Time','Year','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
            dfg = dfm
        else:
            print('Process Complete')

        if time == 'wk' and agg =='mean':
            dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W-MON')])['Episode_Count'].mean().round(2).reset_index().sort_values('Date')
            dfg = dfw
        elif time == 'wk' and agg =='sum':
            dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W-MON')])['Episode_Count'].sum().round(2).reset_index().sort_values('Date')
            dfg = dfw
        else:
            print('Process Complete')    
        
        if time == 'day' and agg == 'mean':
            dfd = dfq.groupby(['Date','Year','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
            dfg = dfd
            print("day: \n")
            print(dfd.head())
        elif time == 'day' and agg == 'sum':
            dfd = dfq.groupby(['Date','Year','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
            dfg = dfd
        else:
            print('Process Complete')

        if time == 'shift' and agg == 'mean':
            dfs = dfq.groupby(['Date_Time', 'Target',],sort=False,)['Episode_Count'].mean().reset_index()
            print("shift: \n")
            print(dfs.head())
            dfg = dfs
        elif time == 'shift' and agg == 'sum':
            dfs = dfq.groupby(['Date_Time','Target',],sort=False,)['Episode_Count'].mean().reset_index()
            dfg = dfs
        else:
            print('Process Complete')

        if time == 'roll' and agg == 'mean':
            dfm = dfq.groupby(['Rolling','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
            print(dfm)
            dfg = dfm
        elif time == 'roll' and agg == 'sum':
            dfm = dfq.groupby(['Rolling','Target'],sort=False,)['Episode_Count'].sum().round(2).reset_index()
            dfg = dfm
        else:
            print('Process Complete')

        #if dataframe empty pass in dummy data
        if dfg.empty:        
            dfg = dfg.append({date_frmt: start_date,'Target':'Null', 'Episode_Count':0}, ignore_index=True)
        # print(dfg)
        #ceate charts for behavior data
        if beh_gph == 'bar': 
            fig = px.bar(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            title="Aggregate Behavior Data: " + patient + " - " + today, barmode="group")
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")
        elif beh_gph == 'line':
            fig = px.line(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            title="Aggregate Behavior Data: " + patient + " - " + today,)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")
        elif beh_gph =='ols':
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            trendline="ols", title="Aggregate Behavior Data: " + patient + " - " + today)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")
        else:
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            trendline="lowess", title="Aggregate Behavior Data: " + patient + " - " + today)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")

        #MED DATA ------------------------------------------------------------------------------------------------------
        #group medication data, convert date vars to python datetime abd sort ascending
        print(patient)
        dfmeds['End'].fillna(value = today_fmt, inplace=True)
        dfmeds = dfmeds.groupby(['Name','Medication','Start','End'])['Dose'].sum().reset_index()
        dfmeds.sort_values(by = 'Start' , ascending = True, inplace=True)
        dfmeds = dfmeds.drop_duplicates(subset = ['Start','Medication'],keep='last')

        #create duplicate daily entries for all dosage data between start and end dates 
        if not dfmeds.empty:
            dfmeds = pd.concat([g.set_index('Start').reindex(pd.date_range(g['Start'].min(), g['End'].max(), freq='d'), method='ffill').reset_index().rename({'index':'Start'}, axis=1)
                        for _, g in dfmeds.groupby(['Name','Medication','Dose'])],
                        axis=0)
            dfmeds.sort_values(by = ['Medication', 'Start'] , ascending = True, inplace=True)
        #if no medication data within daterange create null dataframe
        elif dfmeds.empty:
            dfmeds = dfmeds.append({'Name':patient,'Medication':'Null','Measure_Date_Year': start_date, 'Start':start_date, 'End':end_date, 'Dose':0}, ignore_index=True)

        #read date range from UI and filter medication dataset 
        flt_meds = (dfmeds['Start'] >= start_date) & (dfmeds['Start'] <= end_date)
        dfmeds = dfmeds.loc[flt_meds]

        #drop any duplicate data created and convert Dose to numeric
        dfmeds = dfmeds.drop_duplicates(subset = ['Start','Medication'],keep='last')
    
        #create chart for medication data
        if scale == 'log':
            fig2 = px.line(dfmeds, x='Start', y="Dose", color = "Medication",
                title="Medication Dosages: " + patient + " - " + today, log_y=True)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(template = 'plotly_white',hovermode="x unified")
        else:
            fig2 = px.line(dfmeds, x='Start', y="Dose", color = "Medication",
                title="Medication Dosages: " + patient + " - " + today, log_y=False)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(template = 'plotly_white',hovermode="x unified")

        return fig, fig2

        # ------------------------------------------------------------------------------

print("\nloading... \n")
dashboard() 
print("\nComplete! \n")

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(host='10.1.84.77', port=8050)