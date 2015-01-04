from sharppy.viz import SkewApp
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import datetime as date
import sys


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

        ## All of these variables get set/reset by the various menus in the GUI

        ## this is the time step between available profiles
        self.delta = 12
        ## default the sounding location to OUN because obviously I'm biased
        self.loc = "OUN"
        ## set the default profile to display
        self.prof_time = "Latest"
        ## the index of the item in the list that corresponds
        ## to the profile selected from the list
        self.prof_idx = []
        ## set the default profile type to Observed
        self.model = "Observed"
        ## the offset is time time offset between sounding availabilities for models
        self.offset = 1
        ## this is the duration of the period the available profiles have
        self.duration = 17
        ## this is the default model initialization time.
        self.run = "00Z"
        ## this is the default map to display
        self.map = None
        ## initialize the UI
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
        self.select_flag = False
        self.all_profs = QPushButton("Select All")
        self.all_profs.clicked.connect(self.select_all)

        self.profile_list = self.list_profiles()

        ## create subwidgets that will hold the individual GUI items
        self.left_data_frame = QWidget()
        self.right_map_frame = QWidget()
        ## set the layouts for these widgets
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.left_data_frame.setLayout(self.left_layout)
        self.right_map_frame.setLayout(self.right_layout)

        ## create dropdown menus
        self.model_dropdown = self.dropdown_menu(['Observed', 'GFS', 'NAM', 'NAM4KM', 'RAP', 'HRRR', 'SREF'])
        self.map_dropdown = self.dropdown_menu(['CONUS', 'Southeast', 'Central', 'West', 'Northeast', 'Europe', 'Asia'])
        self.run_dropdown = self.dropdown_menu(["None"])

        ## connect the click actions to functions that do stuff
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
        self.left_layout.addWidget(self.all_profs)
        self.left_layout.addWidget(self.button)

        ## add the elements to the right side of the GUI
        self.right_layout.addWidget(self.map_label)
        self.right_layout.addWidget(self.map_dropdown)
        self.right_layout.addWidget(self.view)

        ## add the left and right sides to the main window
        self.layout.addWidget(self.left_data_frame, 0, 0, 1, 1)
        self.layout.addWidget(self.right_map_frame, 0, 1, 1, 1)
        self.left_data_frame.setMaximumWidth(200)

        self.menuBar()

    def __date(self):
        """
        This function does some date magic to get the current date nearest to 00Z or 12Z
        """
        current_time = date.datetime.utcnow()
        delta = date.timedelta(hours=12)
        today_00Z = date.datetime.strptime( str(current_time.year) + str(current_time.month).zfill(2) +
                                            str(current_time.day).zfill(2) + "00", "%Y%m%d%H")
        if current_time.hour >= 12:
            time = today_00Z + delta
        else:
            time = today_00Z

        return time

    def menuBar(self):

        self.bar = QMenuBar()
        self.filemenu = self.bar.addMenu("File")
        opendata = QAction("Open", self, shortcut=QKeySequence("Ctrl+O"))
        exit = QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"))
        pref = QAction("Preferences", self)
        self.filemenu.addAction(opendata)
        opendata.triggered.connect(self.openFile)
        self.filemenu.addAction(exit)
        exit.triggered.connect(self.exitApp)        
        self.filemenu.addAction(pref)
        self.filemenu.addAction(exit)
        self.helpmenu = self.bar.addMenu("Help")
        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)
        self.helpmenu.addAction(about)

    def exitApp(self):
        self.close()

    def openFile(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.model = "Archive"
        self.location = None
        self.prof_time = None
        self.run = None
        self.skew = SkewApp(model=self.model, location=self.loc,
            prof_time=self.prof_time, run=self.run, path=fname)
        self.skew.show()

    def aboutbox(self):

        msgBox = QMessageBox()
        msgBox.setText("SHARPpy\nSounding and Hodograph Research and Analysis Program for " +
                       "Python\n\n(C) 2014 by Kelton Halbert and Greg Blumberg")
        msgBox.exec_()

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
        view.setUrl(QUrl(self.model.lower() + '.html'))
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
        ## create the dropdown menu
        dropdown = QComboBox()
        ## set the text as editable so that it can have centered text
        dropdown.setEditable(True)
        dropdown.lineEdit().setReadOnly(True)
        dropdown.lineEdit().setAlignment(Qt.AlignCenter)

        ## add each item in the list to the dropdown
        for item in item_list:
            dropdown.addItem(item)

        return dropdown


    def list_profiles(self):
        """
        Add profile times to the list of profiles.
        """
        ## create a list widget
        list = QListWidget()
        list.setSelectionMode(QAbstractItemView.MultiSelection)
        ## get the date nearest to 00Z or 12 Z
        time = self.__date()

        timelist = ['Latest', time.strftime('%Y:%m:%d %HZ')]
        delta = date.timedelta(hours=self.delta)
        i = 0
        while i < 17:
            time = time - delta
            timelist.append(time.strftime('%Y:%m:%d %HZ'))
            i += 1
        for item in timelist:
            list.addItem(item)
        return list

    def update_list(self):
        """
        Update the list with new dates.

        :param list:
        :return:
        """
        self.profile_list.clear()
        self.prof_idx = []
        timelist = []

        if self.model == "Observed":
            self.set_model_dt()
            time = self.__date()
            timelist = ['Latest', time.strftime('%Y:%m:%d %HZ')]
            delta = date.timedelta(hours=self.delta)
            i = 0
            while i < 17:
                time = time - delta
                timelist.append(time.strftime('%Y:%m:%d %HZ'))
                i += 1

        else:
            current_time = date.datetime.utcnow()
            hour = current_time.hour
            self.set_model_dt()
            delta = date.timedelta(hours=self.delta)
            if hour < int(self.run[:-1]) - self.offset:
                current_time = current_time - date.timedelta(days=1)

            time = date.datetime.strptime( str(current_time.year) + str(current_time.month).zfill(2) +
                                str(current_time.day).zfill(2) + self.run[:-1], "%Y%m%d%H")
            timelist.append(time.strftime('%Y:%m:%d %HZ'))
            i = 0
            while i < self.duration:
                time = time + delta
                timelist.append(time.strftime('%Y:%m:%d %HZ'))
                i += 1

        for item in timelist:
            self.profile_list.addItem(item)

        self.profile_list.update()


    def set_model_dt(self):
        """
        Set the model dt (model time step) based on the user's selection, in addition
        to the duration of the forecast and the time offset in hours that determines
        when new model data is available.
        """
        if self.model == "Observed":
            self.delta = 12
            self.duration = 17
            self.offset = 1
            self.available = 12
        elif self.model == "RAP" or self.model == "HRRR":
            self.delta = 1
            self.duration = 15
            self.offset = 1
            self.available = 1
        elif self.model == "NAM":
            self.delta = 1
            self.duration = 83
            self.offset = 3
            self.available = 6
        elif self.model == "NAM4KM":
            self.delta = 1
            self.duration = 60
            self.offset = 3
            self.available = 6
        elif self.model.startswith("GFS"):
            self.delta = 3
            self.duration = 60
            self.offset = 4
            self.available = 6
        elif self.model == "SREF":
            self.delta = 1
            self.duration = 84
            self.offset = 4
            self.available = 3

    def update_run_dropdown(self):
        """
        Updates the dropdown menu that contains the model run
        information.
        :return:
        """
        self.run_dropdown.clear()
        if self.model == "Observed":
            self.run_dropdown.addItem("None")

        else:
            runs = []
            for i in range(0, 24, self.available):
                runs.append(str(i).zfill(2) + "Z")
            for run in runs:
                self.run_dropdown.addItem(run)

        self.run_dropdown.update()

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
            self.prof_idx = []
            selected = self.profile_list.selectedItems()
            for item in xrange(len(selected)):
                #text = item.text()
                if item in self.prof_idx:
                    continue
                else:
                    self.prof_idx.append(item)
            self.prof_time = selected[0].text()
            self.prof_idx.sort()
            self.skewApp()


    def get_model(self):
        """
        Get the user's model selection
        """
        self.model = self.model_dropdown.currentText()
        self.view.setUrl(self.model.lower() + '.html')
        self.update_list()
        self.update_run_dropdown()

    def get_run(self):
        """
        Get the user's run hour selection for the model
        """
        self.run = self.run_dropdown.currentText()
        self.update_list()

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
        item = self.profile_list.currentIndex().row()
        if item in self.prof_idx:
            self.prof_idx.remove(item)
        else:
            self.prof_idx.append(item)
        self.prof_idx.sort()

    def select_all(self):
        items = self.profile_list.count()
        if not self.select_flag:
            for i in range(items):
                if self.profile_list.item(i).text() in self.prof_idx:
                    continue
                else:
                    self.profile_list.item(i).setSelected(True)
            self.all_profs.setText("Deselect All")
            self.select_flag = True
        else:
            for i in range(items):
                self.profile_list.item(i).setSelected(False)
            self.all_profs.setText("Select All")
            self.select_flag = False


    def skewApp(self):
        """
        Create the SPC style SkewT window, complete with insets
        and magical funtimes.
        :return:
        """
        self.skew = SkewApp(model=self.model, location=self.loc,
            prof_time=self.prof_time, run=self.run, idx=self.prof_idx)
        self.skew.show()


if __name__ == '__main__':
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
