import plotly.express as px
import plotly
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import os
import tkinter
from tkinter import filedialog
import plotly.express as px
from skimage import data
import json

# from skimage import io as skio

from skimage import io

external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/segmentation-style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.title = "Interactive image segmentation based on machine learning"
DEBUG = True

################## Header Tab ################################
# region
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

##################### IMAGE TAB ####################################
# region
# -------------------- CONFIGURATION ------------------------
DEFAULT_IMAGE_PATH = "assets/images"
DEFAULT_STROKE_WIDTH = 2  # gives line width of 2^3 = 8

DEFAULT_LABEL_CLASS = 0
NUM_LABEL_CLASSES = 5
class_label_colormap = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"]
class_labels = list(range(NUM_LABEL_CLASSES))
assert NUM_LABEL_CLASSES <= len(class_label_colormap)  # we can't have less colors than classes

# --------------------- Functions -------------------------------
filelist = []
for (dirpath, dirnames, filenames) in os.walk(os.path.join(os.getcwd(), DEFAULT_IMAGE_PATH), topdown=False):
    for name in filenames:
        filelist.append(os.path.join(os.getcwd(), dirpath, name))


def class_to_color(n):
    return class_label_colormap[n]


def make_default_figure(
        images=filelist[-1],
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


# --------------------- TAB --------------------------------------
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


# ----------------- Callbacks--------------

# image path callbacks
@app.callback(
    [Output("output-path", "data"),
     Output("next-image-button", "disabled"),
     Output("previous-image-button", "disabled")],
    [Input("path-button", "n_clicks")],
)
def select_directory(n1):
    if n1:
        root = tkinter.Tk()
        root.withdraw()
        image_path = filedialog.askdirectory()
        root.destroy()
        if os.path.isdir(image_path):
            return image_path, False, False
        else:
            return dash.no_update
    else:
        return DEFAULT_IMAGE_PATH, True, True


@app.callback(
    Output("output-1", "children"),
    [Input("output-path", "data")],
)
def update_directory(data):
    return data


# image name callback
@app.callback(
    Output("directory-images", "data"),
    [Input("output-path", "data")],
)
def directory_images(indata):
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(os.getcwd(), indata), topdown=False):
        filelist.extend(filenames)
        print(filelist)
        return filelist


@app.callback(
    [Output("output-2", "children"),
     Output("index-images", "data"),
     Output("graph", "figure"),
     Output("masks", "data"),
     Output("mark-flag", "data"),],
    [Input("next-image-button", "n_clicks"),
     Input("previous-image-button", "n_clicks"),
     Input("directory-images", "data"),
     Input("stroke-width", "value"),
     Input({"type": "label-class-button", "index": dash.dependencies.ALL},
           "n_clicks_timestamp", ),
     Input("graph", "relayoutData"),
     ],
    [State("index-images", "data"),  # index of images in the file
     State("directory-images", "data"),  #
     State("output-path", "data"),
     State("masks", "data"),
     State("graph", "figure"),
     State("mark-flag", "data")],
)
def change_image(next_b, prev_b, path_2, stroke_width_value, any_label_class_button_value, graph_relayoutData, i, data,
                 path, masks_data, figure, mark_flag):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    #print(len(masks_data["shapes"]))
    #print((masks_data["shapes"]))

    if 'next-image-button' in changed_id:
        '''
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data["shapes"],
                             )
        '''
        image_index = i + 1
        fig_out = make_default_figure(
            images=os.path.join(os.getcwd(), path, data[image_index]),
        )
        mark_flag=False
        # masks_data=[]
        return data[image_index], (image_index), fig_out, masks_data, mark_flag
    elif 'previous-image-button' in changed_id:
        '''
        save_image_annotation(mark_flag=mark_flag,
                              path=path,
                              data_name=data[i],
                              shapes=masks_data["shapes"],
                              )
        '''
        image_index = i - 1
        fig_out = make_default_figure(
            images=os.path.join(os.getcwd(), path, data[image_index]),
        )
        # masks_data=[]
        mark_flag = False
        return data[image_index], (image_index), fig_out, masks_data, mark_flag,
    else:
        image_index = i
        stroke_width = int(round(2 ** (stroke_width_value)))
        if any_label_class_button_value is None:
            label_class_value = DEFAULT_LABEL_CLASS
        else:
            label_class_value = max(
                enumerate(any_label_class_button_value),
                key=lambda t: 0 if t[1] is None else t[1],
            )[0]

        if changed_id == "graph.relayoutData":
            if "shapes" in graph_relayoutData.keys():
                masks_data["shapes"] = graph_relayoutData["shapes"]
                mark_flag=True
                print("shapes_exist")
            else:
                print("shapes_not")
                return dash.no_update

        fig_out = make_default_figure(
            images=os.path.join(os.getcwd(), path, data[image_index]),
            stroke_color=class_to_color(label_class_value),
            stroke_width=stroke_width,
            shapes=masks_data["shapes"]
        )
        return data[image_index], image_index, fig_out, masks_data, mark_flag


def save_image_annotation(mark_flag,path, data_name, shapes):
    # check existance of anotation
    images_path=os.path.join(os.getcwd(), path, data_name),
    save_to = os.path.join(os.getcwd(), path,"annotations", data_name),
    print(path)
    print(save_to)
    if mark_flag:
        # annotation
        print(True)

        # check existence of directory
        # save image
        fig = px.imshow(io.imread(images_path))
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0, pad=4),
            shapes=shapes,
        )
    else:
        print(False)
        # no annotation

    # endregion


##################### TOOLS
tools_tab = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Tools"),
            dbc.CardBody(
                [
                    html.H6("Label class", className="card-title"),
                    # Label class chosen with buttons
                    html.Div(
                        id="label-class-buttons",
                        children=[
                            dbc.Button(
                                "%2d" % (n,),
                                id={"type": "label-class-button", "index": n},
                                style={"background-color": class_to_color(c)},
                            )
                            for n, c in enumerate(class_labels)
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

                        ],
                    ),

                    html.A(id="download-image", download="classified-image.png", ),
                ]
            ),
        ],
    ),
]

###################### META DATA ####################
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

        ],
    ),
]

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

# we use a callback to toggle the collapse on small screens


if __name__ == "__main__":
    app.run_server(debug=DEBUG)
