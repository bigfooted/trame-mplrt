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

state.solver_icon = "mdi-stop-circle"
state.realtime = True
history_filename = 'history.csv'

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
state.keep_updating = True
state.countdown = 1000

@asynchronous.task
async def start_countdown():
    try:
        state.countdown = int(state.countdown)
    except:
        state.countdown = countdown_init

    while state.keep_updating:
        with state:
            await asyncio.sleep(10.0)
            print("keep updating = ",state.keep_updating)
            global history_filename
            readHistory(history_filename)

            #state.countdown = not state.countdown
            state.countdown -= 1


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
    global history_filename

    if files_exchange is None:
        return

    history_filename = files_exchange.get("name")
    print("file = ",history_filename)
    history_filename="user/nijso/sudo/history.csv"
    #nodes_bytes = files_exchange.get("content")
    #if isinstance(nodes_bytes, list):
    #    nodes_bytes = b"".join(nodes_bytes)

    #history_filename = io.StringIO(nodes_bytes.decode("utf-8"))
    print("file_uploaded::read history file ",history_filename)
    readHistory(history_filename)



# Read the history file
# set the names and visibility
def readHistory(filename):
    print("read_history, filename=",filename)
    skipNrRows=[]
    # read the history file
    dataframe = pd.read_csv(filename,skiprows=skipNrRows)
    # get rid of quotation marks in the column names
    dataframe.columns = dataframe.columns.str.replace('"','')
    # get rid of spaces in the column names
    dataframe.columns = dataframe.columns.str.replace(' ','')

    # limit the columns to the ones containing the strings rms and Res
    dfrms = dataframe.filter(regex='rms|Res')
    #print("keys=",dfrms.keys())
    #print("list=",list(dataframe))
    #print("list=",list(dfrms))

    state.monitorLinesNames = list(dfrms)
    state.monitorLinesRange = list(range(0,len(state.monitorLinesNames)))
    state.monitorLinesVisibility = [True for i in dfrms]

    #print("names=",state.monitorLinesNames)
    #print("range=",state.monitorLinesRange)
    #print("visibility=",state.monitorLinesVisibility)

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
      #print("line= ",idx,", name= ",state.monitorLinesNames[idx]," visible:",state.monitorLinesVisibility[idx])
      #print("__ range x = ", min(state.x), " ",max(state.x))
      # only plot if the visibility is True
      if state.monitorLinesVisibility[idx]:
        #print("printing line ",idx)
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



def su2_play():
    print("Start SU2 solver!"),
    # every time we press the button we switch the state
    state.realtime = not state.realtime
    if state.realtime:
        state.solver_icon="mdi-stop-circle"
        print("Real-time update!"),
        state.keep_updating = True
    else:
        state.solver_icon="mdi-play-circle"
        print("Real-time update stopped!"),
        state.keep_updating = False



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
    print("updating figure 1")
    ctrl.update_figure1(globals()[active_figure]())
    ctrl.update_figure2(globals()[active_figure]())

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
    [state.x,state.ylist] = readHistory(history_filename)
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

        #with vuetify.VBtn(icon=True, click=su2_play, disabled=("export_disabled",False)):
        with vuetify.VBtn("Real-time update",click=su2_play):
            vuetify.VIcon("{{solver_icon}}",color="purple")

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
                    {"text": "Subplots", "value": "Subplots"},
                ],
            ),
            hide_details=True,
            dense=True,
        )

    with layout.content:

      with vuetify.VTabs(v_model=("active_tab", 0), right=True):
        vuetify.VTab("plot1")
        vuetify.VTab("plot2")

      # fill-height is important
      with vuetify.VContainer(fluid=True,classes=" fill-height"):
        with vuetify.VTabsItems(
            value=("active_tab",), style="width: 100%; height: 100%;"
        ):
            with vuetify.VTabItem(
                value=(0,), style="width: 100%; height: 100%;"
            ):
              with vuetify.VRow(dense=True, style="height: 100%;", classes="pa-0 ma-0"):
                with vuetify.VBtn(classes="ml-2 mr-0 mt-16 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                  vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")
                with vuetify.VCol(
                    classes="pa-0 ma-0",
                    #style="border-right: 1px solid #ccc; position: relative;",
                ):
                  with trame.SizeObserver("figure_size"):
                    html_figure1 = tramematplotlib.Figure(style="position: absolute")
                    ctrl.update_figure1 = html_figure1.update

            with vuetify.VTabItem(
               value=(1,), style="width: 100%; height: 100%;"
            ):
               with trame.SizeObserver("figure_size"):
                    html_figure2 = tramematplotlib.Figure(style="position: absolute")
                    ctrl.update_figure2 = html_figure2.update

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
