from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP
from sharppy.viz import SkewApp
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import datetime as date
from subprocess import call
from StringIO import StringIO
import sharppy.sharptab.profile as profile
import urllib
import numpy as np


# Create an application
app = QApplication([])

class MainWindow(QWidget):
    def __init__(self, **kwargs):
        """
        Construct the main window and handle all of the
        necessary events. This window serves as the SHARPpy
        sounding picker - a means for interactively selecting
        which sounding profile(s) to view.
        """
        super(MainWindow, self).__init__(**kwargs)

        ## create a threading pool
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(10)
        self.delta = date.timedelta(hours=12)
        ## default the sounding location to none
        self.loc = None
        self.prof_time = "Latest"
        self.model = "Observed"
        self.run = None
        self.map = None
        self.__initUI()

    def __initUI(self):
        """
        Initialize the main user interface.
        """

        ## Give the main window a layout. Using GridLayout
        ## in order to control placement of objects.

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        ## set the window title
        self.setWindowTitle('SHARPpy Sounding Picker')

        # Create and fill a QWebView
        self.view = self.create_map_view()
        self.button = QPushButton('Generate Profiles')
        self.button.clicked.connect(self.complete_name)

        self.profile_list = self.list_profiles()
        self.profile_list.clicked.connect(self.get_time)

        ## create subwidgets that will hold the individual GUI items
        self.left_data_frame = QWidget()
        self.right_map_frame = QWidget()
        ## set the layouts for these widgets
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.left_data_frame.setLayout(self.left_layout)
        self.right_map_frame.setLayout(self.right_layout)

        ## create dropdown menus
        self.model_dropdown = self.dropdown_menu(['Observed', 'GFS', 'NAM', 'NAM 4km', 'RAP', 'HRRR', 'SREF'])
        self.map_dropdown = self.dropdown_menu(['CONUS', 'Southeast', 'Central', 'West', 'Northeast', 'Europe', 'Asia'])
        runs = []
        for i in range(0,24):
            runs.append(str(i).zfill(2) + "Z")
        self.run_dropdown = self.dropdown_menu(runs)

        self.model_dropdown.activated.connect(self.get_model)
        self.map_dropdown.activated.connect(self.get_map)
        self.run_dropdown.activated.connect(self.get_run)

        ## Create text labels to describe the various menus
        self.type_label = QLabel("Select Sounding Type")
        self.date_label = QLabel("Select Sounding Date")
        self.map_label = QLabel("Select Map Area")
        self.run_label = QLabel("Select Model Run")

        ## add the elements to the left side of the GUI
        self.left_layout.addWidget(self.type_label)
        self.left_layout.addWidget(self.model_dropdown)
        self.left_layout.addWidget(self.run_label)
        self.left_layout.addWidget(self.run_dropdown)
        self.left_layout.addWidget(self.date_label)
        self.left_layout.addWidget(self.profile_list)
        self.left_layout.addWidget(self.button)

        ## add the elements to the right side of the GUI
        self.right_layout.addWidget(self.map_label)
        self.right_layout.addWidget(self.map_dropdown)
        self.right_layout.addWidget(self.view)

        ## add the left and right sides to the main window
        self.layout.addWidget(self.left_data_frame, 0, 0, 1, 1)
        self.layout.addWidget(self.right_map_frame, 0, 1, 2, 2)

    def __date(self):
        """
        This function does some date magic
        """
        current_time = date.datetime.utcnow()
        today_00Z = date.datetime.strptime( str(current_time.year) + str(current_time.month) + str(current_time.day) + "00",
                                    "%Y%m%d%H")
        if current_time.hour >= 12:
            time = today_00Z + self.delta
        else:
            time = today_00Z

        return time

    def create_map_view(self):
        """
        Create a clickable map that will be displayed in the GUI.
        Will eventually be re-written to be more general.

        Returns
        -------
        view : QWebView object
        """
        # Create and fill a QWebView
        view = QWebView()
        view.setUrl(QUrl('observed.html'))
        view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        view.linkClicked.connect(self.map_link)

        return view

    def dropdown_menu(self, item_list):
        """
        Create and return a dropdown menu containing items in item_list.

        Params
        ------
        item_list : a list of strings for the contents of the dropdown menu

        Returns
        -------
        dropdown : a QtGui.QComboBox object
        """
        dropdown = QComboBox()
        dropdown.setEditable(True)
        dropdown.lineEdit().setReadOnly(True)
        dropdown.lineEdit().setAlignment(Qt.AlignCenter)
        for item in item_list:
            dropdown.addItem(item)

        return dropdown


    def list_profiles(self):
        """
        Add profile times to the list of profiles.
        """
        list = QListWidget()
        time = self.__date()
        timelist = []
        if self.model == "Observed":
            timelist = ['Latest', time.strftime('%Y:%m:%d %HZ')]
            i = 0
            while i < 17:
                time = time - self.delta
                timelist.append(time.strftime('%Y:%m:%d %HZ'))
                i += 1

        for item in timelist:
            list.addItem(item)
        return list



    def map_link(self, url):
        """
        Change the text of the button based on the user click.
        """
        self.loc = url.toString().split('/')[-1]
        self.button.setText(self.loc + ' | Generate Profiles')


    def complete_name(self):
        """
        Handles what happens when the user clicks a point on the map
        """
        if self.loc is None:
            return
        else:
            self.skewApp()


    def get_model(self):
        """
        Get the user's model selection
        """
        self.model = self.model_dropdown.currentText()

    def get_run(self):
        """
        Get the user's run hour selection for the model
        """
        self.run = self.run_dropdown.currentText()

    def get_map(self):
        """
        Get the user's map selection
        """
        self.map = self.map_dropdown.currentText()

    def get_time(self):
        """
        Get the user's profile date selection
        """
        self.prof_time = self.profile_list.currentItem().text()

    def skewApp(self):
        self.skew = SkewApp(model=self.model, location=self.loc,
            prof_time=self.prof_time, run=self.run)
        self.skew.show()

if __name__ == '__main__':
    win = MainWindow()
    win.show()
    app.exec_()
