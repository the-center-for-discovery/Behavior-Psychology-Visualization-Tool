from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px
from read_workbook import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

df = get_all_months_int_dur("data/DP Beh Data 2022-23.xlsm")

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-xaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-yaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'label': 'no data'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),
])

@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-xaxis-type', 'value'))
def update_graph(xaxis_type):
    df['value'] = df['value'].astype(float)
    dfmean = df.groupby(['Date', 'variable'],sort=False,)['value'].mean().round(2).reset_index()
    df_agg = dfmean
    bar_fig = px.bar(df_agg, x=df_agg['Date'], y=df_agg['value'], color = 'variable',barmode='group')
    return bar_fig

def create_time_series(dff):
    fig = px.scatter(dff['value'])

    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text="title")
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@app.callback(
    Output('x-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'))
def update_y_timeseries(hoverData):
    print(hoverData)
    date = hoverData['points'][0]['label']
    print(date)
    #dff = df[df['Country Name'] == country_name]
    #dff = dff[dff['Indicator Name'] == xaxis_column_name]
    #title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(df)

@app.callback(
    Output('y-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'))
def update_x_timeseries(hoverData):
    #dff = df[df['Country Name'] == hoverData['points'][0]['customdata']]
    #dff = dff[dff['Indicator Name'] == yaxis_column_name]
    return create_time_series(df)

if __name__ == '__main__':
    app.run_server(debug=True)