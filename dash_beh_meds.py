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
    today = date.today()
    today = today.strftime("%B %d, %Y")
    today_fmt = pd.to_datetime(today)

    #format date variables
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')
    day = date.today().strftime('%d')
    
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
                                ]
                                ),
                        
                        #row containing label and resident select
                            dcc.Store(id='stored-data', storage_type='session'),
                            dcc.Store(id='stored-meds-data', storage_type='session'),
                            dcc.Store(id='stored-name', storage_type='session'),
                            dcc.Store(id='stored-name-list', storage_type='session', data=[]),
                            
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
                                                # {'label': 'Shift', 'value': 'shift'},
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
    
    ##############################
    
    def parse_contents(contents, filename, date, store_data, store_meds_data,stored_name):
        content_type, content_string = contents.split(',')
        
        decoded = base64.b64decode(content_string)
        stored_df = pd.DataFrame(store_data)
        stored_meds_df = pd.DataFrame(store_meds_data)

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

            dfmeds = get_all_meds_data(workbook_xl)
            dfmeds = pd.concat([stored_meds_df, dfmeds])
        
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([
            dcc.Store(id='stored-data', data=dfmean.to_dict('records')),
            dcc.Store(id='stored-meds-data', data=dfmeds.to_dict('records')),
            dcc.Store(id='stored-name', data=name)
                        ])

    @app.callback(
                dash.dependencies.Output('output-datatable', 'children'),
                dash.dependencies.Input('upload-data', 'contents'),
                dash.dependencies.State('upload-data', 'filename'),
                dash.dependencies.State('upload-data', 'last_modified'),
                dash.dependencies.State('stored-data','data'),
                dash.dependencies.State('stored-meds-data','data'),
                dash.dependencies.State('stored-name','data')
                )

    def update_output(contents, filename, date_modified, store_data, store_meds_data,stored_name):
        if contents is not None:
            children = [
                parse_contents(contents, filename, date_modified, store_data, store_meds_data,stored_name)]
            return children
    
    ##############################
    # ------------------------------------------------------------------------------
    # set input and output dependencies
    @app.callback(
        [
        dash.dependencies.Output(component_id='beh_meds_bar', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_line', component_property='figure'),
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
        dash.dependencies.Input('stored-meds-data', 'data'),
        dash.dependencies.Input('stored-name', 'data'),
        dash.dependencies.State(component_id='stored-name-list', component_property='data')
        ]
    )
    # --------------------------------------------------------------------------------
    # define function to control graphical outputs
    def update_graph(start_date,end_date,agg,time,beh_gph,scale,shift,data, store_meds_data,stored_name,stored_name_list):
        
        if not stored_name:
            patient = 'patient'
        else:
            patient = stored_name
        
        print(f"stored name {stored_name}")
        
        stored_name_list.append(stored_name)
        
        print(f"list of names - {stored_name_list}")
    
        #covert workbooks to dataframes     
        df_workbook = pd.DataFrame(data)
        dfmeds = pd.DataFrame(store_meds_data)
        
        #rename Target and Episode_Count columns 
        if not df_workbook.empty:
            df_workbook.rename(columns={'variable':'Target','value':'Episode_Count'},inplace=True)
            df_workbook.sort_values(by = ['Date','Target'], inplace=True)
            
            #clean behavior data 
            df_workbook = df_workbook.dropna()
            df_workbook = df_workbook[df_workbook["Target"].str.contains("Insert") == False]
            
        #get start and end from workbook
        if not df_workbook.empty:
            start_date_wb = df_workbook['Date'].iloc[0]
            end_date_wb = df_workbook['Date'].iloc[-1]
           
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
                dfm = dfq.groupby(['Yr_Mnth','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
                dfg = dfm
            else:
                print('Process Complete')
            if time == 'wk' and agg =='mean':
                dfq['Date'] = pd.to_datetime(dfq['Date'])
                dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W')])['Episode_Count'].mean().round(2).reset_index().sort_values('Date')
                dfw.sort_values(by = ['Date','Target'], inplace=True)
                dfg = dfw
            elif time == 'wk' and agg =='sum':
                dfq['Date'] = pd.to_datetime(dfq['Date'])
                dfw = dfq.groupby(['Target', pd.Grouper(key='Date', freq='W')])['Episode_Count'].sum().round(2).reset_index().sort_values('Date')
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

            if time == 'roll' and agg == 'mean':
                dfm = dfq.groupby(['Rolling','Target',],sort=False,)['Episode_Count'].mean().round(2).reset_index()
                print(dfm)
                dfg = dfm
            elif time == 'roll' and agg == 'sum':
                dfm = dfq.groupby(['Rolling','Target'],sort=False,)['Episode_Count'].sum().round(2).reset_index()
                dfg = dfm
            else:
                print('Process Complete')
        else:
            # when dfq is empty set dfg to be empty as well
            dfg = dfq

        #if dataframe empty pass in dummy data
        if dfg.empty:        
            dfg = dfg.append({date_frmt: start_date_wb,'Target':'Null', 'Episode_Count':0}, ignore_index=True)
        
        # print(dfg)
        #ceate charts for behavior data
        if beh_gph == 'bar': 
            fig = px.bar(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            title="Behavior and Medication Data: " + patient, barmode="group")
            fig.update_xaxes(tickangle=45, ticks="outside", ticklen=30,tickcolor='white')
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
                                    "Yr_Mnth": "Date" },
                            title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")
        elif beh_gph =='ols':
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            trendline="ols", title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x unified")
        
        else:
            dfg[date_frmt] = pd.to_datetime(dfg[date_frmt])
            print(dfg)
            fig = px.scatter(dfg, x=date_frmt, y="Episode_Count", color = "Target",
                            labels={"Episode_Count": tally + " per Shift",
                                    "Target":"Target",
                                    "Yr_Mnth": "Date" },
                            trendline="lowess", trendline_options=dict(frac=0.1), title="Behavior and Medication Data: " + patient)
            fig.update_xaxes(tickangle=45,)
            fig.update_layout(template = 'plotly_white',hovermode="x")

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
            dfmeds['Date'] = dfmeds['Date'].fillna(end_date_wb)
            dfmeds['Date'] = pd.to_datetime(dfmeds['Date'])
            dfmeds['Medication'] = dfmeds['Medication'] + " (" + dfmeds['Units'] + ")"
            
            #front fill dosage data 
            def expand_dates(ser):
                return pd.DataFrame({'Date': pd.date_range(ser['Date'].min(), date.today(), freq='D')})

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
            fig2.update_layout(template = 'plotly_white',hovermode="x unified")
        
        if not df_workbook.empty and start_date_wb == start_date_wb:
            start_date_wb = start_date
            end_date_wb = end_date
        
        return fig, fig2, start_date_wb, end_date_wb

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