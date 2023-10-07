r"""
Matplotlib realtime plotting of residuals
"""

import io
import asyncio
from trame.app import get_server, asynchronous

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
state.show_dialog3 = False

# keep updating the graph
state.keep_updating = True
state.countdown = True


# tk file browser
from tkinter import filedialog, Tk
# Keep track of the currently selected directory
state.selected_dir = None
root = Tk()
# Ensure the tkinter main window is hidden
root.withdraw()
# Ensure that the file browser will appear in front on Windows
root.wm_attributes("-topmost", 1)

# qt5 file_browser_ui.py
#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *

import sys

# A simple widget consisting of a QLabel, a QLineEdit and a
# QPushButton. The class could be implemented in a separate
# script called, say, file_browser.py
# class FileBrowser(QWidget):

#     OpenFile = 0

#     def __init__(self, title, mode=OpenFile):
#         QWidget.__init__(self)
#         layout = QHBoxLayout()
#         self.setLayout(layout)
#         self.browser_mode = mode
#         self.filter_name = 'All files (*.*)'
#         self.dirpath = QDir.currentPath()
#         self.filepaths = []

#         self.label = QLabel()
#         self.label.setText(title)
#         self.label.setFixedWidth(65)
#         self.label.setFont(QFont("Arial",weight=QFont.Bold))
#         self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         layout.addWidget(self.label)

#         self.lineEdit = QLineEdit(self)
#         self.lineEdit.setFixedWidth(180)

#         layout.addWidget(self.lineEdit)

#         self.button = QPushButton('Search')
#         self.button.clicked.connect(self.getFile)
#         layout.addWidget(self.button)
#         layout.addStretch()
#     #--------------------------------------------------------------------
#     def setMode(mode):
#         self.mode = mode
#     #--------------------------------------------------------------------
#     # For example,
#     #    setFileFilter('Images (*.png *.xpm *.jpg)')
#     def setFileFilter(text):
#         self.filter_name = text
#     #--------------------------------------------------------------------
#     def setDefaultDir(path):
#         self.dirpath = path
#     #--------------------------------------------------------------------
#     def getFile(self):
#         self.filepaths = []

#         if self.browser_mode == FileBrowser.OpenFile:
#             self.filepaths.append(QFileDialog.getOpenFileName(self, caption='Choose File',
#                                                     directory=self.dirpath,
#                                                     filter=self.filter_name)[0])
#         if len(self.filepaths) == 0:
#             return
#         elif len(self.filepaths) == 1:
#             self.lineEdit.setText(self.filepaths[0])
#         else:
#             self.lineEdit.setText(",".join(self.filepaths))
#     #--------------------------------------------------------------------
#     def setLabelWidth(self, width):
#         self.label.setFixedWidth(width)
#     #--------------------------------------------------------------------
#     def setlineEditWidth(self, width):
#         self.lineEdit.setFixedWidth(width)
#     #--------------------------------------------------------------------
#     def getPaths(self):
#         return self.filepaths
# #-------------------------------------------------------------------

# class Demo(QDialog):
#     def __init__(self, parent=None):
#         QDialog.__init__(self, parent)

#         # Ensure our window stays in front and give it a title
#         self.setWindowFlags(Qt.WindowStaysOnTopHint)
#         self.setWindowTitle("File Browsing Dialog")
#         self.setFixedSize(400, 300)

#         # Create and assign the main (vertical) layout.
#         vlayout = QVBoxLayout()
#         self.setLayout(vlayout)

#         self.fileBrowserPanel(vlayout)
#         vlayout.addStretch()
#         self.addButtonPanel(vlayout)
#         self.show()
#     #--------------------------------------------------------------------
#     def fileBrowserPanel(self, parentLayout):
#         vlayout = QVBoxLayout()
#         self.fileFB = FileBrowser('Open File', FileBrowser.OpenFile)
#         vlayout.addWidget(self.fileFB)
#         vlayout.addStretch()
#         parentLayout.addLayout(vlayout)
#     #--------------------------------------------------------------------
#     def addButtonPanel(self, parentLayout):
#         hlayout = QHBoxLayout()
#         hlayout.addStretch()

#         self.button = QPushButton("OK")
#         self.button.clicked.connect(self.buttonAction)
#         hlayout.addWidget(self.button)
#         parentLayout.addLayout(hlayout)
#     #--------------------------------------------------------------------
#     def buttonAction(self):
#         global history_filename
#         print(self.fileFB.getPaths())
#         history_filename = self.fileFB.getPaths()[0]
#         print("filename=",history_filename)
#         readHistory(history_filename)

#         self.done(1)

    #--------------------------------------------------------------------

@ctrl.set("open_directory_qt")
def open_directory_qt():
    #kwargs = {
    #    "title": "Select Directory",
    #}
    #state.selected_dir = filedialog.askopenfilename(**kwargs)
    #print("state.selected_dir=",state.selected_dir)
    print("create qapplication")
    #app = QApplication(sys.argv)
    #demo = Demo() # <<-- Create an instance
    #demo.show()
    #app.exec_()
    print("exit")


@ctrl.set("open_directory_tk")
def open_directory_tk():
    kwargs = {
        "title": "Select Directory",
    }
    state.selected_dir = filedialog.askopenfilename(**kwargs)
    print("state.selected_dir=",state.selected_dir)
    global history_filename
    history_filename = state.selected_dir
    readHistory(history_filename)



@asynchronous.task
async def start_countdown():

    while state.keep_updating:
        with state:
            await asyncio.sleep(1.0)
            print("keep updating = ",state.keep_updating)
            global history_filename
            readHistory(history_filename)
            # we flip-flop the true-false state to keep triggering the state and read the history file
            state.countdown = not state.countdown

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


        # close dialog window button
        #with vuetify.VCardText():
        # right-align the button
        with vuetify.VCol(classes="text-right"):
          vuetify.VBtn("Close", classes="mt-5",click=update_dialog2)

   # show_dialog2 determines if the entire dialog is shown or not
    with vuetify.VDialog(width=200,position='{X:10,Y:10}',transition="dialog-top-transition",v_model=("show_dialog3",False)):
      #with vuetify.VCard(color="light-gray"):
      with vuetify.VCard():
        vuetify.VCardTitle("Line-tab2 visibility", classes="grey lighten-1 grey--text text--darken-3")

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



        # close dialog window button
        # right-align the button
        with vuetify.VCol(classes="text-right"):
          vuetify.VBtn("Close", classes="mt-5",click=update_dialog3)


def update_dialog():
    state.show_dialog = not state.show_dialog

def update_dialog2():
    state.show_dialog2 = not state.show_dialog2
    state.dirty('monitorLinesVisibility')
    state.dirty('monitorLinesNames')
    state.dirty('monitorLinesRange')


def update_dialog3():
    state.show_dialog3 = not state.show_dialog3
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

    if ((w_inch<=0) or (h_inch<=0)):
       return {}

    return {
        "figsize": (w_inch, h_inch),
        "dpi": dpi,
    }



# -----------------------------------------------------------------------------


###############################################################################
def DotsandPoints():

    plt.close('all')
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
        start_countdown()

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

        #with vuetify.VBtn("path",click=ctrl.open_directory_qt):
        with vuetify.VBtn("path",click=ctrl.open_directory_tk):
            vuetify.VIcon("{{solver_icon}}",color="red")

        #with vuetify.VBtn("filename",click=ctrl.open_file):
        #    vuetify.VIcon("{{solver_icon}}",color="blue")

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
                with vuetify.VCol(cols="1",classes="pa-0 ma-0"):


                  with vuetify.VRow(dense=True,classes="pa-0 ma-0"):
                    with vuetify.VBtn(classes="ml-2 mr-0 mt-6 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                      vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")
                  with vuetify.VRow(dense=True,classes="pa-0 ma-0"):
                    with vuetify.VBtn(classes="ml-2 mr-0 mt-6 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                      vuetify.VIcon("mdi-dots-vertical",density="compact",color="red")
                  with vuetify.VRow(dense=True,classes="pa-0 ma-0"):
                    with vuetify.VBtn(classes="ml-2 mr-0 mt-6 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                      vuetify.VIcon("mdi-dots-vertical",density="compact",color="blue")
                  with vuetify.VRow(dense=True,classes="pa-0 ma-0"):
                    with vuetify.VBtn(classes="ml-2 mr-0 mt-6 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                      vuetify.VIcon("mdi-dots-vertical",density="compact",color="black")
                  with vuetify.VRow(dense=True,classes="pa-0 ma-0"):
                    with vuetify.VBtn(classes="ml-2 mr-0 mt-6 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog2, icon="mdi-dots-vertical"):
                      vuetify.VIcon("mdi-dots-vertical",density="compact",color="green")

                with vuetify.VCol(cols="11",classes="pl-n0 pr-0 py-0 ml-n12 mr-0 my-0"):
                  with trame.SizeObserver("figure_size"):
                    html_figure1 = tramematplotlib.Figure(style="position: absolute")
                    ctrl.update_figure1 = html_figure1.update

            with vuetify.VTabItem(
               value=(1,), style="width: 100%; height: 100%;"
            ):
             with vuetify.VRow(dense=True, style="height: 100%;", classes="pa-0 ma-0"):
                with vuetify.VBtn(classes="ml-2 mr-0 mt-16 mb-0 pa-0", elevation=1,variant="text",color="white",click=update_dialog3, icon="mdi-dots-vertical"):
                  vuetify.VIcon("mdi-dots-vertical",density="compact",color="red")
                with vuetify.VCol(
                    classes="pa-0 ma-0",
                ):
                  with trame.SizeObserver("figure_size"):
                    html_figure2 = tramematplotlib.Figure(style="position: absolute")
                    ctrl.update_figure2 = html_figure2.update

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
