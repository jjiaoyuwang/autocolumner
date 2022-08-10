# dash app frontend for automated dry column vacuum chromatography
from dash import dcc, html, Dash
from dash.dependencies import Input, Output

app = Dash('Automated DCVC')

app.layout = html.Div([
    dcc.Tabs(id='tab-ctrls', value='tab-pump', children=[
        dcc.Tab(label='Pump Control', value='tab-pump'),
        dcc.Tab(label='Valve Control', value='tab-valves'),
        dcc.Tab(label='Robotic Arm Control', value='tab-arm')
    ]),
    html.Div(id='tabs-ctrl-content')
])

@app.callback(
    Output('tabs-ctrl-content', 'children'),
    Input('tab-ctrls', 'value'),
    Input('pump1-on', 'n_clicks')
)
def render_content(tab):
    if tab == 'tab-pump':
        return html.Div([
            html.H3('Pump Control'),
            html.Button('Pump 1 (non-polar) on', id='pump1-on')
        ])
    elif tab == 'tab-valves':
        pass
    elif tab == 'tab-arm':
        pass
def pump1_on()

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)