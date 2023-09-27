r"""
Matplotlib realtime plotting of residuals
"""

#import sys
#import os.path
import io
import asyncio
from trame.app import get_server, asynchronous

# time scheduler (realtime plotting of file data)
#import schedule,time
#import threading

#import numpy as np

#import tkinter
#from PIL import Image, ImageTk

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import pandas as pd
from trame.ui.vuetify import SinglePageWithDrawerLayout
import trame.ui.vuetify
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, trame
from trame.widgets import matplotlib as tramematplotlib
# importing the style package
#from matplotlib import style
#import matplotlib.backends.backend_tkagg as tkagg
#mpl.rcParams["figure.facecolor"]="black"
#plt.style.use("seaborn-dark")
#for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
#  plt.rcParams[param] = '#212946'  # bluish dark grey
#for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
#  plt.rcParams[param] = '0.9'  # very light grey
#ax.grid(color='#2A3459')  # bluish dark grey, but slightly lighter than background

SMALL_SIZE = 10
MEDIUM_SIZE = 10
BIGGER_SIZE = 10

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=20)    # fontsize of the x and y labels

plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
plt.rc('ytick', labelsize=14)    # fontsize of the tick labels

plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title


# line 'i' has fixed color so the color does not change if a line is deselected
mplColorList=['blue','orange','red','green','purple','brown','pink','gray','olive','cyan',
              'black','gold','yellow','springgreen','thistle','beige','coral','navy','salmon','lightsteelblue']

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.monitorLinesVisibility = []
state.monitorLinesNames = []
state.monitorLinesRange = []
state.dataframe = []
state.x = []
state.ylist= []

state.initialization_state_idx = 0
state.show_dialog = False
state.show_dialog2 = False

countdown_init = 100
# keep updating the graph
keep_updating = True

@asynchronous.task
async def start_countdown():
    #try:
    #    state.countdown = int(state.countdown)
    #except:
    #    state.countdown = countdown_init

    while keep_updating:
        with state:
            await asyncio.sleep(3.0)
            print("keep updating = ",keep_updating)
            #state.countdown -= 1


# -----------------------------------------------------------------------------
# Chart examples from:
#   - http://jakevdp.github.io/blog/2013/12/19/a-d3-viewer-for-matplotlib/
# -----------------------------------------------------------------------------

def update_visibility(index, visibility):
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)
    state.monitorLinesVisibility[index] = visibility
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)
    state.dirty("monitorLinesVisibility")
    print(f"Toggle {index} to {visibility}")
    print("monitorLinesVisibility = ",state.monitorLinesVisibility)

######################################################################
def dialog_card():
    print("dialog card, lines=",state.monitorLinesNames)
    # show_dialog2 determines if the entire dialog is shown or not
    with vuetify.VDialog(width=200,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_dialog2",False)):
      #with vuetify.VCard(color="light-gray"):
      with vuetify.VCard():
        vuetify.VCardTitle("Line visibility", classes="grey lighten-1 grey--text text--darken-3")

        #with vuetify.VListGroup(value=("true",), sub_group=True):
        #    with vuetify.Template(v_slot_activator=True):
        #            vuetify.VListItemTitle("Bars")
        #    with vuetify.VListItemContent():
        #            #with vuetify.VListItem(v_for="id in monitorLinesRange", key="id"):
        vuetify.VCheckbox(
                              # loop over list monitorLinesRange
                              v_for="id in monitorLinesRange",
                              key="id",
                              # checkbox changes the state of monitorLinesVisibility[id]
                              v_model=("monitorLinesVisibility[id]",),
                              # name of the checkbox
                              label=("`label= ${ monitorLinesNames[id] }`",),
                              # on each change, immediately go to update_visibility
                              change=(update_visibility,"[id, $event]"),
                              classes="mt-1 pt-1",
                              hide_details=True,
                              dense=True,
        )

        #print("d.names=",state.monitorLinesNames)
        #print("d.range=",state.monitorLinesRange)
        #print("d.visibility=",state.monitorLinesVisibility)


        # close dialog window button
        #with vuetify.VCardText():
        # right-align the button
        with vuetify.VCol(classes="text-right"):
          vuetify.VBtn("Close", classes="mt-5",click=update_dialog2)


def update_dialog():
    state.show_dialog = not state.show_dialog
def update_dialog2():
    state.show_dialog2 = not state.show_dialog2
    state.dirty('monitorLinesVisibility')
    state.dirty('monitorLinesNames')
    state.dirty('monitorLinesRange')



# client-state file reader
@state.change("files_exchange")
def file_uploaded(files_exchange, **kwargs):

    if files_exchange is None:
        return

    nodes_bytes = files_exchange.get("content")
    if isinstance(nodes_bytes, list):
        nodes_bytes = b"".join(nodes_bytes)

    file_name = io.StringIO(nodes_bytes.decode("utf-8"))

    print("read history file ",file_name)



    readHistory(file_name)



# Read the history file
# set the names and visibility
def readHistory(filename):
    skipNrRows=[]
    # read the history file
    dataframe = pd.read_csv(filename,skiprows=skipNrRows)
    # get rid of quotation marks in the column names
    dataframe.columns = dataframe.columns.str.replace('"','')
    # get rid of spaces in the column names
    dataframe.columns = dataframe.columns.str.replace(' ','')

    # limit the columns to the ones containing the strings rms and Res
    dfrms = dataframe.filter(regex='rms|Res')
    print("keys=",dfrms.keys())
    print("list=",list(dataframe))
    print("list=",list(dfrms))

    state.monitorLinesNames = list(dfrms)
    state.monitorLinesRange = list(range(0,len(state.monitorLinesNames)))
    state.monitorLinesVisibility = [True for i in dfrms]

    print("names=",state.monitorLinesNames)
    print("range=",state.monitorLinesRange)
    print("visibility=",state.monitorLinesVisibility)

    state.dirty('monitorLinesVisibility')
    state.dirty('monitorLinesNames')
    state.dirty('monitorLinesRange')

    state.x = [i for i in range(len(dfrms.index))]
    print("x = ",state.x)
    state.ylist=[]
    for c in range(len(dfrms.columns)):
        state.ylist.append(dfrms.iloc[:,c].tolist())


    dialog_card()
    return [state.x,state.ylist]


def figure_size():
    if state.figure_size is None:
        return {}

    dpi = state.figure_size.get("dpi")
    rect = state.figure_size.get("size")
    w_inch = rect.get("width") / dpi
    h_inch = rect.get("height") / dpi

    return {
        "figsize": (w_inch, h_inch),
        "dpi": dpi,
    }


def FirstDemo():
    fig, ax = plt.subplots(**figure_size())
    np.random.seed(0)
    ax.plot(
        np.random.normal(size=100), np.random.normal(size=100), "or", ms=10, alpha=0.3
    )
    ax.plot(
        np.random.normal(size=100), np.random.normal(size=100), "ob", ms=20, alpha=0.1
    )

    ax.set_xlabel("this is x")
    ax.set_ylabel("this is y")
    ax.set_title("Matplotlib Plot Rendered in D3!", size=14)
    ax.grid(color="lightgray", alpha=0.7)

    return fig


# -----------------------------------------------------------------------------


def MultiLines():
    fig, ax = plt.subplots(**figure_size())
    x = np.linspace(0, 10, 1000)
    for offset in np.linspace(0, 3, 7):
        ax.plot(x, 0.9 * np.sin(x - offset), lw=5, alpha=0.4)
    #ax.set_ylim(-1.2, 1.0)
    ax.text(5, -1.1, "Here are some curves", size=18)
    ax.grid(color="lightgray", alpha=0.7)

    return fig


# -----------------------------------------------------------------------------


###############################################################################
def DotsandPoints():


    fig, ax = plt.subplots(1,1,**figure_size(),facecolor='blue')
    #ax.cla()

    #fig.set_facecolor('black')
    #fig.tight_layout()
    #fig.patch.set_linewidth(10)
    #fig.patch.set_edgecolor('purple')
    ax.set_facecolor('#eafff5')
    fig.set_facecolor('blue')
    fig.patch.set_facecolor('blue')
    #ax.plot(
    #    np.random.rand(20),
    #    "-o",
    #    alpha=0.5,
    #    color="black",
    #    linewidth=5,
    #    markerfacecolor="green",
    #    markeredgecolor="lightgreen",
    #    markersize=20,
    #    markeredgewidth=10,
    #)
    #fig.subplots_adjust(top=0.95, bottom=0.1, left=0.1, right=0.9,hspace=0.8)

    fig.subplots_adjust(top=0.98, bottom=0.15, left=0.05, right=0.99, hspace=0.0,wspace=0.0)
    #fig.tight_layout()

    # loop over the list and plot
    for idx in state.monitorLinesRange:
      print("line= ",idx,", name= ",state.monitorLinesNames[idx]," visible:",state.monitorLinesVisibility[idx])
      print("__ range x = ", min(state.x), " ",max(state.x))
      # only plot if the visibility is True
      if state.monitorLinesVisibility[idx]:
        print("printing line ",idx)
        ax.plot( state.x,state.ylist[idx], label=state.monitorLinesNames[idx],linewidth=5, markersize=20, markeredgewidth=10,color=mplColorList[idx])

    ax.set_xlabel('iterations',labelpad=10)
    ax.set_ylabel('residuals',labelpad=-15)
    ax.grid(True, color="lightgray", linestyle="solid")
    ax.legend(framealpha=1,facecolor='white')

    # autoscale the axis
    ax.autoscale(enable=True,axis="x")
    ax.autoscale(enable=True,axis="y")
    #ax.set_xlim(0, 22)
    #ax.set_ylim(-20, 0)
    #frame = ax.legend.get_frame()
    #frame.set_color('white')

    return fig
###############################################################################


# -----------------------------------------------------------------------------


def MovingWindowAverage():
    np.random.seed(0)
    t = np.linspace(0, 10, 300)
    x = np.sin(t)
    dx = np.random.normal(0, 0.3, 300)

    kernel = np.ones(25) / 25.0
    x_smooth = np.convolve(x + dx, kernel, mode="same")

    fig, ax = plt.subplots(**figure_size())
    ax.plot(t, x + dx, linestyle="", marker="o", color="black", markersize=3, alpha=0.3)
    ax.plot(t, x_smooth, "-k", lw=3)
    ax.plot(t, x, "--k", lw=3, color="blue")

    return fig


# -----------------------------------------------------------------------------



def Subplots():
    fig = plt.figure(**figure_size())
    fig.subplots_adjust(hspace=0.3)
    np.random.seed(0)

    for i in range(1, 5):
        ax = fig.add_subplot(2, 2, i)
        color = np.random.random(3)
        ax.plot(np.random.random(30), lw=2, c=color)
        ax.set_title("RGB = ({0:.2f}, {1:.2f}, {2:.2f})".format(*color), size=14)
        ax.grid(color="lightgray", alpha=0.7)

    return fig


###############################################################################
# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------
state.active_figure="DotsandPoints"

state.graph_update=True

@state.change("active_figure", "figure_size", "countdown","monitorLinesVisibility")
def update_chart(active_figure, **kwargs):
    print("updating figure!")
    ctrl.update_figure(globals()[active_figure]())
###############################################################################


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

state.trame__title = "Matplotly"

with SinglePageWithDrawerLayout(server) as layout:
    #with SinglePageLayout(server) as layout:
    layout.title.set_text("realtime update")
    start_countdown()


    # read the file
    [state.x,state.ylist] = readHistory('history.csv')
    print("x=",state.x)
    print("y=",state.ylist)




    # left side menu
    with layout.drawer as drawer:
        # drawer components
        drawer.width = 400
        dialog_card()
        pass

    with layout.toolbar:
        vuetify.VSpacer()

        # file input
        vuetify.VFileInput(
          multiple=False,
          #webkitdirectory=True,
          v_model=("files_exchange", None),
        )

        vuetify.VSelect(
            v_model=("active_figure", "DotsandPoints"),
            items=(
                "figures",
                [
                    {"text": "Dots and Points", "value": "DotsandPoints"},
                    {"text": "First Demo", "value": "FirstDemo"},
                    {"text": "Multi Lines", "value": "MultiLines"},
                    {"text": "Moving Window Average", "value": "MovingWindowAverage"},
                    {"text": "Subplots", "value": "Subplots"},
                ],
            ),
            hide_details=True,
            dense=True,
        )

    with layout.content:
        # fill-height is important
        with vuetify.VContainer( fluid=True, classes=" fill-height pa-0 ma-0"):
            #with vuetify.VRow(classes="pa-2 ma-0", dense=True):
            #    with vuetify.VBtn(classes="ma-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
            #      vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")
            with vuetify.VRow(dense=True, style="height: 100%;", classes="pa-0 ma-0"):
                with vuetify.VBtn(classes="ml-2 mr-0 mt-16 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                  vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")
                with vuetify.VCol(
                    classes="pa-0 ma-0",
                    #style="border-right: 1px solid #ccc; position: relative;",
                ):

                  with trame.SizeObserver("figure_size"):
                    html_figure = tramematplotlib.Figure(style="position: absolute",classes="blue ma-0 pa-0")
                    ctrl.update_figure = html_figure.update



# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
