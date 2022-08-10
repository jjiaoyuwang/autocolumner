from dash import Dash, html, dcc, Input, Output, ctx, State
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash('test_app', external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True


app.layout = html.Div([
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2')
    ]),
    html.Div(id='tabs-example-content-1'),
    html.Div(id='test-div-2')
])

@app.callback(
    Output('tabs-example-content-1', 'children'),
    Input('tabs-example-1','value')
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2('Manual operation'),
            html.Div([
                html.H3('Pump control'),
                html.Button('Pump off', id='btn-pump-off'),
                html.Button('Pump on', id='btn-pump-on')
            ]),
            html.Div([
                html.H3('Valve control'),
                html.Button('Vacuum off', id='btn-vac-off'),
                html.Button('Vacuum on', id='btn-vac-on'),
                html.Button('Close sep funnel', id='btn-sep-off'),
                html.Button('Open sep funnel', id='btn-sep-on')
            ])
        ])

@app.callback(
    Output('tab-1', 'active_tab'),
    Input('btn-pump-off', 'n_clicks'),
    Input('btn-pump-on', 'n_clicks'),
    Input('btn-vac-off', 'n_clicks'),
    Input('btn-vac-on', 'n_clicks'),
    Input('btn-sep-off', 'n_clicks'),
    Input('btn-sep-on', 'n_clicks')
)
def runScript(btn1, btn2, btn3, btn4, btn5, btn6):
    button_clicked = ctx.triggered_id
    app.logger.debug(button_clicked)
    print('Button clicked')
    if button_clicked == 'btn-pump-off':
        app.logger.info('Pump was turned off')
        app.logger.debug('Pump was turned off')
        print('Pump was turned off')
    elif button_clicked == 'btn-pump-on':
        print('Pump was turned on')
    elif button_clicked == 'btn-vac-off':
        print('Vacuum was turned off')
    elif button_clicked == 'btn-vac-on':
        print('Vacuum was turned on')
    elif button_clicked == 'btn-sep-off':
        print('Sep funnel was closed')
    elif button_clicked == 'btn-sep-on':
        print('Sep funnel was opened')


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
