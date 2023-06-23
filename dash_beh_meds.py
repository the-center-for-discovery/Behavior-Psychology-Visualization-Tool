import dash # v 1.16.2
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html  # v 1.1.1

import base64
import calendar
import datetime
from datetime import date, datetime, timedelta

import time 
from flask import Flask
import glob
import pandas as pd
import plotly.express as px # plotly v 5.2.1
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json

import io
import re

from read_workbook import * 

pd.options.mode.chained_assignment = None  # default='warn'

#setup Dash app 
app = dash.Dash(__name__, title='Behavior Medication Dashboard', external_stylesheets=[dbc.themes.DARKLY], prevent_initial_callbacks=True)

def dashboard():
    #import necessary files here
    pd.set_option('display.max_columns', 200)

    #get date
    # Textual month, day and year
    today = datetime.datetime.today().date()
    today = today.strftime("%B %d, %Y")
    today_fmt = pd.to_datetime(today)

    #format date variables
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')
    day = date.today().strftime('%d')
    
    #------------------------------------------------------------------------
    #design layout of UI
    def layout():
        return html.Div([
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
                                ]
                                ),
                        
                        #row containing label and resident select
                            dcc.Store(id='stored-data', storage_type='session'),
                            dcc.Store(id='stored-dur-data', storage_type='session'),
                            dcc.Store(id='stored-int-data', storage_type='session'),
                            dcc.Store(id='stored-meds-data', storage_type='session'),
                            dcc.Store(id='stored-name', storage_type='session'),
                            dcc.Store(id='stored-name-list', storage_type='session', data=[]),
                            dcc.Store(id='stored-filepath-data', storage_type='session'),
                            
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
                                multiple=False
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
                                            with_portal = True,
                                            clearable=False,
                                            number_of_months_shown = 6,
                                            is_RTL=False,
                                            min_date_allowed=date(2015, 1, 1),
                                            max_date_allowed=date(int(year), int(month), int(day)),
                                            initial_visible_month=date(int(year), int(month), int(day)),
                                            start_date=date((int(year)-1), int(month), int(day)),
                                            end_date=date(int(year), int(month), int(day)),

                                            persistence=True,
                                            persisted_props=['start_date'],
                                            persistence_type='session',  # session, local, or memory. Default is 'local'

                                            updatemode='singledate',
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
                dcc.Tabs([
                    dcc.Tab(label='Episodes', children=[
                        dbc.Col(
                            dcc.Graph(id='beh_meds_bar',figure={}),
                                    width={'size': 10,'offset':1, 'order':1}
                                ),]
                            ),
                        
                    dcc.Tab(label='Duration', children=[
                        dbc.Col(
                            dcc.Graph(id='beh_meds_dur',figure={}),
                                    width={'size': 10,'offset':1, 'order':1}
                                ),]
                            ),

                    dcc.Tab(label='Intervals', children=[
                        dbc.Col(
                            dcc.Graph(id='beh_meds_int',figure={}),
                                    width={'size': 10,'offset':1, 'order':1}
                                ),]
                            ),
                        
                        ]),
                    ),
            
            dbc.Row(
                [    
            dbc.Row(
                    dbc.Col(
                    dcc.Graph(id='beh_meds_line',figure={}),
                            width={'size': 10,'offset':1, 'order':1}
                        ),
                    ),
            html.Div(id='output-div'),
            html.Div(id='output-datatable'),
            
            dbc.Col(
                dcc.RadioItems(
                        id = 'slct_scl',
                        options=[
                            {'label': 'Medication Data - Logarithmic Scale   ', 'value': 'log'},
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

            ],
        )
    
    app.layout = layout

    ##############################
    
    def parse_contents(contents, filename, date, store_data, store_dur_data, store_int_data, store_meds_data,stored_name, stored_name_list):
        content_type, content_string = contents.split(',')
        
        decoded = base64.b64decode(content_string)
        stored_df = pd.DataFrame(store_data)
        print("store data", store_data)
        stored_dur_df = pd.DataFrame(store_dur_data)
        print("stored dur data", store_dur_data)
        stored_int_df = pd.DataFrame(store_int_data)
        print("stored int data", store_dur_data)
        stored_meds_df = pd.DataFrame(store_meds_data)
        print("stored_meds_df data", stored_meds_df)
        stored_name_list = pd.DataFrame(stored_name_list)

        new_name = pd.DataFrame( {
            filename : [stored_name]
        }
        )

        dfnames = pd.concat([stored_name_list, new_name])

        try:
            workbook_xl = pd.ExcelFile(io.BytesIO(decoded))
            
            dfstudet = pd.read_excel(workbook_xl, sheet_name=2, header=None)
            name = dfstudet.iloc[0,0]
            print(f"name is {name}")

            #aggregates all months data into a single data frame
            def get_all_months(workbook_xl):
                months = ['July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June']
                xl_file = pd.ExcelFile(workbook_xl)                
                months_data = []
                
                for month in months:
                    df_month = get_month_dataframe(xl_file, month)
                    months_data.append(df_month)
                return pd.concat(months_data)
            
            #run get all months function and produce behavior dataframe 
            df = get_all_months(workbook_xl)
            
            #convert episode values to float and aggregate mean per shift 
            df['value'] = df['value'].astype(float)
            dfmean = df.groupby(['Date', 'Shift','variable'],sort=False,)['value'].mean().round(2).reset_index()
            dfmean = pd.concat([stored_df, dfmean])
            # print(dfmean)

            dfmeds = get_all_meds_data(workbook_xl)

            dfmeds = pd.concat([stored_meds_df, dfmeds])
            
            dfdur, dfint = get_all_months_int_dur(workbook_xl)
            
            print(dfint)
        
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])
        
        return html.Div([
            dcc.Store(id='stored-data', data=dfmean.to_dict('records')),
            dcc.Store(id='stored-dur-data', data=dfdur.to_dict('records')),
            dcc.Store(id='stored-int-data', data=dfint.to_dict('records')),
            dcc.Store(id='stored-meds-data', data=dfmeds.to_dict('records')),
            dcc.Store(id='stored-name', data=name),
            dcc.Store(id='stored-name-list', data=dfnames.to_dict('records'))
                        ])

    @app.callback(
                dash.dependencies.Output('output-datatable', 'children'),
                dash.dependencies.Input('upload-data', 'contents'),
                dash.dependencies.State('upload-data', 'filename'),
                dash.dependencies.State('upload-data', 'last_modified'),
                dash.dependencies.State('stored-data','data'),
                dash.dependencies.State('stored-dur-data','data'),
                dash.dependencies.State('stored-int-data','data'),
                dash.dependencies.State('stored-meds-data','data'),
                dash.dependencies.State('stored-name','data'),
                dash.dependencies.State('stored-name-list','data')
                )

    def update_output(contents, filename, date_modified, store_data,store_dur_data, store_int_data, store_meds_data,stored_name, stored_name_list):
        if contents is not None:
            children = [
                parse_contents(contents, filename, date_modified, store_data, store_dur_data,store_dur_data, store_meds_data,stored_name, stored_name_list)]
            return children
    
    ##############################
    # ------------------------------------------------------------------------------
    # set input and output dependencies
    @app.callback(
        [
        dash.dependencies.Output(component_id='beh_meds_bar', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_line', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_dur', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_int', component_property='figure'),
        dash.dependencies.Output(component_id='my-date-picker-range', component_property='start_date'),
        dash.dependencies.Output(component_id='my-date-picker-range', component_property='end_date')
        ],
        [
        dash.dependencies.Input('my-date-picker-range', 'start_date'),
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
        # dash.dependencies.Input(component_id='slct_pt', component_property='value'),
        dash.dependencies.Input(component_id='slct_agg', component_property='value'),
        dash.dependencies.Input(component_id='slct_tme', component_property='value'),
        dash.dependencies.Input(component_id='slct_gph', component_property='value'),
        dash.dependencies.Input(component_id='slct_scl', component_property='value'),
        dash.dependencies.Input(component_id='slct_sft', component_property='value'),
        dash.dependencies.Input('stored-data', 'data'),
        dash.dependencies.Input('stored-dur-data', 'data'),
        dash.dependencies.Input('stored-int-data', 'data'),
        dash.dependencies.Input('stored-meds-data', 'data'),
        dash.dependencies.Input('stored-name', 'data'),
        dash.dependencies.Input('stored-name-list', 'data')
        ]
    )
    # --------------------------------------------------------------------------------
    # define function to control graphical outputs
    def update_graph(start_date,end_date,agg,time,beh_gph,scale,shift,data,store_dur_data,store_int_data,store_meds_data,stored_name,stored_name_list):
        
        if not stored_name:
            patient = 'patient'
        else:
            patient = f"<b>{stored_name}</b>"
        
        # print(f"stored name {stored_name}")
        
        # print(f"list of names - {stored_name_list}")
    
        #covert workbooks to dataframes     
        df_workbook = pd.DataFrame(data)
        dfdur = pd.DataFrame(store_dur_data)
        print(dfdur)
        dfint = pd.DataFrame(store_int_data)
        print(dfint)        
        dfmeds = pd.DataFrame(store_meds_data)
        dfnames = pd.DataFrame(stored_name_list)
        print(f"list of names - {list(dfnames.columns)}")
        
        #rename Target and Episode_Count columns 
        if not df_workbook.empty:
            df_workbook.rename(columns={'variable':'Target','value':'Episode_Count'},inplace=True)
            df_workbook.sort_values(by = ['Date','Target'], inplace=True)
            
            #clean behavior data 
            df_workbook = df_workbook.dropna()
            df_workbook = df_workbook[df_workbook["Target"].str.contains("Insert") == False]
            
        #get start and end from workbook
        if not df_workbook.empty:
            # start_date_wb = df_workbook['Date'].iloc[0]
            end_date_meds = df_workbook['Date'].iloc[-1]
            start_date_wb = start_date
            end_date_wb = end_date
        else:
            start_date_wb = start_date
            end_date_wb = end_date
           
        #NOTE; need to align final date of behavior with final date of medication
        
        ''' Function that takes inputs from front end, consolidates and filters data based 
            on specific information request and displays graphically for end user '''

        #select data subset by individual 
        dfq = df_workbook

        #select whether to aggrate by mean or count 
        if agg == 'mean':
            tally = "Average"
        else:
            tally = "Count"
        # print('time: ' + str(time))
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
        #don't process dfq if dfq is empty
        if not dfq.empty:
                            
            dfq = dfq.loc[dfq['Shift'].isin(shift)]

            #BEH DATA ------------------------------------------------------------------------------------------------------
            #read date range from UI and filter behavior dataset 
            flt_beh = (dfq['Date'] >= start_date_wb) & (dfq['Date'] <= end_date_wb)
            dfq = dfq.loc[flt_beh]
            # print(dfq.head())
            
            #format date variables for grouping requirements
            dfq['Year'] = pd.DatetimeIndex(dfq['Date']).year
            dfq['Month'] = pd.DatetimeIndex(dfq['Date']).month
            dfq['Yr_Mnth'] = pd.to_datetime(dfq['Date']).dt.strftime('%Y-%m')
            dfq['Month_Formated'] = dfq['Month'].apply(lambda x: calendar.month_abbr[x])
            dfq['Rolling'] = 'Rolling'
            
            #refactor and filer out erroneous target naming 
            dfq = dfq[~dfq['Target'].str.isdecimal()]
            # dfq = dfq[~(dfq == 0).any(axis=0)]
            dfq = dfq.replace('Self-injury', 'Self-Injury')
            dfq = dfq.replace('SIB', 'Self-Injury')
            # print(dfq.head())
            
            dfq.to_csv('toy_data.csv', index = False)

            #NOTE; dataframes are aggregated here per selection of timeframe 
            #determine groupings for various graphical outputs
            if time == 'mon' and agg == 'mean':
                dfm = dfq.groupby(['Yr_Mnth','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
                dfg = dfm
                dfg.sort_values(by = ['Yr_Mnth','Target'], inplace=True)
            elif time == 'mon' and agg == 'sum':
                dfm = dfq.groupby(['Yr_Mnth','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
                dfg = dfm
                dfg.sort_values(by = ['Yr_Mnth','Target'], inplace=True)
            else:
                print('Process Complete')
            if time == 'wk' and agg =='mean':
                dfq['Date'] = pd.to_datetime(dfq['Date'])
                dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W')])['Episode_Count'].mean().round(2).reset_index().sort_values('Date')
                dfg = dfw
                dfg.sort_values(by = ['Date','Target'], inplace=True)
            elif time == 'wk' and agg =='sum':
                dfq['Date'] = pd.to_datetime(dfq['Date'])
                dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W')])['Episode_Count'].sum().round(2).reset_index().sort_values('Date')
                dfg = dfw
                dfg.sort_values(by = ['Date','Target'], inplace=True)
            else:
                print('Process Complete')
            
            if time == 'day' and agg == 'mean':
                dfd = dfq.groupby(['Date','Year','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
                dfg = dfd
                dfg.sort_values(by = ['Date','Target'], inplace=True)
            elif time == 'day' and agg == 'sum':
                dfd = dfq.groupby(['Date','Year','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
                dfg = dfd
                dfg.sort_values(by = ['Date','Target'], inplace=True)
            else:
                print('Process Complete')

            if time == 'roll' and agg == 'mean':
                dfm = dfq.groupby(['Rolling','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
                dfg = dfm
                dfg.sort_values(by = ['Target'], inplace=True)
            elif time == 'roll' and agg == 'sum':
                dfm = dfq.groupby(['Rolling','Target'],sort=False,)['Episode_Count'].sum().round(2).reset_index()
                dfg = dfm
                dfg.sort_values(by = ['Target'], inplace=True)
            else:
                print('Process Complete')
        else:
            # when dfq is empty set dfg to be empty as well
            dfg = dfq

        #if dataframe empty pass in dummy data
        if dfg.empty:
            print(dfg)        
            dfg = dfg.append({date_frmt: start_date_wb,'Target':'Null', 'Episode_Count':0}, ignore_index=True)
        
        #ceate charts for behavior data
        if beh_gph == 'bar': 
            fig = px.bar(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date"},
                            title="Behavior and Medication Data: " + patient, barmode="group")
            fig.update_xaxes(tickangle=45, ticks="outside", ticklen=0,tickcolor='white')
            fig.update_layout(
                            template = 'plotly_white',hovermode="x unified",
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1),
                            xaxis_title=None
                              ),
        elif beh_gph == 'line':
            fig = px.line(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date"},
                            title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45, ticks="outside", ticklen=0,tickcolor='white')
            fig.update_layout(
                            template = 'plotly_white',hovermode="x unified",
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1),
                            xaxis_title=None
                              ),
        elif beh_gph =='ols':
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            # print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date"},
                            trendline="ols", title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45, ticks="outside", ticklen=0,tickcolor='white')
            fig.update_layout(
                            template = 'plotly_white',hovermode=False,
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1),
                            xaxis_title=None
                              ),
        
        else:
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            # print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",},
                            trendline="lowess", trendline_options=dict(frac=0.1), title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45, ticks="outside", ticklen=0,tickcolor='white')
            fig.update_layout(
                            template = 'plotly_white',hovermode=False,
                            legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1),
                            xaxis_title=None
                              ),
        
        #DUR DATA ------------------------------------------------------------------------------------------------------
        #NOTE; review "grouped + stacked barchart examples" to get final plots 
        if not dfdur.empty:
            flt_dur = (dfdur['Date'] >= start_date_wb) & (dfdur['Date'] <= end_date_wb)
            dfdur = dfdur.loc[flt_dur]

            #remove trailing 0 entries
            if not dfq.empty:
                last_date = dfq['Date'].max()
                dateflt_dur = (dfdur['Date'] <= last_date)
                dfdur = dfdur.loc[dateflt_dur]

            targets = dfdur["Target"].unique()
            dfdur_wide = pd.pivot_table(dfdur, values='value', index=['Date', 'variable'], columns='Target',aggfunc=np.max)
            dfdur_wide_grp = pd.pivot_table(dfdur_wide, index="Date", columns="variable", values=targets)

            dfdur_wide_grp['Yr_Mnth'] = pd.to_datetime(dfdur_wide_grp.index).strftime('%Y-%m')
            df_month = dfdur_wide_grp.groupby(['Yr_Mnth'],sort=False,)[dfdur_wide_grp.columns].sum().reset_index()
            df_dates = dfdur_wide_grp.groupby(['Yr_Mnth'],sort=False,)[dfdur_wide_grp.columns].sum()
            dfdur_wide_grp = df_month.drop('Yr_Mnth', axis='columns')

            figdur = go.Figure(
                layout=go.Layout(
                    template = 'plotly_white',
                    height=600,
                    #width=1000,
                    barmode="group",
                    yaxis_title="count",
                    yaxis_showticklabels=True,
                    yaxis_showgrid=True,
                    yaxis_range=[0, dfdur_wide_grp.groupby(axis=1, level=0).sum().max().max() * 1.5],
                # Secondary y-axis overlayed on the primary one and not visible
                    yaxis2=go.layout.YAxis(
                        visible=False,
                        matches="y",
                        overlaying="y",
                        anchor="x",
                    ),
                    font=dict(size=12),
                    legend_x=0,
                    legend_y=1,
                    legend_orientation="h",
                    hovermode="x unified",
                    showlegend=False,
                    margin=dict(b=0,t=10,l=0,r=10)
                )
            )

            # Define some colors for the duration data
            colors = { 
                "beh 1" : {
                    "Duration: 0": "#00D8FF",#
                    "Duration: <5": "#00BCDE",#
                    "Duration: 6-10": "#00A7C6",#
                    "Duration: 11-15": "#0089A3",#
                    "Duration: 16-20": "#006D82",#
                    "Duration: 20+" : "#005262",#
                },
                "beh 2" : {
                    "Duration: 0": "#F7FF00",#
                    "Duration: <5": "#D6DD00",#
                    "Duration: 6-10": "#BAC100",#
                    "Duration: 11-15": "#9CA200",#
                    "Duration: 16-20": "#838800",#
                    "Duration: 20+" : "#6A6E00",#
                },
                "beh 3" : {
                    "Duration: 0": "#00FF08",#
                    "Duration: <5": "#00ED07",#
                    "Duration: 6-10": "#00D006",#
                    "Duration: 11-15": "#00AD05",#
                    "Duration: 16-20": "#008C04",#
                    "Duration: 20+" : "#006A03",#
                },
                "beh 4" : {
                    "Duration: 0": "#FF0000",#
                    "Duration: <5": "#F00202",#
                    "Duration: 6-10": "#CA0000",#
                    "Duration: 11-15": "#AF0000",#
                    "Duration: 16-20": "#900000",#
                    "Duration: 20+" : "#6C0000",#
                },
                "beh 5" : {
                    "Duration: 0": "#d900ff",#
                    "Duration: <5": "#bd02de",#
                    "Duration: 6-10": "#9a02b5",#
                    "Duration: 11-15": "#85039c",#
                    "Duration: 16-20": "#68017a",#
                    "Duration: 20+" : "#43014f",#
                },
            }

            # Add the traces
            for i, t in enumerate(colors):
                base_offset = 0
                for j, col in enumerate(colors[t]):
                    if i >= len(targets):
                        continue
                    beh = targets[i]
                    if (dfdur_wide_grp[beh][col] == 0).all():
                        continue
                    # print(df[t][col])
                    # print(df.index)
                    figdur.add_trace(go.Bar(
                        x=df_dates.index,
                        y=dfdur_wide_grp[beh][col],
                        base=base_offset,
                        # Set the right yaxis depending on the selected product (from enumerate)
                        # yaxis=f"y{i + 1}",
                        # Offset the bar trace, offset needs to match the width
                        # The values here are in milliseconds, 1billion ms is ~1/3 month
                        offsetgroup=str(i),
                        #offset=(i - 1) * 1,
                        #width=1,
                        legendgroup=beh,
                        legendgrouptitle_text=beh,
                        name=col,
                        marker_color=colors[t][col],
                        marker_line=dict(width=0, color="#333"),
                        hovertemplate= beh + " " + str(col)+ ": %{y} " + "<extra></extra>"
                                        )
                                )
                    
                    base_offset += dfdur_wide_grp[beh][col]

            #figdur = px.bar(dfdur,x = 'Target', y='value', color = 'variable',
            #    color_discrete_sequence= px.colors.sequential.Reds, category_orders={"variable": ["Duration: 0", "Duration: <5", "Sat", "Duration: 6-10",
            #                                                                                "Duration: 11-15","Duration: 16-20", "Duration: 20+"]})
            #figdur.update_traces(width=0.4)
        else:
            dfdur = dfdur.append({'Date': 'None','Target':'Null', 'variable':'Null', 'value':'Null'}, ignore_index=True)
            print(dfdur)
            figdur = px.bar(dfdur,x = 'Target', y='value', color = 'variable')
        
        #INT DATA ------------------------------------------------------------------------------------------------------
        if not dfint.empty:
            flt_int = (dfint['Date'] >= start_date_wb) & (dfint['Date'] <= end_date_wb)
            dfint = dfint.loc[flt_int]

            #remove trailing 0 entries
            if not dfq.empty:
                last_date = dfq['Date'].max()
                dateflt_int = (dfint['Date'] <= last_date)
                dfint = dfint.loc[dateflt_int]

            targets = dfint["Target"].unique()
            dfin_wide = pd.pivot_table(dfint, values='value', index=['Date', 'variable'], columns='Target',aggfunc=np.max)
            dfin_wide_grp = pd.pivot_table(dfin_wide, index="Date", columns="variable", values=targets)
            dfin_wide_grp.index.name = None

            #group by month
            dfin_wide_grp['Yr_Mnth'] = pd.to_datetime(dfin_wide_grp.index).strftime('%Y-%m')
            dfin_m = dfin_wide_grp.groupby(['Yr_Mnth'],sort=False,)[dfin_wide_grp.columns].sum().reset_index()
            df_month_data = dfin_wide_grp.groupby(['Yr_Mnth'],sort=False,)[dfin_wide_grp.columns].sum()
            dfin_wide_grp = dfin_m.drop('Yr_Mnth', axis='columns')

            # Create a figure with the right layout
            figint = go.Figure(
                layout=go.Layout(
                    template = 'plotly_white',
                    height=600,
                    #width=1000,
                    barmode="group",
                    yaxis_title="count",
                    yaxis_showticklabels=True,
                    yaxis_showgrid=True,
                    yaxis_range=[0, dfin_wide_grp.groupby(axis=1, level=0).sum().max().max() * 1.5],
                # Secondary y-axis overlayed on the primary one and not visible
                    yaxis2=go.layout.YAxis(
                        visible=False,
                        matches="y",
                        overlaying="y",
                        anchor="x",
                    ),
                    font=dict(size=12),
                    legend_x=0,
                    legend_y=1,
                    legend_orientation="h",
                    hovermode="x unified",
                    margin=dict(b=0,t=10,l=0,r=10),
                    showlegend=False
                )
            )

            # Define some colors for the interval data
            colors = {
                "beh 1" : {
                    "Interval: 0" : "#00D8FF",
                    "Interval: 1": "#00BCDE",
                    "Interval: 2": "#00A7C6",
                    "Interval: 3": "#0089A3",
                    "Interval: 4": "#006D82",
                },
                "beh 2" : {
                    "Interval: 0" : "#F7FF00",
                    "Interval: 1": "#D6DD00",
                    "Interval: 2": "#BAC100",
                    "Interval: 3": "#9CA200",
                    "Interval: 4": "#838800",
                },
                "beh 3" : {
                    "Interval: 0" : "#00FF08",
                    "Interval: 1": "#00ED07",
                    "Interval: 2": "#00D006",
                    "Interval: 3": "#00AD05",
                    "Interval: 4": "#008C04",
                },
                "beh 4" : {
                    "Interval: 0" : "#FF0000",
                    "Interval: 1": "#F00202",
                    "Interval: 2": "#CA0000",
                    "Interval: 3": "#AF0000",
                    "Interval: 4": "#900000",
                },
                "beh 5" : {
                    "Interval: 0": "#d900ff",#
                    "Interval: 1": "#bd02de",#
                    "Interval: 2": "#9a02b5",#
                    "Interval: 3": "#85039c",#
                    "Interval: 4": "#68017a",#
                },
            }

            #removes all zeros rows
            # df = df.loc[~(df==0).all(axis=1)]

            # Add the traces
            for i, t in enumerate(colors):
                base_offset = 0
                for j, col in enumerate(colors[t]):
                    if i >= len(targets):
                        continue
                    beh = targets[i]
                    if (dfin_wide_grp[beh][col] == 0).all():
                        continue
                    # print(df[t][col])
                    # print(df.index.to_list())
                    figint.add_trace(go.Bar(
                        x=df_month_data.index,
                        y=dfin_wide_grp[beh][col],
                        base=base_offset,
                        # Set the right yaxis depending on the selected product (from enumerate)
                        # yaxis=f"y{i + 1}",
                        # Offset the bar trace, offset needs to match the width
                        # The values here are in milliseconds, 1billion ms is ~1/3 month
                        offsetgroup=str(i),
                        #offset=(i - 1) * 1,
                        #width=1,
                        legendgroup=beh,
                        legendgrouptitle_text=beh,
                        name=col,
                        marker_color=colors[t][col],
                        marker_line=dict(width=0, color="#333"),
                        hovertemplate=beh + " " + str(col)+ ": %{y} " + "<extra></extra>"
                                        )
                                )

                    base_offset += dfin_wide_grp[beh][col]

            #print(dfint.head())
            #figint = px.bar(dfint,x = 'Target', y='value', color = 'variable',
            #    color_discrete_sequence= px.colors.sequential.Greens, category_orders={"variable": ["Interval: 0", "Interval: 1", "Interval: 2",
            #                                                                                   "Interval: 3","Interval: 4"]})
            #figint.update_traces(width=0.4)
        else:
            dfint = dfint.append({'Date': 'None','Target':'Null', 'variable':'Null', 'value':'Null'}, ignore_index=True)
            print(dfint)
            figint = px.bar(dfint,x = 'Target', y='value', color = 'variable')
    
        #MED DATA ------------------------------------------------------------------------------------------------------
        #group medication data, convert date vars to python datetime abd sort ascending
        print(patient)
        #drop any duplicate data created and convert Dose to numeric
        if not dfmeds.empty:
            dfmeds = pd.melt(dfmeds, id_vars =['Dose','Units','Medication'])
            dfmeds = dfmeds.rename(columns = {'value':'Date'})
            dfmeds.sort_values(by='Date',inplace=True)
            
            dfmeds = dfmeds.drop_duplicates(subset = ['Date','Medication'],keep='last')

            dfmeds['Dose'] = dfmeds['Dose'].astype(float)
            print(end_date_meds)
            dfmeds['Date'] = dfmeds['Date'].fillna(end_date_meds)
            dfmeds['Date'] = pd.to_datetime(dfmeds['Date'])
            # print(dfmeds.tail())
            dfmeds['Medication'] = dfmeds['Medication'] + " (" + dfmeds['Units'] + ")"
            
            #format date variables for grouping requirements
            dfmeds['Year'] = pd.DatetimeIndex(dfmeds['Date']).year
            dfmeds['Month'] = pd.DatetimeIndex(dfmeds['Date']).month
            dfmeds['Yr_Mnth'] = pd.to_datetime(dfmeds['Date']).dt.strftime('%Y-%m')
            dfmeds['Month_Formated'] = dfmeds['Month'].apply(lambda x: calendar.month_abbr[x])
            dfmeds['Rolling'] = 'Rolling'
            
            # print(dfmeds.head())
            
            #front fill dosage data 
            def expand_dates(ser):
                return pd.DataFrame({'Date': pd.date_range(ser['Date'].min(), end_date_meds, freq='D')})

            dfmeds = dfmeds.groupby(['Medication']).apply(expand_dates).reset_index().merge(dfmeds, how='left')[['Medication', 'Date', 'Dose']].ffill()
        else:
            dfmeds = dfmeds.append({'Medication':'Null','Date': 'None', 'Dose':0,'variable':'Null', 'Units':'Null', 'Dose':0}, ignore_index=True)
        
        # read date range from UI and filter medication dataset 
        flt_meds = (dfmeds['Date'] >= start_date_wb) & (dfmeds['Date'] <= end_date_wb)
        dfmeds = dfmeds.loc[flt_meds]

        #create chart for medication data
        if scale == 'log':
            fig2 = px.line(dfmeds, x='Date', y="Dose", color = "Medication", log_y=True)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(
                                template = 'plotly_white',hovermode="x unified",
                                legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1),
                                xaxis={'visible': False, 'showticklabels': False}
                              )
        else: 
            fig2 = px.line(dfmeds, x='Date', y="Dose", color = "Medication",
                title="Medication Data",log_y=False)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(template = 'plotly_white',hovermode="x unified",
                                legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1),
                                xaxis={'visible': False, 'showticklabels': False}
                                )
        
        if not df_workbook.empty and start_date_wb == start_date_wb:
            start_date_wb = start_date
            end_date_wb = end_date
        
        return fig, fig2, figdur, figint, start_date_wb, end_date_wb

        # ------------------------------------------------------------------------------

print("\nloading... \n")
dashboard() 
print("\nComplete! \n")

if __name__ == '__main__':
    app.run_server(debug=True)
    
    #Conor's Mac
    # app.run_server(host='10.1.183.58', port=8050)
    
    #Mac Pro0
    # app.run_server(host='10.1.84.68', port=8050)