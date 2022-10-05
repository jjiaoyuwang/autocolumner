from email import message
from gc import callbacks
from turtle import position, width
# from tkinter.ttk import Style
from dash import Dash, html, dcc, Input, Output, ctx, State,dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq
import datetime
import time
import pump
import vacuum_hardware
import sepfunnel
import arm
import pandas as pd
import io
import base64

# external_stylesheets = ['assets/codepen_stylesheet.css']
app = Dash('Auto Columner') #, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True

# Variables for tracking machine state ---------------------------
start_time=time.time()
sequence_in_progress=False;
arm_pos=0;#the position of arm
Min_armpos=0;##the min of arm position
Max_armpos=10;##the max of arm position. todo: calculate from sequence parameters?
pump1=False;
pump2=False;
vacuum=False;
sep_funnel=False;
sequence_volumes = [] 
sequence_gradients = []
#---------------------------------------------------------------

hardware_pump1=pump.Pump("1");
hardware_pump2=pump.Pump("2");
hardware_vacuum=vacuum_hardware.Vacuum("3");
hardware_sep=sepfunnel.Sepfunnel("4");
hardware_arm=arm.Arm("5",arm_pos);

message_fraction= "Fraction: {:0}/{:1}".format(0, 0);
timing_message="Time: 00:00:00";
volume_str="Volume: 0/0 mL";

button_buttom={}
tab3_switch={}

app.layout = html.Div([
    dcc.Tabs(id='Main_Tabs', value='setup', mobile_breakpoint=0, children=[
        dcc.Tab(id='setup', label='Setup', value='setup', children=html.Div([
            # html.H2('Fractions'),
            #html.Div([
            dcc.Upload(
                # id='upload-params',
                html.A('Upload Parameters'),
                id='upload-params',
                className='file-upload',
            ),
            html.H2('Fractions'),
            dash_table.DataTable(
                id='dataset'
            ),
            #],className="container"),

            # html.Br(),
            # html.Table([
            #     html.Th([html.Td("Volume"), html.Td("Gradient")]),
            #     html.Tr([
            #         html.Td(
            #             dcc.Input(
            #                 id="fra1_v",
            #                 type="number",
            #                 value=None,
            #                 style={
            #                 'width':'60px'}),
            #             ),
            #         html.Td(
            #             dcc.Input(
            #             id="fra1_g",
            #             type="number",
            #             value='',
            #             style={
            #             'width':'60px',
            #             'margin-left':'-90px'})
            #             )
            #     ]),
            # ])
            
            html.Button('start',id='startclick',n_clicks=0),
        ])),
        dcc.Tab(id='monitor',label='Monitor', value='monitor',children=html.Div([
            html.H2(id='Fraction ratio'),
            dcc.Markdown(f'''{message_fraction}''',id="messageoffraction"),
            dcc.Markdown(f'''{timing_message}''',id="messageoftime"),
            dcc.Markdown(f'''{volume_str}''',id="volume_display"),
            html.H2(id='timing'),
            # pause and stop buttons removed until backend can support them
            # html.Button('Pause', id='pause-click', n_clicks=0, disabled=True),
            # html.Button('Stop', id='stop-click', n_clicks=0, disabled=True),
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
            html.Div(id='one'),#the 'one' to 'four' have no use, just because every callback need a output
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
        dcc.Tab(id='tlc',label='TLC', value='tlc',children=html.Div([
            dcc.Upload(
                # id='upload-image',
                html.A('Select Files'),
                id='upload-image',
                className='file-upload',
            multiple=True
            ),
            html.Div(id='output-image-upload'),
        ])
        )
    ])
])

# Setup Tab Callbacks ------------------------------
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))


@app.callback(Output('dataset', 'data'),
              Output('dataset', 'columns'),
              Input('upload-params', 'contents'),
              State('upload-params', 'filename'))
def update_output(contents, filename):
    volume = []
    gradient = []
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    # for i in df.columns:
    #     print({"name": i, "id": i})
        # volume.append(i[0])
        # gradient.append(i[1])
    # print(volume)
    # print(gradient)
    for i in df.to_dict('records'):
        volume.append(i['volume'])
        gradient.append(i['gradient'])
    print(volume)
    print(gradient)
    global sequence_volumes
    sequence_volumes = volume
    global sequence_gradients
    sequence_gradients = gradient
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

# Run Button
@app.callback(
    Output('Main_Tabs','value'),
    Input('startclick','n_clicks'),
    State('Main_Tabs','value')
    )
def start_tab(btn1,cur_tab):
    global sequence_in_progress;
    global start_time;
    if "startclick"== ctx.triggered_id and sequence_in_progress==False:
        sequence_in_progress=True;
        start_time = time.time();
        return 'monitor';
    else:
        # this part of the callback is so that Dash's
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
    Input('Main_Tabs', 'value'),
    )
def updatetiming(on, tab):
    global start_time;
    global sequence_in_progress;
    # not sure timing_message needs to be global
    global timing_message;
    if sequence_in_progress==True:
        cur_time = time.gmtime(time.time() - start_time);
        cur_time = time.strftime("%H:%M:%S",cur_time)
        timing_message = "Time: " + cur_time;
    return timing_message;

# update current fraction display
    # IMPORTANT: you cannot call a function to update the display
    # you need to change the global variable 'arm_pos'
    # and this will update the display to match next time the timer changes
@app.callback(
    Output("messageoffraction", "children"),
    Input('interval-component', 'n_intervals'),
    Input('Main_Tabs', 'value'),
    )
def update_fraction_display(on, tab):
    global arm_pos;
    if sequence_in_progress:
        cur_f_str = get_cur_fraction_msg(arm_pos, Max_armpos);
    else:
        cur_f_str = get_cur_fraction_msg(0,0);
    return cur_f_str;

def get_cur_fraction_msg(cur_fraction, last_fraction):
    return "Fraction: {:0}/{:1}".format(cur_fraction, last_fraction);

# update current volume dispensed display
    # like with fraction display
@app.callback(
    Output("volume_display", "children"),
    Input('interval-component', 'n_intervals'),
    Input('Main_Tabs', 'value'),
    )
def update_volume_display(on, tab):
    global sequence_in_progress;
    global arm_pos;
    if not sequence_in_progress:
        return get_vol_msg(0,0)
    global sequence_volumes;
    so_far_vol = sum(sequence_volumes[:arm_pos]);
    final_vol = sum(sequence_volumes);
    return get_vol_msg(so_far_vol, final_vol);

def get_vol_msg(so_far_vol, final_vol):
    return "Volume Dispensed: {:0}/{:1} mL".format(so_far_vol, final_vol);

# IMPORTANT: stop button and pause button functionality delayed until backside multithreading is implemented.
# stop the run when STOP button pressed
    # close all peripherals
    # stop arm movement
    # reset time
    # reset volume
    # change pause button to RUN button
#@app.callback(
#    Output('stop-click','disabled'),
#    Input('stop-click','n_clicks'),
#    )
#def stop(btn1):
#    global sequence_in_progress;
#    if "stop-click"==ctx.triggered_id:
#        sequence_in_progress=False;
#        return True;
#    return False;

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
    if "smallest" == ctx.triggered_id:# turn the arm to the min position
        print(hardware_arm.tomin());
        arm_pos=Min_armpos;##this can be delete if use arm.py
    elif "smaller"== ctx.triggered_id and arm_pos>Min_armpos:
        print(hardware_arm.smaller());
        arm_pos=arm_pos-1;##this can be delete if use arm.py
    elif "bigger"==ctx.triggered_id and arm_pos<Max_armpos:
        print(hardware_arm.bigger());
        arm_pos=arm_pos+1;##this can be delete if use arm.py
    elif "biggest"==ctx.triggered_id:#turn the arm to the max position
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