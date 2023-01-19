import dash # v 1.16.2
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html  # v 1.1.1
import dash_auth

import calendar
import datetime
from datetime import date
from datetime import date, datetime, timedelta
import time 
from flask import Flask
import glob
import pandas as pd
import plotly.express as px # plotly v 5.2.1
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

#setup Dash app 
app = dash.Dash(__name__, title='Behavior Medication Dashboard', external_stylesheets=[dbc.themes.DARKLY], prevent_initial_callbacks=True)

auth = dash_auth.BasicAuth(
    app,
    {'temp': 'Disc0very21',
    }
)

def dashboard():
    #import necessary files 
    pd.set_option('display.max_columns', 200)
    #store pathnames for relevent development machines
    #pathnames pro
    dir_pro = '//DISCOVERYDB/Data Warehouse/Output_CUBRC/'
    path_pro = glob.glob(dir_pro + 'tbl_Clinical_Behavior_Tracking_01_Target_00_No_Data_*')
    print(path_pro[1])
    path_meds = glob.glob(dir_pro + 'tbl_Clinical_Behavior_Tracking_06_Medications_Data_*')
    df_meds = pd.read_csv(path_meds[1],dtype='unicode')
    path_bm = glob.glob(dir_pro + 'tbl_Clinical_BM_Menses_*')
    df_bm = pd.read_csv(path_bm[1],dtype='unicode')
    path_slp = glob.glob(dir_pro + 'tbl_Clinical_Sleep_*')
    df_slp = pd.read_csv(path_slp[1],dtype='unicode')
   
    #df macpro
    df = pd.read_csv(path_pro[0], dtype='unicode')

    #configure formatting of colums where necessary
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date_Time'] = pd.to_datetime(df['Date_Time'])
    df['Episode_Count'] = pd.to_numeric(df['Episode_Count'])
    df_meds['Dose'] = df_meds['Dose'].str.extract('(\d+)', expand=False) #zach - what does this line do?
    df_meds['Medication'] = df_meds['Medication'] + \
        ' (' + df_meds['Unit'] + ')' #zach - why not on one line
    df_meds[['Start', 'End']] = df_meds[['Start', 'End']].apply(pd.to_datetime)
    df_meds['Dose'] = pd.to_numeric(df_meds['Dose'])
    df_bm['Menses'].replace({'False': 0, 'True': 1}, inplace=True)
    df_slp['Date'] = pd.to_datetime(df_slp['Date'])
    df_slp['Sleep_Hours'] = pd.to_numeric(df_slp['Sleep_Hours'])
    df_bm.head()
    df_bm['Date'] = pd.to_datetime(df_bm['Date'])

    print(datetime.now())

    #get date
    # Textual month, day and year
    today = date.today()
    today = today.strftime("%B %d, %Y")
    today_fmt = pd.to_datetime(today)

    #get unique list of names for individuals
    names = list(df['Name'].unique()) #zach - why call unique
    names = sorted(names)

    #format date variables
    year = datetime.today().strftime('%Y')
    month = datetime.today().strftime('%m')
    day = datetime.today().strftime('%d')
    #------------------------------------------------------------------------
    #design layout of UI
    app.layout = html.Div([

        dcc.Interval(
            id='my_interval',
            disabled=False,  # if True, the counter will no longer update
            interval=1*3000,  # increment the counter n_intervals every interval milliseconds
            n_intervals=0,  # number of times the interval has passed
            max_intervals=4,  # number of times the interval will be fired.
            #if -1, then the interval has no limit (the default)
            #and if 0 then the interval stops running.
        ),
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
                                
                                dbc.Col(
                                    html.Label('Select Resident'), 
                                    style={'font-size': '18px','margin-top': 10,'margin-bottom':0},
                                    width={'size': 2,'offset':9, 'order':3},
                                        ),     
                                ]
                                ),
                        #row containing label and resident select
                        dbc.Row(
                                [
                                dbc.Col(
                                    dcc.Dropdown(id="slct_pt",
                                                options=[
                                                    {'label':i,'value':i} for i in names
                                                    ],
                                                clearable=False,
                                                value='Ballantine-Kaplan, Eli', #zach - hardcoded name
                                                ),  
                                    style={'margin-top':0},
                                    width={'size': 2,'offset':9, 'order':2},
                                        ),
                                ]
                                ),
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
                                                    {'label': '7:00 AM', 'value': '07:00:00'},
                                                    {'label': '3:00 PM', 'value': '15:00:00'},
                                                    {'label': '11:00 PM', 'value': '23:00:00'}
                                                        ],
                                                value=['07:00:00', '15:00:00', '23:00:00'],
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
                    
                    dbc.Col(
                        dcc.Textarea(
                        id='text_meds',
                        value='Add notes...',
                        style={'width': '80%', 'height': 50},
                        ),width={'size': 6, 'offset':6,},
                    ),
                    
                    ]
                    ),



            dbc.Row(
                
            dcc.Tabs([
                
                dcc.Tab(label='Medication Data', children=[
                    
                    dbc.Col(        
                        dcc.Graph(id='beh_meds_line', figure={}),
                        width={'size': 10,'offset':1, 'order':1}
                            ),
                        
                                                    ]
                        ),
                dcc.Tab(label='BM/Menses', children=[
                    
                    dbc.Col(        
                        dcc.Graph(id='bm_mens', figure={}),
                        width={'size': 10,'offset':1, 'order':1}
                            ),
                        
                                                    ]
                        ),      
                    
                dcc.Tab(label='Sleep', children=[
                    
                    dbc.Col(        
                        dcc.Graph(id='sleep', figure={}),
                        width={'size': 10,'offset':1, 'order':1}
                            ),
                        
                                                    ]
                        ),      
                    
                    ]),              
                    
                    ),

            # end of Div 
            ],
        )
    # ------------------------------------------------------------------------------
    # set input and output dependencies
    @app.callback(
        [
        dash.dependencies.Output(component_id='beh_meds_bar', component_property='figure'),
        dash.dependencies.Output(component_id='beh_meds_line', component_property='figure'),
        dash.dependencies.Output(component_id='bm_mens', component_property='figure'),
        dash.dependencies.Output(component_id='sleep', component_property='figure')
        ],
        [
        dash.dependencies.Input('my-date-picker-range', 'start_date'), # zach - why positional only here?
        dash.dependencies.Input('my-date-picker-range', 'end_date'),
        dash.dependencies.Input(component_id='slct_pt', component_property='value'),
        dash.dependencies.Input(component_id='slct_agg', component_property='value'),
        dash.dependencies.Input(component_id='slct_tme', component_property='value'),
        dash.dependencies.Input(component_id='slct_gph', component_property='value'),
        dash.dependencies.Input(component_id='slct_scl', component_property='value'),
        dash.dependencies.Input(component_id='slct_sft', component_property='value')
        ]
    )
    # --------------------------------------------------------------------------------
    # define function to control graphical outputs
    def update_graph(start_date,end_date,patient,agg,time,beh_gph,scale,shift):

        print(shift) 
        
        ''' Function that takes inputs from front end, consolidates and filters data based 
            on specific information request and displays graphically for end user '''

        #select data subset by individual 
        dfq = df.query('Name == @patient')
        dfmeds = df_meds.query('Name == @patient')
        dfbm = df_bm.query('Name == @patient')
        dfslp = df_slp.query('Name == @patient')

        #select whether to aggrate by mean or count 
        if agg == 'mean':
            tally = "Average"
        else:
            tally = "Count"

        #select date format 
        if time == 'mon':
            date_frmt = "Yr_Mnth"
        elif time == 'wk' or time == 'day':
            date_frmt = "Date"
        elif time == 'roll':
            date_frmt = "Rolling"
        else:
            date_frmt = "Year"
        
        #select shift 
        dfq = dfq.loc[dfq['Time'].isin(shift)]

        #BEH DATA ------------------------------------------------------------------------------------------------------
        #read date range from UI and filter behavior dataset 
        flt_beh = (dfq['Date'] >= start_date) & (dfq['Date'] <= end_date)
        dfq = dfq.loc[flt_beh]
        #format date variables for grouping requirements
        dfq['Year'] = pd.DatetimeIndex(dfq['Date']).year
        dfq['Month'] = pd.DatetimeIndex(dfq['Date']).month
        dfq['Month_Formated'] = dfq['Month'].apply(lambda x: calendar.month_abbr[x])
        dfq['Yr_Mnth'] = dfq['Month_Formated'] + "-" + dfq['Year'].astype(str)
        dfq['Rolling'] = 'Rolling'
        dfq = dfq.replace('Self-injury', 'Self-Injury')
        dfq = dfq.replace('SIB', 'Self-Injury')
        print(dfq.head())


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
        elif time == 'day' and agg == 'sum':
            dfd = dfq.groupby(['Date','Year','Target',],sort=False,)['Episode_Count'].sum().round(2).reset_index()
            dfg = dfd
        else:
            print('Process Complete')

        if time == 'shift' and agg == 'mean':
            dfs = dfq.groupby(['Date_Time', 'Target',],sort=False,)['Episode_Count'].mean().reset_index()
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
        print(dfg)
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

        dfmeds.to_csv("output_{}.csv".format(patient))

        #create duplicate daily entries for all dosage data between start and end dates 
        if not dfmeds.empty:
            dfmeds = pd.concat([g.set_index('Start').reindex(pd.date_range(g['Start'].min(), g['End'].max(), freq='d'), method='ffill').reset_index().rename({'index':'Start'}, axis=1)
                        for _, g in dfmeds.groupby(['Name','Medication','Dose'])],
                        axis=0)
            dfmeds.sort_values(by = ['Medication', 'Start'] , ascending = True, inplace=True)
        #if no medication data within daterange create null dataframe
        elif dfmeds.empty:
            dfmeds = dfmeds.append({'Name':patient,'Medication':'Null','Measure_Date_Year': start_date, 'Start':start_date, 'End':end_date, 'Dose':0}, ignore_index=True)
        print(dfmeds)

        #read date range from UI and filter medication dataset 
        flt_meds = (dfmeds['Start'] >= start_date) & (dfmeds['Start'] <= end_date)
        dfmeds = dfmeds.loc[flt_meds]

        #drop any duplicate data created and convert Dose to numeric
        dfmeds = dfmeds.drop_duplicates(subset = ['Start','Medication'],keep='last')
    
        #create chart for medication data
        if scale == 'log':
            fig2 = px.line(dfmeds, x='Start', y="Dose", color = "Medication",
                # labels={"Episode_Count": tally + " per Shift",
                #         "Target":"Target",
                #         "Yr_Mnth": "Date" },
                title="Medication Dosages: " + patient + " - " + today, log_y=True)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(template = 'plotly_white',hovermode="x unified")
        else:
            fig2 = px.line(dfmeds, x='Start', y="Dose", color = "Medication",
                # labels={"Episode_Count": tally + " per Shift",
                #         "Target":"Target",
                #         "Yr_Mnth": "Date" },
                title="Medication Dosages: " + patient + " - " + today, log_y=False)
            fig2.update_xaxes(tickangle=45,)
            fig2.update_layout(template = 'plotly_white',hovermode="x unified")

        #BM_MENS DATA ------------------------------------------------------------------------------------------------------
        
        flt_bm = (dfbm['Date'] >= start_date) & (dfbm['Date'] <= end_date)
        dfbm = dfbm.loc[flt_bm]
        
        dfbm = dfbm.groupby(['Date','BM_Bristol','Menses'])['BM_Size'].count().reset_index()
        
        dfbm = dfbm.drop_duplicates(subset = ['Date','Menses'],keep='last')

        fig3 = make_subplots(specs=[[{"secondary_y": True}]])

        x = dfbm['Date']
        bm = dfbm['BM_Size']
        mn = dfbm['Menses']
        fig3.add_trace(go.Scatter(x=x, y=bm,name='BM'), secondary_y=False,)
        fig3.add_trace(go.Bar(x=x, y=mn,name='Menses'), secondary_y=True,)

        fig3.update_xaxes(tickangle=45,)

        fig3.update_yaxes(title_text="BM Frequency",secondary_y=False,rangemode = "tozero")
        fig3.update_yaxes(title_text="Menses",secondary_y=True,tickmode = 'array',tickvals=[0,1],ticktext = ["False","True"], )

        #SLEEP DATA ------------------------------------------------------------------------------------------------------
        flt_slp = (dfslp['Date'] >= start_date) & (dfslp['Date'] <= end_date)
        dfslp = dfslp.loc[flt_slp]

        dfslp = dfslp.groupby(['Date'])['Sleep_Hours'].mean().reset_index()

        fig4 = px.line(dfslp,x='Date', y='Sleep_Hours',)
        fig4.update_traces(line=dict(color="#00cc99"))

        return fig, fig2, fig3, fig4

        # ------------------------------------------------------------------------------


# if __name__ == '__main__':
print("\nloading... \n")
dashboard() 
print("\nComplete! \n")
# app.run_server(debug=True)

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(host='10.1.84.77', port=8050)