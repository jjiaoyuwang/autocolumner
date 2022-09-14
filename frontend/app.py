from dash import Dash, html, dcc, Input, Output, ctx, State
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash('test_app', external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1', children=html.Div([
            html.H2('Manual operation'),
            html.Div([
                html.H3('Pump control'),
                html.Button('Pump off', id='btn-pump-off',n_clicks=0),
                html.Button('Pump on', id='btn-pump-on',n_clicks=0),
            ]),
            html.Div([
                html.H3('Valve control'),
                html.Button('Vacuum off', id='btn-vac-off',n_clicks=0),
                html.Button('Vacuum on', id='btn-vac-on',n_clicks=0),
                html.Button('Close sep funnel', id='btn-sep-off',n_clicks=0),
                html.Button('Open sep funnel', id='btn-sep-on',n_clicks=0),
                html.Div(id='container-button-timestamp')
            ])
        ])),
        dcc.Tab(label='Tab two', value='tab-2')
    ]),
    html.Div(id='tabs-example-content-1'),
    html.Div(id='test-div-2')
])

@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-pump-off', 'n_clicks'),
    Input('btn-pump-on', 'n_clicks'),
    Input('btn-vac-off', 'n_clicks'),
    Input('btn-vac-on', 'n_clicks'),
    Input('btn-sep-off', 'n_clicks'),
    Input('btn-sep-on', 'n_clicks'),
)

def displayClick(btn1,btn2,btn3, btn4,btn5,btn6):
    msg = ""
    if "btn-pump-off" == ctx.triggered_id:
        msg = "Pump off"
    elif "btn-pump-on" == ctx.triggered_id:
        msg = "Pump on"
    elif "btn-vac-off" == ctx.triggered_id:
        msg = "Vacuum off"
    elif "btn-vac-on" == ctx.triggered_id:
        msg = "Vacuum on"
    elif "btn-sep-off" == ctx.triggered_id:
        msg = "Close sep funnel"
    elif "btn-sep-on" == ctx.triggered_id:
        msg = "open sep funnel"
    return html.Div(msg)

if __name__ == '__main__':
    # run server with only internal connections allowed
    # app.run_server(debug=True, port=8050)

    # run server with external connections allowed
    app.run_server(host="0.0.0.0", debug=True, port=8050)
