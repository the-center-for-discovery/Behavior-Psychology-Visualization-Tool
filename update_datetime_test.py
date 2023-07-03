import datetime
import dash
from dash import html

app = dash.Dash()

def serve_layout():
    return html.H1('The time is: ' + str(datetime.datetime.now()))

app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=True)