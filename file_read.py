import base64
import datetime
import io
import re

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

import pandas as pd
from read_workbook import *

import pdb

suppress_callback_exceptions=True

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([ # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Store(id='stored-data', storage_type='session'),
    dcc.Store(id='stored-meds-data', storage_type='session'),
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
    html.Div(id='output-div'),
    html.Div(id='output-meds-div'),
    html.Div(id='output-datatable'),
])

def parse_contents(contents, filename, date, store_data, store_meds_data):
    content_type, content_string = contents.split(',')
    
    decoded = base64.b64decode(content_string)
    stored_df = pd.DataFrame(store_data)
    stored_meds_df = pd.DataFrame(store_meds_data)
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
        #run get all meds data to produce medication dataframe
        df_meds = get_all_meds_data(workbook_xl)
        df_meds = pd.concat([stored_meds_df, df_meds])

        #convert episode values to float and aggregate mean per shift 
        df['value'] = df['value'].astype(float)
        dfmean = df.groupby(['Date', 'variable'],sort=False,)['value'].mean().round(2).reset_index()
        dfmean = pd.concat([stored_df, dfmean])
    
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        
        html.H5("Behavior data:"),
        dash_table.DataTable(
            data=dfmean.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in dfmean.columns],
            page_size=15
        ),
        
        html.H5("Medication data:"),
        dash_table.DataTable(
            data=df_meds.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df_meds.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=dfmean.to_dict('records')),
        dcc.Store(id='stored-meds-data', data=df_meds.to_dict('records')),
        
        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('stored-data','data'), 
              State('stored-meds-data','data'))

def update_output(contents, filename, date_modified, store_data, store_meds_data):
    if contents is not None:
        children = [
            parse_contents(contents, filename, date_modified, store_data, store_meds_data)]
        return children


@app.callback(Output('output-div', 'children'),
              Input('stored-data','data'))

def make_graphs(data):
    
    df_agg = pd.DataFrame(data)
    
    # df_agg['Date'] = pd.to_datetime(df_agg['Date'])
    
    if df_agg.empty:
        print("Dataframe epmty")
    else:
        bar_fig = px.bar(df_agg, x=df_agg['Date'], y=df_agg['value'], color = 'variable',barmode='group')
        return dcc.Graph(figure=bar_fig)


@app.callback(Output('output-meds-div', 'children'),
              Input('stored-meds-data','data'))

def make_graphs(data):
    
    df_meds = pd.DataFrame(data)

    df_meds = pd.melt(df_meds, id_vars =['Dose','Units','Medication'])
    df_meds = df_meds.rename(columns = {'value':'Date'})
    df_meds.sort_values(by='Date',inplace=True)
    
    if df_meds.empty:
        print("Dataframe epmty")
    else:
        bar_fig = px.line(df_meds, x='Date', y="Dose", color = "Medication",
                title="Medication Dosages", log_y=True)
        return dcc.Graph(figure=bar_fig)
    
if __name__ == '__main__':
    app.run_server(debug=True)
    
    # app.run_server(host='10.1.183.44', port=8050)