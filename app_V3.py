
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
#import plotly
import plotly.express as px
#import plotly.graph_objs as go
#import plotly.io as pio
import os
#import psutil
#import requests
import tkinter
from tkinter import filedialog
from skimage import io
#from skimage import data
import json
import fnmatch

# from skimage import io as skio



external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/segmentation-style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.title = "Interactive image segmentation based on machine learning"
DEBUG = False

# -------------------- CONFIGURATION ------------------------
DEFAULT_IMAGE_PATH = "assets/images"
DEFAULT_STROKE_WIDTH = 2  # gives line width of 2^3 = 8

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
        dragmode="drawopenpath",
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        shapes=shapes,
        newshape=dict(
            line_color=stroke_color,
            line_width=stroke_width,
            opacity=0.5
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
            html.Div(id='output-2'),
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
                                                "drawrect",
                                                "drawopenpath",
                                                "drawclosedpath",
                                                "eraseshape",
                                            ],
                                            "modeBarButtonsToRemove": [
                                                "downloadImage",
                                                "togglespikelines",
                                                "autoscale",
                                            ],
                                        },
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
        id="sidebar-card",
        children=[
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [
                    html.H6("State of the Cytoplasm", className="Cytoplasm-title"),
                    # Label class chosen with buttons
                    html.Div(
                        children=[
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
                                size="lg",
                                style={"width": "100%"},
                            ),
                        ],
                    ),
                    html.H6("Chromatin aspect", className="Chromatin-title"),
                    # Label class chosen with buttons
                    html.Div(
                        children=[
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
                                size="lg",
                                style={"width": "100%"},
                            ),
                        ],
                    ),
                    html.H6("Number of Lobes", className="Lobes-title"),
                    # Label class chosen with buttons
                    html.Div(
                        children=[
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Nomal",
                                        id="normal-button",
                                        outline=True,
                                        disabled=True,
                                        style={"background-color": class_to_color(4)}
                                    ),
                                    dbc.Button(
                                        "Abnormal",
                                        id="abnormal-button",
                                        outline=True,
                                        disabled=True,
                                        style={"background-color": class_to_color(5)}
                                    ),
                                ],
                                size="lg",
                                style={"width": "100%"},
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
                                        "Image Path",
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
                                    {'label': 'Save image', 'value': "IMAGE", 'disabled': False},
                                    {'label': 'Save title', 'value': "TITLE", 'disabled': True},
                                    {'label': 'Save annotation', 'value': "ANNOTATION", 'disabled': True},
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
                    children=[dbc.Col(image_tab, md=8), dbc.Col(tools_tab, md=4)],
                ),
                dbc.Row(dbc.Col(meta)),
            ],
            fluid=True,
        ),
    ]
)


# endregion
# we use a callback to toggle the collapse on small screens

####################### Callbacks ###################################
# region

@app.callback(
    [Output("save-image-memory", "data"),
     Output("save-image", "options"),
     ],
    [Input("save-image", "value"),],
)
def update_directory(data):
    if 'IMAGE' in data:
        print(True)
        return True, [{'label': 'Save image', 'value': 'IMAGE', 'disabled': False}, {'label': 'Save title', 'value': 'TITLE', 'disabled': False}, {'label': 'Save annotation', 'value': 'ANNOTATION', 'disabled': False}]
    else:
        print(False)
        return False, [{'label': 'Save image', 'value': 'IMAGE', 'disabled': False}, {'label': 'Save title', 'value': 'TITLE', 'disabled': True}, {'label': 'Save annotation', 'value': 'ANNOTATION', 'disabled': True}]


# region Image Path button - Callback
@app.callback(
    [Output("output-path", "data"),
     Output("next-image-button", "disabled"),
     Output("previous-image-button", "disabled"),
     Output("transparent-button", "disabled"),
     Output("granular-button", "disabled"),
     Output("heterogenic-button", "disabled"),
     Output("homogenic-button", "disabled"),
     Output("normal-button", "disabled"),
     Output("abnormal-button", "disabled"),
     Output("stroke-width", "disabled"),
     ],
    [Input("path-button", "n_clicks")],
)
def select_directory(n1):
    if n1:
        root = tkinter.Tk()
        root.lift()
        root.withdraw()
        image_path = filedialog.askdirectory()
        root.destroy()
        if os.path.isdir(image_path):
            return image_path, False, False, False, False, False, False, False, False, False
        else:
            return dash.no_update
    else:
        return DEFAULT_IMAGE_PATH, True, True, True, True, True, True, True, True, True


# endregion

@app.callback(
    Output("output-1", "children"),
    [Input("output-path", "data")],
)
def update_directory(data):
    return ("FILE PATH: " + data)


# image name callback
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


@app.callback(
    [Output("output-2", "children"),
     Output("index-images", "data"),
     Output("graph", "figure"),
     Output("masks", "data"),
     Output("mark-flag", "data"),
     Output("stroke-color-memory", "data")],
    [Input("next-image-button", "n_clicks"),
     Input("previous-image-button", "n_clicks"),
     Input("directory-images", "data"),
     Input("stroke-width", "value"),
     Input("graph", "relayoutData"),
     Input("transparent-button", "n_clicks"),
     Input("granular-button", "n_clicks"),
     Input("heterogenic-button", "n_clicks"),
     Input("homogenic-button", "n_clicks"),
     Input("normal-button", "n_clicks"),
     Input("abnormal-button", "n_clicks"),

     ],
    [State("index-images", "data"),  # index of images in the file
     State("directory-images", "data"),  #
     State("output-path", "data"),
     State("masks", "data"),
     State("graph", "figure"),
     State("mark-flag", "data"),
     State("stroke-color-memory", "data"),
     State("save-image", "value")
     ],
)
def change_image(next_b, prev_b, path_2, stroke_width_value, graph_relayoutData,
                 transparent_but, granular_but, heterogenic_but, homogenic_but, normal_but, abnormal_but,
                 i, data, path, masks_data, figure, mark_flag, stroke_color_memory, save_image):
    # check what has triggered the calback
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    stroke_width = int(round(2 ** (stroke_width_value)))
    print(changed_id)

    if 'next-image-button' in changed_id:

        # save current data
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data,
                              save_image=save_image,
                              condition='healthy',
                              )

        # update image index
        image_index = i + 1
        data_name = data[image_index]

        # check if notations exist
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")
        if os.path.isfile(json_mask_data):  # file with notation shapes exists
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)

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
        mark_flag = False
        return ("FILE NAME: " + data[image_index]), image_index, fig_out, masks_data, mark_flag, stroke_color_memory

    elif 'previous-image-button' in changed_id:
        # save current data
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data,
                              save_image=save_image,
                              condition='healthy',
                              )
        # update image index
        image_index = i - 1
        data_name = data[image_index]
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")

        if os.path.isfile(json_mask_data):
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)

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
        return ("FILE NAME: " + data[image_index]), (image_index), fig_out, masks_data, mark_flag, stroke_color_memory

    elif 'directory-images' in changed_id:
        print(i)
        image_index = i
        data_name = data[image_index]
        json_mask_data = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")

        if os.path.isfile(json_mask_data):
            with open(json_mask_data) as json_file:
                masks_data = json.load(json_file)

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
        return ("FILE NAME: " + data[image_index]), (image_index), fig_out, masks_data, mark_flag, stroke_color_memory
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

        fig_out = make_default_figure(
            images=os.path.join(os.getcwd(), path, data[image_index]),
            stroke_color=class_to_color(stroke_color_memory),
            stroke_width=stroke_width,
            shapes=masks_data["shapes"]
        )
        return ("FILE NAME: " + data[image_index]), image_index, fig_out, masks_data, mark_flag, stroke_color_memory


def save_image_annotation(mark_flag, path, data_name, shapes, save_image, condition):
    # check existance of anotation

    if mark_flag:  # annotation is true

        # Save image
        if 'IMAGE' in save_image:
            images_path = os.path.join(os.getcwd(), path, data_name)
            fig = px.imshow(io.imread(images_path))
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            if 'ANNOTATION' in save_image:
                print('annotation')
                fig.update_layout(
                    margin=dict(l=0, r=0, b=0, t=0, pad=0),
                    shapes=shapes["shapes"],
                )
            if 'TITLE' in save_image:
                print('Title')
                fig.update_layout(
                    title={
                        'text': data_name +' - ' + condition,
                        'y':0.9,
                        'x':0.1,
                        'xref': 'paper',
                        'yref': 'paper'}
                )
            save_to_image = os.path.join(os.getcwd(), path,data_name[:-4]+"_annotation"+data_name[-4:])
            fig.write_image(save_to_image,engine="kaleido")

        # save data
        save_json = os.path.join(os.getcwd(), path, data_name[:-4] + "_json.txt")
        with open(save_json, 'w') as outfile:
            json.dump(shapes, outfile)

    else:  # no annotation
        print(False)


# endregion


if __name__ == "__main__":
    app.run_server(debug=DEBUG)
