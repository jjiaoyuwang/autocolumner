from email import message
from email.mime import image
from gc import callbacks
from turtle import ht, position, width
# from tkinter.ttk import Style
from dash import Dash, html, dcc, Input, Output, ctx, State,dash_table,no_update
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
from PIL import Image
import cv2
import os
import sys
import numpy as np
import plotly.express as px
import json
from matplotlib import pyplot as plt

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(__dir__, '../')))

from cv_method import calibration
from cv_method.detector import find_spots

# external_stylesheets = ['assets/codepen_stylesheet.css']
app = Dash('Auto Columner') #, external_stylesheets=external_stylesheets)
#app.config.suppress_callback_exceptions = True

# Variables for tracking machine state ---------------------------
start_time=time.time()
sequence_in_progress=False;
arm_pos=1;#the position of arm
Min_armpos=1;##the min of arm position
Max_armpos=10;##the max of arm position. todo: calculate from sequence parameters?
pump1=False;
pump2=False;
vacuum=False;
sep_funnel=False;
sequence_volumes = [] 
sequence_gradients = []

status_message = "placeholder status message"
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

fig = px.imshow(cv2.imread("./blank.png"))

app.layout = html.Div([
    dcc.Tabs(id='Main_Tabs', value='setup', mobile_breakpoint=0, children=[
        dcc.Tab(id='setup', label='Setup', value='setup', children=html.Div([
            dcc.Upload(
                # id='upload-params',
                html.A('Upload Parameters'),
                id='upload-params',
                className='file-upload',
            ),
            html.H2('Fractions'),
            html.Div([
                dash_table.DataTable(
                    id='params_table'
                ),
            ],className="container"),
            
            html.Button('start',id='startclick',n_clicks=0,style={'height':'2em','width':'90%','margin-left':'5%','margin-top':'10px','font-size':'2em'}),
        ])),
        dcc.Tab(id='monitor',label='Monitor', value='monitor',children=html.Div([
            html.H3('Fraction #:', id="messageoffraction"),
            #dcc.Markdown(f'''{message_fraction}''',id="messageoffraction"),
            html.Hr(),
            html.H3('Time Elapsed:', id="messageoftime"),
            html.Hr(),
            html.H3('Volume Dispensed:',id="volume_display"),
            html.Hr(),
            html.H3('Status:'),
            # status message in smaller font, below "Status:" heading
            dcc.Markdown(f'''{status_message}''',id="mntr_status_message"),
            html.Hr(),
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
            daq.BooleanSwitch(id='pump1',on=False,label='Pump 1'),
            html.Hr(),
            daq.BooleanSwitch(id='pump2',on=False,label='Pump 2'),
            html.Hr(),
            daq.BooleanSwitch(id='vacuum',on=False,label='Vacuum'),
            html.Hr(),
            daq.BooleanSwitch(id='sep_funnel',on=False,label='Sep. Funnel'),
            html.Hr(),
            html.Div(id='one'),#the 'one' to 'four' have no use, just because every callback need a output
            html.Div(id='two'),
            html.Div(id='three'),
            html.Div(id='four'),
            # trying to position the arm control buttons all at once
            html.Div(id='arm_controls_div', children=[
                html.Div(id='the arm message'),
                html.Button('|<', id='smallest', n_clicks=0),
                html.Button('<', id='smaller', n_clicks=0),
                html.Button('>', id='bigger', n_clicks=0),
                html.Button('>|', id='biggest', n_clicks=0),
            ], style={'text-align':'center'}),
            html.Div(id='testhardware'),
        ])
        ),
        dcc.Tab(id='tlc',label='TLC', value='tlc',children=html.Div([
            dcc.Upload(
                id='upload-image',
                className='file-upload',
                children=html.Div([
                    'Drag and Drop or ',
            html.A('Select Files')
                ]),
                # html.A('Select Files'),
                # id='upload-image',
                style={
                'width':'80%',
                'height':'60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                # 'didplay':
                # 'margin-left': '100px',
                'margin-top':'10px',
                'vertical-align':'middle',
            },
            multiple=True
            ),
            html.Button('Delete',id='delete_img',n_clicks=0),
            html.Div(id='output-image-upload'),
            html.Button('Automatic Outputs', id='auto',n_clicks=0),
            html.Button('Semi-Automatic Outputs',id='semi',n_clicks=0),
            html.Div(id='auto_result'),
            html.Div(id='semi_result')
            # html.Div(id='graph_display'),
            # dcc.Graph(id="graph-picture", figure=fig),
            # html.Pre(id="annotations-data")
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


@app.callback(Output('params_table', 'data'),
              Output('params_table', 'columns'),
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
    global sequence_volumes;
    if sequence_in_progress:
        cur_f_str = get_cur_fraction_msg(arm_pos,len(sequence_volumes));
    else:
        cur_f_str = get_cur_fraction_msg(0,0);
    return cur_f_str;

def get_cur_fraction_msg(cur_fraction, last_fraction):
    return "Fraction #: {:0}/{:1}".format(cur_fraction, last_fraction);

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
    so_far_vol = sum(sequence_volumes[:arm_pos-1]);
    final_vol = sum(sequence_volumes);
    return get_vol_msg(so_far_vol, final_vol);

def get_vol_msg(so_far_vol, final_vol):
    return "Volume Dispensed: {:0}/{:1} mL".format(so_far_vol, final_vol);

# update current status message
    # edit the global variable status_message
    # and this will update the page to match that later
@app.callback(
    Output("mntr_status_message", "children"),
    Input('interval-component', 'n_intervals'),
    Input('Main_Tabs', 'value'),
    )
def update_status_display(on, tab):
    global status_message;
    return status_message;

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
    msg='Arm at #'+str(hardware_arm.position);
    return html.Div(msg);



# TLC Tab callbacks -------------------------------------------

@app.callback(Output('output-image-upload', 'children'),
            #   Output('annotations-data','show_data'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'),
              Input('delete_img','n_clicks'),
            #   Input("graph-picture", "relayoutData"),
              prevent_initial_call=True,)
def update_image(list_of_contents, list_of_names, list_of_dates, n_clicks):
    config = {
        "modeBarButtonsToAdd": [
            "drawline",
            "drawopenpath",
            "drawclosedpath",
            "drawcircle",
            "drawrect",
            "eraseshape",
        ]
    }

    # show_data = no_update
    if "delete_img" == ctx.triggered_id:
        os.remove("./assets/cal.png")
        children = []
        # return children,show_data
        return children

    if list_of_contents is not None:
        if not os.path.exists("./assets/cal.png"):
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
                content_type, content_string = c.split(',')
                decoded = base64.b64decode(content_string)
                img = cv2.imdecode(np.array(bytearray(decoded),dtype='uint8'),cv2.IMREAD_UNCHANGED)
                solved_img = calibration.calibrate(img)
                cv2.imwrite("./assets/cal.png",solved_img)
                children = [
                    html.Div([
                    html.H5(n),
                    html.H6(datetime.datetime.fromtimestamp(d)),
                    html.Img(src=c),
                    html.Img(src=app.get_asset_url('cal.png')),
                    html.Hr(),
                    dcc.Graph(figure=px.imshow(cv2.imread("./assets/cal.png")),config=config),
                    ])
                ]
        else:
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates):
                children = [
                    html.Div([
                    html.H5(n),
                    html.H6(datetime.datetime.fromtimestamp(d)),
                    html.Img(src=c),
                    html.Img(src=app.get_asset_url('cal.png')),
                    html.Hr(),
                    dcc.Graph(figure=px.imshow(cv2.imread("./assets/cal.png")),config=config),
                    ])
                ]
    # if "shapes" in relayoutData:
    #     show_data =  json.dumps(relayoutData["shapes"], indent=2)
        # return children,show_data
        return children

@app.callback(Output('auto_result','children'),
            Input('auto','n_clicks'))
def auto_result(n_clicks):
    children = []
    if n_clicks != 0 and os.path.exists("./assets/cal.png"):
        img = cv2.imread("./assets/cal.png")
        P,rfs = find_spots(img)
        dst = img.copy()
        for o in P:
            cv2.drawMarker(img=dst, position=(int(o[0]), int(o[1])), color=(0, 0, 255), markerType=cv2.MARKER_CROSS)
        # plt.imshow(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)), plt.show()
        cv2.imwrite("./assets/auto.png",dst)
        children = [
            html.Img(src="./assets/auto.png")
        ]
    return children

# --------------------------------------------------


if __name__ == '__main__':
    # run server with only internal connections allowed
    app.run_server(debug=True, port=8050)

    # run server with external connections allowed
    # app.run_server(host="0.0.0.0", debug=True, port=8050)