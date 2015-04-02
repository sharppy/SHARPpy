import sys, os
import numpy as np

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    debug = True
    sys.path.insert(0, os.path.normpath(os.getcwd() + "/.."))
else:
    debug = False
    np.seterr(all='ignore')

from sharppy.viz import SkewApp, MapWidget 
import sharppy.sharptab.profile as profile
from sharppy.io.decoder import SPCDecoder, BufDecoder
from datasources import data_source

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import datetime as date
from StringIO import StringIO
import urllib
import traceback
from functools import wraps, partial
import hashlib

class AsyncThreads(QObject):
    def __init__(self):
        super(AsyncThreads, self).__init__()
        self.threads = {}
        self.callbacks = {}
        return

    def post(self, func, callback, *args, **kwargs):
        thd_id = self._genThreadId()

        thd = self._threadFactory(func, thd_id, *args, **kwargs)
        thd.finished.connect(self.finish)
        thd.start()

        self.threads[thd_id] = thd
        if callback is None:
            callback = lambda x: x
        self.callbacks[thd_id] = callback
        return thd_id

    def isFinished(self, thread_id):
        return not (thread_id in self.threads)

    def join(self, thread_id):
        while not self.isFinished(thread_id):
            QCoreApplication.processEvents()

    @Slot(str, tuple)
    def finish(self, thread_id, ret_val):
        thd = self.threads[thread_id]
        callback = self.callbacks[thread_id]

        callback(ret_val)

        del self.threads[thread_id]
        del self.callbacks[thread_id]

    def _genThreadId(self):
        time_stamp = date.datetime.utcnow().isoformat()
        return hashlib.md5(time_stamp).hexdigest()

    def _threadFactory(self, func, thread_id, *args, **kwargs):

        class AsyncThread(QThread):
            finished = Signal(str, tuple)

            def __init__(self):
                super(AsyncThread, self).__init__()
            
            def run(self):
                try:
                    ret_val = func(*args, **kwargs)
                except Exception as e:
                    if debug:
                        print traceback.format_exc()
                    ret_val = e
                if type(ret_val) != tuple:
                    ret_val = (ret_val, )

                self.finished.emit(thread_id, ret_val)

        return AsyncThread()

class progress(QThread):
    _progress = Signal(int, int)
    _text = Signal(str)

    def __init__(self, *args, **kwargs):
        super(progress, self).__init__()
        self._func = None
        self._async = args[0]
        self._ret_val = None

    def __get__(self, obj, cls):
        return partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and hasattr(args[0], '__call__'):
            self._func = args[0]
            ret = self.doasync
        else:
            ret = self.doasync(*args, **kwargs)
        return ret

    def doasync(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self._kwargs['__prog__'] = self._progress
        self._kwargs['__text__'] = self._text

        self._progress_dialog = QProgressDialog()
        self._progress.connect(self.updateProgress)
        self._text.connect(self.updateText)
        self._progress_dialog.setMinimum(0)
        self._progress_dialog.setValue(0)

        self._progress_dialog.open()
        self._isfinished = False

        def finish(ret_val):
            self._isfinished = True
            self._progress_dialog.close()
            self._ret_val = ret_val

        self._async.post(self._func, finish, *self._args, **self._kwargs)

        while not self._isfinished:
            QCoreApplication.processEvents()

        return self._ret_val

    @Slot(int, int)
    def updateProgress(self, value, maximum):
        text = self._prog_text

        self._progress_dialog.setMaximum(maximum)
        self._progress_dialog.setValue(value)

        if maximum > 0:
            text += " (%d / %d)" % (value, maximum)
        self._progress_dialog.setLabelText(text)

    @Slot(str)
    def updateText(self, text):
        self._prog_text = text
        self._progress_dialog.setLabelText(text)

# Create an application
app = QApplication([])

class MainWindow(QWidget):
    date_format = "%Y-%m-%d %HZ"
    run_format = "%d %B %Y / %H%M UTC"

    async = AsyncThreads()

    def __init__(self, **kwargs):
        """
        Construct the main window and handle all of the
        necessary events. This window serves as the SHARPpy
        sounding picker - a means for interactively selecting
        which sounding profile(s) to view.
        """

        super(MainWindow, self).__init__(**kwargs)
        self.data_sources = data_source.loadDataSources()

        ## All of these variables get set/reset by the various menus in the GUI

        ## default the sounding location to OUN because obviously I'm biased
        self.loc = None
        ## set the default profile to display
        self.prof_time = "Latest"
        ## the index of the item in the list that corresponds
        ## to the profile selected from the list
        self.prof_idx = []
        ## set the default profile type to Observed
        self.model = "Observed"
        ## this is the default model initialization time.
        self.run = [ t for t in self.data_sources[self.model].getAvailableTimes() if t.hour in [0, 12] ][-1]
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
        self.all_profs.setDisabled(True)

        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.profile_list.setDisabled(True)

        ## create subwidgets that will hold the individual GUI items
        self.left_data_frame = QWidget()
        self.right_map_frame = QWidget()
        ## set the layouts for these widgets
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.left_data_frame.setLayout(self.left_layout)
        self.right_map_frame.setLayout(self.right_layout)

        ## create dropdown menus
        models = sorted(self.data_sources.keys())
        self.model_dropdown = self.dropdown_menu(models)
        self.model_dropdown.setCurrentIndex(models.index(self.model))
        self.map_dropdown = self.dropdown_menu(['CONUS', 'Southeast', 'Central', 'West', 'Northeast', 'Europe', 'Asia'])
        times = self.data_sources[self.model].getAvailableTimes()
        self.run_dropdown = self.dropdown_menu([ t.strftime(MainWindow.run_format) for t in times ])
        self.run_dropdown.setCurrentIndex(times.index(self.run))

        ## connect the click actions to functions that do stuff
        self.model_dropdown.activated.connect(self.get_model)
        self.map_dropdown.activated.connect(self.get_map)
        self.run_dropdown.activated.connect(self.get_run)

        ## Create text labels to describe the various menus
        self.type_label = QLabel("Select Sounding Source")
        self.date_label = QLabel("Select Forecast Time")
        self.map_label = QLabel("Select Map Area")
        self.run_label = QLabel("Select Cycle")
        self.date_label.setDisabled(True)

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
        self.left_data_frame.setMaximumWidth(280)

        self.menuBar()

    def menuBar(self):

        self.bar = QMenuBar()
        self.filemenu = self.bar.addMenu("File")

        opendata = QAction("Open", self, shortcut=QKeySequence("Ctrl+O"))
        opendata.triggered.connect(self.openFile)
        self.filemenu.addAction(opendata)

        exit = QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"))
        exit.triggered.connect(self.exitApp)        
        self.filemenu.addAction(exit)

        pref = QAction("Preferences", self)
        self.filemenu.addAction(pref)

        self.helpmenu = self.bar.addMenu("Help")

        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)

        self.helpmenu.addAction(about)

    def exitApp(self):
        self.close()

    def openFile(self):
        self.link, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        self.model = "Archive"
        self.location = None
        self.prof_time = None
        self.run = None

        self.skewApp()

        ## default the sounding location to OUN because obviously I'm biased
        self.loc = None
        ## set the default profile to display
        self.prof_time = "Latest"
        ## the index of the item in the list that corresponds
        ## to the profile selected from the list
        self.prof_idx = []
        ## set the default profile type to Observed
        self.model = "Observed"
        ## this is the default model initialization time.
        self.run = "00Z"

    def aboutbox(self):

        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        msgBox.setText("SHARPpy\nSounding and Hodograph Research and Analysis Program for " +
                       "Python\n\n(C) 2014-%d by Kelton Halbert, Greg Blumberg, and Tim Supinie" % cur_year)
        msgBox.exec_()

    def create_map_view(self):
        """
        Create a clickable map that will be displayed in the GUI.
        Will eventually be re-written to be more general.

        Returns
        -------
        view : QWebView object
        """

        view = MapWidget(self.data_sources[self.model], self.run, self.async, width=800, height=500)
        view.clicked.connect(self.map_link)

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

    def update_list(self):
        """
        Update the list with new dates.

        :param list:
        :return:
        """

        if self.select_flag:
            self.select_all()
        self.profile_list.clear()
        self.prof_idx = []
        timelist = []

        fcst_hours = self.data_sources[self.model].getForecastHours()
        if fcst_hours != [ 0 ]:
            self.profile_list.setEnabled(True)
            self.all_profs.setEnabled(True)
            self.date_label.setEnabled(True)
            for fh in fcst_hours:
                fcst_str = (self.run + date.timedelta(hours=fh)).strftime(MainWindow.date_format) + "   (F%03d)" % fh
                timelist.append(fcst_str)
        else:
            self.profile_list.setDisabled(True)
            self.all_profs.setDisabled(True)
            self.date_label.setDisabled(True)

        for item in timelist:
            self.profile_list.addItem(item)
 
        self.profile_list.update()
        self.all_profs.setText("Select All")
        self.select_flag = False

    def update_run_dropdown(self):
        """
        Updates the dropdown menu that contains the model run
        information.
        :return:
        """

        getTimes = lambda: self.data_sources[self.model].getAvailableTimes()
        
        def update(times):
            times = times[0]
            self.run_dropdown.clear()

            if self.model == "Observed":
                self.run = [ t for t in times if t.hour in [ 0, 12 ] ][-1]
            else:
                self.run = times[-1]

            for data_time in times:
                self.run_dropdown.addItem(data_time.strftime(MainWindow.run_format))

            self.run_dropdown.update()
            self.run_dropdown.setCurrentIndex(times.index(self.run))

        self.async_id = self.async.post(getTimes, update)

    def map_link(self, point):
        """
        Change the text of the button based on the user click.
        """
        if point is None:
            self.loc = None
            self.disp_name = None
            self.button.setText('Generate Profiles')
        else:
            self.loc = point #url.toString().split('/')[-1]
            if point['icao'] != "":
                self.disp_name = point['icao']
            elif point['iata'] != "":
                self.disp_name = point['iata']
            else:
                self.disp_name = point['srcid'].upper()

            self.button.setText(self.disp_name + ' | Generate Profiles')

    def complete_name(self):
        """
        Handles what happens when the user clicks a point on the map
        """
        if self.loc is None:
            return
        else:
            self.prof_idx = []
            selected = self.profile_list.selectedItems()
            for item in selected:
                idx = self.profile_list.indexFromItem(item).row()
                if idx in self.prof_idx:
                    continue
                else:
                    self.prof_idx.append(idx)

            if len(self.prof_idx) > 0:
                self.prof_time = selected[0].text()
                if '   ' in self.prof_time:
                    self.prof_time = self.prof_time.split("   ")[0]
            else:
                self.prof_time = self.run.strftime(MainWindow.date_format)

            self.prof_idx.sort()
            self.skewApp()

    def get_model(self, index):
        """
        Get the user's model selection
        """
        self.model = self.model_dropdown.currentText()

        self.update_run_dropdown()
        self.update_list()

        self.async.join(self.async_id)
        self.view.setDataSource(self.data_sources[self.model], self.run)

    def get_run(self, index):
        """
        Get the user's run hour selection for the model
        """
        self.run = date.datetime.strptime(self.run_dropdown.currentText(), MainWindow.run_format)
        self.view.setCurrentTime(self.run)
        self.update_list()

    def get_map(self):
        """
        Get the user's map selection
        """
        pass

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

        items = [ self.profile_list.item(idx).text() for idx in self.prof_idx ]
        fhours = [ item.split("   ")[1].strip("()") if "   " in item else None for item in items ]

        profs = []
        dates = []
        failure = False

        exc = ""

        ## if the profile is an archived file, load the file from
        ## the hard disk
        if self.model == "Archive":
            try:
                profs, dates, stn_id = self.loadArchive()
                self.disp_name = stn_id
                self.prof_idx = range(len(dates))
            except Exception as e:
                exc = str(e)
                if debug:
                    print traceback.format_exc()
                failure = True

            run = None

        else:
        ## otherwise, download with the data thread
            if self.data_sources[self.model].getForecastHours() == [ 0 ]:
                self.prof_idx = [ 0 ]

            ret = loadData(self.data_sources[self.model], self.loc, self.run, self.prof_idx)

            if isinstance(ret[0], Exception):
                exc = str(ret[0])
                failure = True
            else:
                profs, dates = ret

            run = "%02dZ" % self.run.hour

        if failure:
            msgbox = QMessageBox()
            msgbox.setText("An error has occurred while retrieving the data.")
            msgbox.setInformativeText("This probably means the data are missing for some reason. Try another site or model or try again later.")
            msgbox.setDetailedText(exc)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.exec_()
        else:
            self.skew = SkewApp(profs, dates, self.model, location=self.disp_name,
                prof_time=self.prof_time, run=run, idx=self.prof_idx, fhour=fhours)
            self.skew.show()

    def loadArchive(self):
        """
        Get the archive sounding based on the user's selections.
        """

        try:
            dec = SPCDecoder(self.link)
        except:
            try:
                dec = BufDecoder(self.link)
            except:
                raise IOError("Could not figure out the format of '%s'!" % self.link)

        prof = dec.getProfiles()
        dates = dec.getProfileTimes()
        stn_id = dec.getStnId()

        return prof, dates, stn_id

@progress(MainWindow.async)
def loadData(data_source, loc, run, indexes, __text__=None, __prog__=None):
    if __text__ is not None:
        __text__.emit("Decoding File")

    url = data_source.getURL(loc, run)
    decoder = data_source.getDecoder(loc, run)
    dec = decoder(url)

    if __text__ is not None:
        __text__.emit("Creating Profiles")

    dates = dec.getProfileTimes(indexes)
    profs = dec.getProfiles(indexes, __prog__)

    return profs, dates

if __name__ == '__main__':
    win = MainWindow()
    win.show()
    win.setFocus()
    sys.exit(app.exec_())
