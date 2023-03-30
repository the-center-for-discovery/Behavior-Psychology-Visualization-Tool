from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

# df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

df  = pd.read_csv('toy_data.csv')
# print(df_test.head())

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                df['Target'].unique(),
                'Aggression',
                id='crossfilter-xaxis-column',
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-xaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df['Target'].unique(),
                'Disruptive',
                id='crossfilter-yaxis-column'
            ),
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
            hoverData={'points': [{'customdata': 'Disruptive'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    # html.Div(dcc.Slider(
    #     df['Date'].min(),
    #     df['Date'].max(),
    #     step=None,
    #     id='crossfilter-Date--slider',
    #     value=df['Date'].max(),
    #     marks={str(Date): str(Date) for Date in df['Date'].unique()}
    # ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
])

@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-yaxis-type', 'value'))
    # Input('crossfilter-Date--slider', 'value'))

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,):
    
    #NOTE; x and y axis 'colum names' need to be set to date and Epidode Count and grouped by Target
    
    # xaxis_column_name = 'Month_Formated'
    print(xaxis_column_name)
    
    # yaxis_column_name = 'Episode_Count'
    print(yaxis_column_name)
    
    # dff = df[df['Date'] == Date_value]
    dff = df
    print(dff[dff['Target'] == xaxis_column_name])
    print(dff[dff['Target'] == yaxis_column_name])

    fig = px.scatter(x=dff[dff['Target'] == xaxis_column_name]['Episode_Count'],
            y=dff[dff['Target'] == yaxis_column_name]['Episode_Count'],
            hover_name=dff[dff['Target'] == yaxis_column_name]['Target']
            )
    print(dff[dff['Target'] == yaxis_column_name]['Target'])
    
    fig.update_traces(customdata=dff[dff['Target'] == yaxis_column_name]['Target'])

    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

def create_time_series(dff, axis_type, title):
    fig = px.scatter(dff, x='Date', y='Episode_Count')
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@app.callback(
    Output('x-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'))
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    # print(hoverData)
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['Target'] == country_name]
    dff = dff[dff['Target'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

@app.callback(
    Output('y-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-yaxis-type', 'value'))
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    dff = df[df['Target'] == hoverData['points'][0]['customdata']]
    dff = dff[dff['Target'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)

if __name__ == '__main__':
    app.run_server(debug=True)