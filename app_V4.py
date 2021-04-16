import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
# import plotly
import plotly.express as px
# import plotly.graph_objs as go
# import plotly.io as pio
import os
# import psutil
# import requests
import tkinter
from tkinter import filedialog
from skimage import io
# from skimage import data
import json
import fnmatch
import copy

# from skimage import io as skio

'''
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
'''

external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/segmentation-style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.title = "Interactive image segmentation based on machine learning"
DEBUG = False

# -------------------- CONFIGURATION ------------------------
DEFAULT_IMAGE_PATH = "assets/images"
DEFAULT_STROKE_WIDTH = 4  # gives line width of 2^3 = 8

DEFAULT_LABEL_CLASS = 0
NUM_LABEL_CLASSES = 6
class_label_colormap = ["#cb4335", "#e67e22", "#5dade2", "#76d7c4", "#f7dc6f", "#bfc9ca"]
class_labels = list(range(NUM_LABEL_CLASSES))
assert NUM_LABEL_CLASSES <= len(class_label_colormap)  # we can't have less colors than classes

# --------------------- Functions -------------------------------
filelist = []
for (dirpath, dirnames, filenames) in os.walk(os.path.join(os.getcwd(), DEFAULT_IMAGE_PATH), topdown=False):
    for name in filenames:
        if fnmatch.fnmatch(name, '*.jpg'):
            filelist.append(os.path.join(os.getcwd(), dirpath, name))


def class_to_color(n):
    return class_label_colormap[n]


def make_default_figure(
        images=filelist[0],
        stroke_color=class_to_color(DEFAULT_LABEL_CLASS),
        stroke_width=int(round(2 ** (DEFAULT_STROKE_WIDTH))),
        shapes=[],
):
    fig = px.imshow(io.imread(images))
    fig.update_layout(
        dragmode="drawclosedpath",
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        shapes=shapes,
        newshape=dict(
            line_color=stroke_color,
            line_width=stroke_width,
            opacity=0.5,
            fillcolor= stroke_color,

        )
    )
    return fig


# region ###################### HEADER TAB ###################################

# Open the readme for use in the context info
with open("assets/About.md", "r") as f:
    # Using .read rather than .readlines because dcc.Markdown
    # joins list of strings with newline characters
    About = f.read()

# About Button
button_about = dbc.Button(
    "About",
    id="About-open",
    outline=True,
    color="secondary",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

# POP up Modal
modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown(About, id="About-md")])),
        dbc.ModalFooter(dbc.Button("Close", id="About-close", className="About-bn", )),
    ],
    id="modal",
    size="lg",
    style={"font-size": "small"},
)

header_tab = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            html.Img(
                                id="logo",
                                src=app.get_asset_url("/images/Logo_upc.png"),
                                height="50px",
                            ),
                            href="https://upc.edu",
                        ),
                        md="auto",
                    ),
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H3("Cell Annotation APP"),
                                    html.P("Dysplasic Cells"),
                                ],
                                id="app-title",
                            )
                        ],
                        md=True,
                        align="center",
                    ),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                        dbc.NavItem(button_about)
                                    ],
                                    className="ml-auto",
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),
                            modal_overlay,
                        ],
                        md=2,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="dark",
    sticky="top",
    className="mb-5",
)


# ------------------- CALLBACKS --------------------------
@app.callback(
    Output("modal", "is_open"),
    [Input("About-open", "n_clicks"), Input("About-close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# endregion
# region###################### IMAGE TAB ####################################
image_tab = [
    dbc.Card(
        id="segmentation-card",
        children=[
            dbc.CardHeader("Viewer"),
            html.Div(id='output-1'),
            html.Div(id='show-image-name'),
            dbc.CardBody(
                [
                    # Wrap dcc.Loading in a div to force transparency when loading
                    html.Div(
                        id="transparent-loader-wrapper",
                        children=[
                            dcc.Loading(
                                id="segmentations-loading",
                                type="circle",
                                children=[
                                    # Graph
                                    dcc.Graph(
                                        id="graph",
                                        figure=make_default_figure(),
                                        config={
                                            "modeBarButtonsToAdd": [
                                                #"drawrect",
                                                "drawopenpath",
                                                "drawclosedpath",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "toImage",
                                                "toggleSpikelines",
                                                "autoScale2d",
                                                "zoomInGeo",
                                                "zoomOutGeo",
                                                "toggleHover",
                                                "hoverClosestCartesian",
                                                "hoverCompareCartesian",
                                                "zoomIn2d",
                                                "zoomOut2d"
                                            ],
                                        },
                                        style={"height": "70vh"},
                                    ),
                                ],
                            )
                        ],
                    ),
                ]
            ),

        ],
    )
]

# endregion
# region ###################### TOOLS TAB ####################################

tools_tab = [
    dbc.Card(
        # id="sidebar-card",
        children=[
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Cell condition:",
                                      style={"font-weight": "bold", 'margin-left': 15, "font-size": "larger"}),
                            dcc.RadioItems(
                                id="cell-condition",
                                options=[
                                    {'label': 'Dysplastic', 'value': 'DYSPLASTIC','disabled':True},
                                    {'label': 'Healthy', 'value': 'HEALTHY','disabled':True},
                                ],
                                value='HEALTHY',
                                labelStyle={'display': 'inline-block', 'margin-left': 15},
                                style={"font-size": "larger", "font-weight": "lighter", 'margin-left': 20},

                            ),
                        ], row=True,
                    ),

                    html.Hr(),

                    dbc.Row(
                        children=[
                            dbc.Col(dbc.Label("Indicator", style={"font-weight": "bold", 'text-align': 'center'}),
                                    md=8),
                            dbc.Col(dbc.Label("Priority", style={"font-weight": "bold", 'text-align': 'center'}), md=4),
                        ],
                    ),

                    dbc.Label("State of the Cytoplasm"),
                    # Label class chosen with buttons
                    dbc.Row(
                        children=[
                            dbc.Col(
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Transparent",
                                            id="transparent-button",
                                            outline=True,
                                            disabled=True,
                                            style={"background-color": class_to_color(0)}
                                        ),
                                        dbc.Button(
                                            "Granular",
                                            id="granular-button",
                                            outline=True,
                                            disabled=True,
                                            style={"background-color": class_to_color(1)}
                                        ),
                                    ],
                                    size="md",
                                    style={"width": "100%", 'margin-left': 20},
                                ),
                                md=8,
                                align='center',
                            ),
                            dbc.Col(
                                dcc.RadioItems(
                                    id="priority-cytoplasm",
                                    options=[
                                        {'label': '0', 'value': 0,'disabled':True},
                                        {'label': '1', 'value': 1,'disabled':True},
                                        {'label': '2', 'value': 2,'disabled':True},
                                        {'label': '3', 'value': 3,'disabled':True},
                                    ],
                                    value=0,
                                    labelStyle={'display': 'inline-block', 'margin-left': 15},
                                ),
                                md=4,
                                align='center',
                            ),
                        ],
                    ),
                    dbc.Label("Chromatin aspect"),
                    # Label class chosen with buttons
                    dbc.Row(
                        children=[
                            dbc.Col(
                                dbc.ButtonGroup(
                                    [
                                        dbc.Button(
                                            "Heterogenic",
                                            id="heterogenic-button",
                                            outline=True,
                                            disabled=True,
                                            style={"background-color": class_to_color(2)}
                                        ),
                                        dbc.Button(
                                            "Homogenic",
                                            id="homogenic-button",
                                            outline=True,
                                            disabled=True,
                                            style={"background-color": class_to_color(3)}
                                        ),
                                    ],
                                    size="md",
                                    style={"width": "100%", 'margin-left': 20},
                                ),
                                md=8,
                                align='center',
                            ),
                            dbc.Col(
                                dcc.RadioItems(
                                    id="priority-chromatin",
                                    options=[
                                        {'label': '0', 'value': 0,'disabled':True},
                                        {'label': '1', 'value': 1,'disabled':True},
                                        {'label': '2', 'value': 2,'disabled':True},
                                        {'label': '3', 'value': 3,'disabled':True},
                                    ],
                                    value=0,
                                    labelStyle={'display': 'inline-block', 'margin-left': 15},
                                ),
                                md=4,
                                align='center',
                            ),
                        ]
                    ),
                    dbc.Label("Number of lobes"),
                    # Label class chosen with buttons
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.RadioItems(
                                    id="lobe-number",
                                    options=[
                                        {'label': 'Hyposegmented (<3)', 'value': 'Hyposegmented','disabled':True},
                                        {'label': 'Normal (3-5)', 'value': 'Normal','disabled':True},
                                        {'label': 'Hypersegmented (>5)', 'value': 'Hypersegmented','disabled':True},

                                    ],
                                    value='',
                                    # labelStyle={'display': 'inline-block','margin-left': 15},
                                    labelStyle={'margin-left': 20},
                                    style={"font-weight": "lighter"},
                                ),
                                md=8,
                                align='center',
                            ),
                            dbc.Col(
                                dcc.RadioItems(
                                    id="priority-lobes",
                                    options=[
                                        {'label': '0', 'value': 0, 'disabled':True},
                                        {'label': '1', 'value': 1, 'disabled':True},
                                        {'label': '2', 'value': 2, 'disabled':True},
                                        {'label': '3', 'value': 3, 'disabled':True},
                                    ],
                                    value=0,
                                    labelStyle={'display': 'inline-block', 'margin-left': 15},
                                ),
                                md=4,
                                align='center',
                            ),
                        ],
                    ),

                    html.Hr(),
                    dbc.Form(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Label(
                                        "Width of annotation paintbrush",
                                        html_for="stroke-width",
                                    ),
                                    # Slider for specifying stroke width
                                    dcc.Slider(
                                        id="stroke-width",
                                        min=1,
                                        max=6,
                                        step=0.5,
                                        value=DEFAULT_STROKE_WIDTH,
                                    ),
                                ]
                            ),

                        ]
                    ),

                ]
            ),
            dbc.CardFooter(
                [
                    # Download links
                    html.Div(
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Previous Image",
                                        id="previous-image-button",
                                        outline=True,
                                        disabled=True,
                                    ),
                                    dbc.Button(
                                        "Next Image",
                                        id="next-image-button",
                                        outline=True,
                                        disabled=True,
                                    ),
                                ],
                                size="lg",
                                style={"width": "100%"},
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Update Image Path",
                                        id="path-button",
                                        outline=True,
                                    ),
                                ],
                                size="lg",
                                style={"width": "100%"},
                            ),
                            dcc.Checklist(
                                id="save-image",
                                options=[
                                    {'label': 'Save title', 'value': "TITLE", 'disabled': False},
                                    {'label': 'Save annotation', 'value': "ANNOTATION", 'disabled': False},
                                ],
                                value=[],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ),
]
# endregion
# region###################### META DATA TAB ################################

meta = [
    html.Div(
        id="no-display",
        children=[
            # Store for user created masks
            # data is a list of dicts describing shapes
            dcc.Store(id='output-path', data=[DEFAULT_IMAGE_PATH], storage_type='session'),
            dcc.Store(id='directory-images', storage_type='session'),
            dcc.Store(id='index-images', data=0, storage_type='session'),
            dcc.Store(id="masks", data={"shapes": []}),
            dcc.Store(id='mark-flag', data=False, storage_type='session'),
            dcc.Store(id='stroke-color-memory', data=DEFAULT_LABEL_CLASS, storage_type='session'),
            dcc.Store(id='save-image-memory', data=False, storage_type='session'),
            dcc.Store(id='priority-memory', data=['Priority_list'], storage_type='session'),
            dcc.Store(id='image_saved_data',data= {"shapes": [], "priorities": ["Priority_list"], "lobes": [' '], "cellstatus": [' ']}, storage_type='session'),
            # dcc.Store(id='cell-condition-memory', data=False, storage_type='session'),

        ],
    ),
]
# endregion
# region ###################### LAYOUT #######################################

app.layout = html.Div(
    [
        header_tab,
        dbc.Container(
            [
                dbc.Row(
                    id="app-content",
                    children=[dbc.Col(image_tab, md=7,style={"height": "100%"}), dbc.Col(tools_tab, md=5,style={"height": "100%"})],
                ),
                dbc.Row(dbc.Col(meta)),
            ],
            fluid=True,
        ),
    ],
    style={"height": "100vh"},
)


# endregion
# we use a callback to toggle the collapse on small screens

# region ####################### Callbacks ###################################

# region  Update Buttons - Callback
@app.callback(
    [Output("priority-cytoplasm", "value"),
     Output("priority-chromatin", "value"),
     Output("priority-lobes", "value"),
     Output("cell-condition", "value"),
     Output("lobe-number", "value"),
     Output("priority-memory", "data"),

    ],
    [Input("priority-cytoplasm", "value"),
     Input("priority-chromatin", "value"),
     Input("priority-lobes", "value"),
     Input("image_saved_data", "data"),
     Input("cell-condition", "value"),
     Input("lobe-number", "value"),

    ],
    [State("priority-memory", "data"),
     State("cell-condition", "value"),
     State("lobe-number", "value"),
    ]
)
def update_directory(value_cytoplasm, value_chromatin, value_lobes, image_saved_data,cellcondition,lobenumber,
                     priority_memory,cell_condition,lobe_number):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    feature_name=[' ','Cytoplasm', 'Chromatin','Lobes']
    #detect what has changed
    if 'image_saved_data' not in changed_id:
        if 'priority-cytoplasm' in changed_id:
            changed_value=feature_name[1]
            new_priority=value_cytoplasm
        elif 'priority-chromatin' in changed_id:
            changed_value = feature_name[2]
            new_priority = value_chromatin
        elif 'priority-lobes' in changed_id:
            changed_value = feature_name[3]
            new_priority = value_lobes
        else:
            changed_value = 'empty'
            new_priority = 0
        # remove from list
        if changed_value in priority_memory:
            priority_memory.remove(changed_value)

        #insert into listdata exept if priority is zero
        if new_priority !=0:
            priority_memory.insert(new_priority,changed_value)

        if isinstance(cell_condition[0], list):
            print('aka')
            cell_condition = cell_condition[0]
        if isinstance(lobe_number[0], list):
            print("ALA")
            lobe_number = lobe_number[0]

    else:
        cell_condition = image_saved_data['cellstatus']
        #if isinstance(cell_condition[0],list):
        #    print('aka')
        cell_condition= cell_condition[0]
        lobe_number = image_saved_data['lobes']
        #if isinstance(lobe_number[0],list):
        #    print("ALA")
        lobe_number= lobe_number[0]
        priority_memory = image_saved_data['priorities']
        if isinstance(priority_memory[0],list):
            priority_memory= priority_memory[0]


    # update priority Cytoplasm
    if priority_memory.count(feature_name[1]) != 0:
       value_cytoplasm = priority_memory.index(feature_name[1])
    else:
        value_cytoplasm = 0
    # update priority Chromatin
    if priority_memory.count(feature_name[2]) !=0:
        value_chromatin = priority_memory.index(feature_name[2])
    else:
        value_chromatin = 0
    # update priority Lobes
    if priority_memory.count(feature_name[3]) !=0:
        value_lobes = priority_memory.index(feature_name[3])
    else:
        value_lobes =0

    print(changed_id)
    print('here',value_cytoplasm, value_chromatin, value_lobes, priority_memory, lobe_number,cell_condition)
    return value_cytoplasm, value_chromatin, value_lobes, cell_condition,lobe_number, priority_memory

# endregion

# region Image Path button disabled - Callback
@app.callback(
    [Output("output-path", "data"),
     Output("next-image-button", "disabled"),
     Output("previous-image-button", "disabled"),
     Output("transparent-button", "disabled"),
     Output("granular-button", "disabled"),
     Output("heterogenic-button", "disabled"),
     Output("homogenic-button", "disabled"),
     Output("stroke-width", "disabled"),
     Output("priority-cytoplasm", "options"),
     Output("priority-chromatin", "options"),
     Output("priority-lobes", "options"),
     Output("cell-condition", "options"),
     Output("lobe-number", "options"),
     ],
    [Input("path-button", "n_clicks")],
)
def select_directory(n1):
    options_F = [
                  {'label': '0', 'value': 0, 'disabled': False},
                  {'label': '1', 'value': 1, 'disabled': False},
                  {'label': '2', 'value': 2, 'disabled': False},
                  {'label': '3', 'value': 3, 'disabled': False},
              ]
    options_T = [
                    {'label': '0', 'value': 0, 'disabled': True},
                    {'label': '1', 'value': 1, 'disabled': True},
                    {'label': '2', 'value': 2, 'disabled': True},
                    {'label': '3', 'value': 3, 'disabled': True},
                ]
    options_lobes_T = [
        {'label': 'Hyposegmented (<3)', 'value': 'Hyposegmented', 'disabled': True},
        {'label': 'Normal (3-5)', 'value': 'Normal', 'disabled': True},
        {'label': 'Hypersegmented (>5)', 'value': 'Hypersegmented', 'disabled': True},
        ]
    options_lobes_F = [
        {'label': 'Hyposegmented (<3)', 'value': 'Hyposegmented', 'disabled':False},
        {'label': 'Normal (3-5)', 'value': 'Normal', 'disabled': False},
        {'label': 'Hypersegmented (>5)', 'value': 'Hypersegmented', 'disabled': False},
    ]
    options_cell_T = [
                  {'label': 'Dysplastic', 'value': 'DYSPLASTIC', 'disabled': True},
                  {'label': 'Healthy', 'value': 'HEALTHY', 'disabled': True},
              ]
    options_cell_F = [
                  {'label': 'Dysplastic', 'value': 'DYSPLASTIC', 'disabled': False},
                  {'label': 'Healthy', 'value': 'HEALTHY', 'disabled': False},
              ]
    if n1:

        root = tkinter.Tk()
        root.lift()
        root.withdraw()
        image_path = filedialog.askdirectory()
        root.destroy()

        #image_path='C:/Users/shern/Google Drive/UPC/TFM/10_Images/3_test/3_test/dysplastic'
        #image_path='/usr/src/app/data'
        if os.path.isdir(image_path):
            return image_path, False, False, False, False, False, False, False, options_F,options_F,options_F, options_cell_F, options_lobes_F
        else:
            return dash.no_update
    else:
        return DEFAULT_IMAGE_PATH, True, True, True, True, True, True, True, options_T,options_T,options_T, options_cell_T, options_lobes_T


# endregion

'''
@app.callback(
    [Output("save-image-memory", "data"),
     Output("save-image", "options"),
     ],
    [Input("save-image", "value"), ],
)
def update_directory(data):
    if 'IMAGE' in data:
        print(True)
        return True, [{'label': 'Save image', 'value': 'IMAGE', 'disabled': False},
                      {'label': 'Save title', 'value': 'TITLE', 'disabled': False},
                      {'label': 'Save annotation', 'value': 'ANNOTATION', 'disabled': False}]
    else:
        print(False)
        return False, [{'label': 'Save image', 'value': 'IMAGE', 'disabled': False},
                       {'label': 'Save title', 'value': 'TITLE', 'disabled': True},
                       {'label': 'Save annotation', 'value': 'ANNOTATION', 'disabled': True}]
'''


#region Show file path on image tab - Callback
@app.callback(
    Output("output-1", "children"),
    [Input("output-path", "data")],
)
def update_directory(data):
    return ("FILE PATH: " + data)
#endregion

# region Show image name on image tab - Callback
@app.callback(
    Output("directory-images", "data"),
    [Input("output-path", "data")],
)
def directory_images(indata):
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(os.getcwd(), indata), topdown=False):
        for name in filenames:
            if fnmatch.fnmatch(name, '*.jpg') and not fnmatch.fnmatch(name, '*annotation.jpg'):
                filelist.append(name)

        return filelist
#endregion

@app.callback(
    [Output("show-image-name", "children"),
     Output("index-images", "data"),
     Output("graph", "figure"),
     Output("masks", "data"),
     Output("mark-flag", "data"),
     Output("stroke-color-memory", "data"),
     Output("image_saved_data", "data"),],
    [Input("next-image-button", "n_clicks"),
     Input("previous-image-button", "n_clicks"),
     Input("directory-images", "data"),
     Input("stroke-width", "value"),
     Input("graph", "relayoutData"),
     Input("transparent-button", "n_clicks"),
     Input("granular-button", "n_clicks"),
     Input("heterogenic-button", "n_clicks"),
     Input("homogenic-button", "n_clicks"),
     Input("cell-condition", "value"),
     Input("lobe-number", "value"),
     Input("priority-memory", "data"),
     # Input("normal-button", "n_clicks"),
     # Input("abnormal-button", "n_clicks"),

     ],
    [State("index-images", "data"),  # index of images in the file
     State("directory-images", "data"),  #
     State("output-path", "data"),
     State("masks", "data"),
     State("graph", "figure"),
     State("mark-flag", "data"),
     State("stroke-color-memory", "data"),
     State("save-image", "value"),
     State("cell-condition", "value"),
     State("priority-memory", "data"),
     State("lobe-number","value"),
     State("image_saved_data", "data"),
     ],
)
def change_image(next_b, prev_b, path_2, stroke_width_value, graph_relayoutData,
                 transparent_but, granular_but, heterogenic_but, homogenic_but,cell__condition,lobe__number,priority__memory,
                 i, data, path, masks_data, figure, mark_flag, stroke_color_memory, save_image, cell_condition, priority_list, lobe_number, image_saved_data):
    # check what has triggered the calback
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    stroke_width = int(round(2 ** (stroke_width_value)))
    print("changed_id",changed_id)

    if 'next-image-button' in changed_id:

        # save current data
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data,
                              save_image=save_image,
                              condition=cell_condition,
                              priority=priority_list,
                              lobe_info=lobe_number,
                              )

        # update image index
        image_index = i + 1
        data_name = data[image_index]

        # check if notations exist
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")
        if os.path.isfile(json_mask_data):  # file with notation shapes exists
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)
            image_saved_data = masks_data

            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                shapes=masks_data["shapes"],
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width,
            )

        else:
            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width,
            )
            masks_data = {"shapes": [], "priorities": ["Priority_list"], "lobes": [' '], "cellstatus": [' ']}

            image_saved_data = masks_data
        mark_flag = False
        print(masks_data)
        return_val=copy.deepcopy(image_index)
        return_val=return_val +1
        return ("FILE NAME: " + data[image_index] +' - '+ str(return_val) + '/'+ str(len(data))), image_index, fig_out, masks_data, mark_flag, stroke_color_memory,image_saved_data

    elif 'previous-image-button' in changed_id:
        # save current data
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data,
                              save_image=save_image,
                              condition=cell_condition,
                              priority=priority_list,
                              lobe_info=lobe_number,
                              )
        # update image index
        image_index = i - 1
        data_name = data[image_index]
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")

        if os.path.isfile(json_mask_data):
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)
            image_saved_data=masks_data

            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                shapes=masks_data["shapes"],
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width
            )
        else:

            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width,
            )
            masks_data = {"shapes": [], "priorities": ["Priority_list"], "lobes": [' '], "cellstatus": [' ']}
            image_saved_data = masks_data
        mark_flag = False
        print(masks_data)
        return_val = copy.deepcopy(image_index)
        return_val=return_val+1
        return ("FILE NAME: " + data[image_index] +' - '+ str(return_val) + '/'+ str(len(data))), (image_index), fig_out, masks_data, mark_flag, stroke_color_memory,image_saved_data

    elif 'directory-images' in changed_id:
        print(i)
        image_index = i
        data_name = data[image_index]
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")

        if os.path.isfile(json_mask_data):
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)

            image_saved_data = masks_data
            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                shapes=masks_data["shapes"],
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width
            )
        else:

            fig_out = make_default_figure(
                images=os.path.join(os.getcwd(), path, data_name),
                stroke_color=class_to_color(stroke_color_memory),
                stroke_width=stroke_width,
            )
        mark_flag = False
        return_val = copy.deepcopy(image_index)
        return_val=return_val+1
        return ("FILE NAME: " + data[image_index] +' - '+ str(return_val) + '/'+ str(len(data))), (image_index), fig_out, masks_data, mark_flag, stroke_color_memory,image_saved_data
    else:
        image_index = i

        if 'transparent-button' in changed_id:
            stroke_color_memory = 0
        elif 'granular-button' in changed_id:
            stroke_color_memory = 1
        elif 'heterogenic-button' in changed_id:
            stroke_color_memory = 2
        elif 'homogenic-button' in changed_id:
            stroke_color_memory = 3
        elif 'abnormal-button' in changed_id:
            stroke_color_memory = 5
        elif 'normal-button' in changed_id:
            stroke_color_memory = 4
        else:
            stroke_color_memory = stroke_color_memory

        if changed_id == "graph.relayoutData":
            if "shapes" in graph_relayoutData.keys():
                masks_data["shapes"] = graph_relayoutData["shapes"]
                mark_flag = True
            else:
                return dash.no_update
        if ("cell-condition" in changed_id) or ( "lobe-number" in changed_id) or ("priority-memory" in changed_id):
            mark_flag = True
            print(mark_flag)

        fig_out = make_default_figure(
            images=os.path.join(os.getcwd(), path, data[image_index]),
            stroke_color=class_to_color(stroke_color_memory),
            stroke_width=stroke_width,
            shapes=masks_data["shapes"]
        )
        return_val = copy.deepcopy(image_index)
        return_val= return_val+1
        return ("FILE NAME: " + data[image_index] +' - '+ str(return_val) + '/'+ str(len(data))), image_index, fig_out, masks_data, mark_flag, stroke_color_memory,dash.no_update


def save_image_annotation(mark_flag, path, data_name, shapes, save_image, condition, priority, lobe_info):
    # check existance of anotation
    export_image=False

    if mark_flag:  # annotation is true
        images_path = os.path.join(os.getcwd(), path, data_name)
        fig = px.imshow(io.imread(images_path))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        if 'TITLE' in save_image:
            print('Title')
            Image_name = data_name + '<br>'
            Cell_condition = 'Status:' + condition + '<br>'
            Lobe_condition = 'N lobes:' + lobe_info + '<br>'
            if len(priority) > 1:
                First_status = 'First:' + priority[1] + '<br>'
            else:
                First_status= ' '
            if len(priority) > 2:
                Second_status = 'Second:' + priority[2] +'<br>'
            else:
                Second_status= ' '

            if len(priority) >3:
                Third_status = 'Third:' + priority[3] +'<br>'
            else:
                Third_status = ' '

            text = Image_name + Cell_condition + Lobe_condition + First_status + Second_status + Third_status
            fig.add_annotation(
                x=0.1,
                y=0.8,
                text=text,
                xref="paper",
                yref="paper",
                showarrow=False,
                font_size=15,
                align="left",
            ),
            export_image=True
        if 'ANNOTATION' in save_image:
            print('annotation')
            fig.update_layout(
                margin=dict(l=0, r=0, b=0, t=0, pad=0),
                shapes=shapes["shapes"],
            )
            export_image=True
        if export_image:
            save_to_image = os.path.join(os.getcwd(), path, data_name[:-4] + "_annotation" + data_name[-4:])
            fig.write_image(save_to_image, engine="kaleido")

        # save data
        print(priority)
        #del shapes['priorities']
        shapes['priorities']=priority,
        #del shapes['lobes']
        shapes['lobes']=lobe_info,
        #del shapes['cellstatus']
        shapes['cellstatus']= condition,
        save_json = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")
        with open(save_json, 'w') as outfile:
            json.dump(shapes, outfile)

    else:  # no annotation
        print(False)


# endregion


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=8050, debug=DEBUG)
