from email import message
from gc import callbacks
from turtle import position
# from tkinter.ttk import Style
from dash import Dash, html, dcc, Input, Output, ctx, State
import dash_bootstrap_components as dbc
import dash_daq as daq
import datetime
import time
import pump
import vacuum_hardware
import sepfunnel
import arm

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash('test_app', external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True

# Variables for tracking machine state ---------------------------
start_time=time.time()
start_machine=False;
switch_start=0;
arm_pos=0;
Min_armpos=0;##the min of arm position
Max_armpos=10;##the max of arm position
pump1=False;
pump2=False;
vacuum=False;
sep_funnel=False;
#---------------------------------------------------------------

hardware_pump1=pump.Pump("1");
hardware_pump2=pump.Pump("2");
hardware_vacuum=vacuum_hardware.Vacuum("3");
hardware_sep=sepfunnel.Sepfunnel("4");
hardware_arm=arm.Arm("5");

data_fraction=6;
message_fraction="Fraction:"+str(data_fraction)+"/10";

timing_message="Time: 00:00:00";

button_buttom={}
tab3_switch={}

app.layout = html.Div([
    dcc.Tabs(id='Main_Tabs', value='setup', mobile_breakpoint=0, children=[
        dcc.Tab(id='setup', label='Setup', value='setup', children=html.Div([
            html.H2('Fractions'),
            html.Button('start',id='startclick',n_clicks=0),
        ])),
        dcc.Tab(id='monitor',label='Monitor', value='monitor',children=html.Div([
            dcc.Interval(id='interval1', interval=0.5* 1000, n_intervals=0),
            html.H2(id='Fraction ratio'),
            dcc.Markdown(f'''{message_fraction}''',id="messageoffraction"),
            dcc.Markdown(f'''{timing_message}''',id="messageoftime"),
            html.H2(id='timing'),
            html.Button('Pause', id='pause-click', n_clicks=0),
            html.Button('Stop', id='stop-click', n_clicks=0),
            dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0)
        ])
        ),
        dcc.Tab(id='debug',label='Debug', value='debug',children=html.Div([
            daq.BooleanSwitch(id='pump1',on=False,label='pump1',style=tab3_switch),
            daq.BooleanSwitch(id='pump2',on=False,label='pump2',style=tab3_switch),
            daq.BooleanSwitch(id='vacuum',on=False,label='vacuum',style=tab3_switch),
            daq.BooleanSwitch(id='sep_funnel',on=False,label='sep_funnel',style=tab3_switch),
            html.Div(id='one'),
            html.Div(id='two'),
            html.Div(id='three'),
            html.Div(id='four'),
            html.Div(id='the arm message'),
            html.Button('|<', id='smallest', n_clicks=0),
            html.Button('<', id='smaller', n_clicks=0),
            html.Button('>', id='bigger', n_clicks=0),
            html.Button('>|', id='biggest', n_clicks=0),
            html.Div(id='testhardware'),
        ])
        ),
        dcc.Tab(id='tlc',label='TLC', value='tlc'
        )
    ])
])

# Setup Tab Callbacks ------------------------------

# Run Button
@app.callback(
    Output('Main_Tabs','value'),
    Input('startclick','n_clicks'),
    State('Main_Tabs','value')
    )
def start_tab(btn1,cur_tab):
    global start_machine;
    if "startclick"== ctx.triggered_id and start_machine==False:
        start_machine=True;
        state_time = time.time();
        return 'monitor';
    else:
        # this part of the callback is so that
        # periodic callback refreshing doesn't change tabs
        return cur_tab;

# --------------------------------------------------


# Monitor Tab Callbacks ----------------------------

# update time elapsed
    # todo: change to using a clientside callback for performance
    # make sure to sync the client's displayed time with the serverside time every couple minutes.
@app.callback(
    Output('messageoftime','children'),
    Input('interval-component', 'n_intervals'),
    # todo: make it update when Monitor tab is selected
    )
def updatetiming(on):
    global start_time;
    global start_machine;
    global switch_start;
    # not sure timing_message needs to be global
    global timing_message;
    if start_machine==True:
        cur_time = time.gmtime(time.time() - start_time);
        cur_time = time.strftime("%H:%M:%S",cur_time)
        timing_message = "Time: " + cur_time;
    return timing_message;

# update current fraction #
    # (maybe implement as a function to call from the backend)

# update current volume dispensed display
    # (again, a functiont to call from the backend)


# stop the run when STOP button pressed
    # close all peripherals
    # stop arm movement
    # reset time
    # reset volume
    # change pause button to RUN button
@app.callback(
    Output('pump1','on'),
    Input('stop-click','n_clicks'),
    Input('pause-click','n_clicks'))
def stop(btn1,btn2):
    global pump1;
    global start_machine;
    global switch_start;
    if "stop-click"==ctx.triggered_id or "pause-click"==ctx.triggered_id:
        start_machine=False;##stop machine
        switch_start=0;
        pump1=False;
        on=False;
    return pump1;

# pause the run when PAUSE button pressed
    # stop arm movement
    # close all peripherals
    # pause time
    # pause volume
    # pause fraction number
    # change pause button to RESUME button
# resume the run when RESUME button pressed
    # complete arm movement
    # open relevant peripherals
    # unpause time
    # unpause volume
    # unpause fraction number
    # change resume button to PAUSE button (perhaps implement as 2 buttons that hide when unavailable?)
# currently not having pause/resume button change to be a RUN button.
# we can implement that in the future if requested.


# ----------------------------------------------------------

##tab debug
@app.callback(
    Output('one','children'),
    Input('pump1','on'),)
def pump1run(on):
    global pump1;
    if on is True:
        pump1=True;
        print(hardware_pump1.on());
    elif on is False:
        pump1=False;
        print(hardware_pump1.off());
    msg='pump1 is '+str(pump1)+',pump2 is '+str(pump2)+',vacuum is '+str(vacuum)+',sep funnel is '+str(sep_funnel);
    print(msg);


@app.callback(
    Output('two','children'),
    Input('pump2','on'),)
def pump2run(on):
    global pump2;
    if on is True:
        pump2=True;
        print(hardware_pump2.on());
    elif on is False:
        pump2=False;
        print(hardware_pump2.off());
    msg='pump1 is '+str(pump1)+',pump2 is '+str(pump2)+',vacuum is '+str(vacuum)+',sep funnel is '+str(sep_funnel);
    print(msg); 

@app.callback(
    Output('three','children'),
    Input('vacuum','on'),)
def vacuumrun(on):
    global vacuum;
    if on is True:
        vacuum=True;
        print(hardware_vacuum.on());
    elif on is False:
        vacuum=False;
        print(hardware_vacuum.off());
    msg='pump1 is '+str(pump1)+',pump2 is '+str(pump2)+',vacuum is '+str(vacuum)+',sep funnel is '+str(sep_funnel);
    print(msg); 

@app.callback(
    Output('four','children'),
    Input('sep_funnel','on'),)
def sepfunnelrun(on):
    global sep_funnel;
    if on is True:
        sep_funnel=True;
        print(hardware_sep.on());
    elif on is False:
        sep_funnel=False;
        print(hardware_sep.off())
    msg='pump1 is '+str(pump1)+',pump2 is '+str(pump2)+',vacuum is '+str(vacuum)+',sep funnel is '+str(sep_funnel);
    print(msg); 

@app.callback(
    Output('the arm message','children'),
    Input('smallest','n_clicks'),
    Input('smaller', 'n_clicks'),
    Input('bigger', 'n_clicks'),
    Input('biggest', 'n_clicks'),)
def arm_run(btn1,btn2,btn3,btn4):
    global arm_pos;
    global Min_armpos;
    global Max_armpos;
    if "smallest" == ctx.triggered_id:
        print(hardware_arm.tomin());
        arm_pos=Min_armpos;##this can be delete if use arm.py
    elif "smaller"== ctx.triggered_id and arm_pos>Min_armpos:
        print(hardware_arm.smaller());
        arm_pos=arm_pos-1;##this can be delete if use arm.py
    elif "bigger"==ctx.triggered_id and arm_pos<Max_armpos:
        print(hardware_arm.bigger());
        arm_pos=arm_pos+1;##this can be delete if use arm.py
    elif "biggest"==ctx.triggered_id:
        print(hardware_arm.tomax());
        arm_pos=Max_armpos;##this can be delete if use arm.py
    ##msg='arm at #'+str(arm_pos);
    msg='arm at #'+str(hardware_arm.position);
    return html.Div(msg);

if __name__ == '__main__':
    # run server with only internal connections allowed
    app.run_server(debug=True, port=8050)

    # run server with external connections allowed
    # app.run_server(host="0.0.0.0", debug=True, port=8050)
