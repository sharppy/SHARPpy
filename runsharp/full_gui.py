import sys, os
import numpy as np
import warnings

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    debug = True
    sys.path.insert(0, os.path.normpath(os.getcwd() + "/.."))
else:
    debug = False
    np.seterr(all='ignore')
    warnings.simplefilter('ignore')

sys.path.insert(0, os.path.normpath(os.path.join(os.path.expanduser("~"), ".sharppy")))

from sharppy.viz import SPCWindow, MapWidget 
import sharppy.sharptab.profile as profile
from sharppy.io.spc_decoder import SPCDecoder
from sharppy.io.buf_decoder import BufDecoder
from sharppy.version import __version__, __version_name__
from datasources import data_source

from PySide.QtCore import *
from PySide.QtGui import *
import datetime as date
import traceback
from functools import wraps, partial
import hashlib
import cProfile
from os.path import expanduser
import ConfigParser
import Queue

class AsyncThreads(QObject):
    def __init__(self, max_threads):
        super(AsyncThreads, self).__init__()
        self.threads = {}
        self.callbacks = {}

        self.max_threads = max_threads
        self.running = 0
        self.queue = Queue.PriorityQueue(0)
        return

    def post(self, func, callback, *args, **kwargs):
        thd_id = self._genThreadId()

        background = kwargs.get('background', False)
        if 'background' in kwargs:
            del kwargs['background']

        thd = self._threadFactory(func, thd_id, *args, **kwargs)
        thd.finished.connect(self.finish)

        priority = 1 if background else 0
        self.queue.put((priority, thd_id))

        self.threads[thd_id] = thd
        if callback is None:
            callback = lambda x: x
        self.callbacks[thd_id] = callback

        if not background or self.running < self.max_threads:
            self.startNext()
        return thd_id

    def isFinished(self, thread_id):
        return not (thread_id in self.threads)

    def join(self, thread_id):
        while not self.isFinished(thread_id):
            QCoreApplication.processEvents()

    def clearQueue(self):
        self.queue = Queue.PriorityQueue(0)
        for thd_id, thd in self.threads.iteritems():
            if thd.isRunning():
                thd.terminate()

        self.threads = {}
        self.callbacks = {}

    def startNext(self):
        try:
            prio, thd_id = self.queue.get(block=False)
        except Queue.Empty:
            return

        self.threads[thd_id].start()
        self.running += 1

    @Slot(str, tuple)
    def finish(self, thread_id, ret_val):
        thd = self.threads[thread_id]
        callback = self.callbacks[thread_id]

        callback(ret_val)

        del self.threads[thread_id]
        del self.callbacks[thread_id]

        self.running -= 1
        if self.running < self.max_threads:
            # Might not be the case if we just started a high-priority thread
            self.startNext()

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

class progress(QObject):
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

class Picker(QWidget):
    date_format = "%Y-%m-%d %HZ"
    run_format = "%d %B %Y / %H%M UTC"

    async = AsyncThreads(2)

    def __init__(self, config, **kwargs):
        """
        Construct the main window and handle all of the
        necessary events. This window serves as the SHARPpy
        sounding picker - a means for interactively selecting
        which sounding profile(s) to view.
        """

        super(Picker, self).__init__(**kwargs)
        self.data_sources = data_source.loadDataSources()
        self.config = config
        self.skew = None

        ## default the sounding location to OUN because obviously I'm biased
        self.loc = None
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

        self.view = self.create_map_view()
        self.button = QPushButton('Generate Profiles')
        self.button.clicked.connect(self.complete_name)
        self.select_flag = False
        self.all_profs = QPushButton("Select All")
        self.all_profs.clicked.connect(self.select_all)
        self.all_profs.setDisabled(True)

        self.save_view_button = QPushButton('Save View as Default')
        self.save_view_button.clicked.connect(self.save_view)

        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.profile_list.setDisabled(True)

        ## create subwidgets that will hold the individual GUI items
        self.left_data_frame = QWidget()
        self.right_map_frame = QWidget()
        ## set the layouts for these widgets
        self.left_layout = QVBoxLayout()
        self.right_layout = QGridLayout() #QVBoxLayout()
        self.left_data_frame.setLayout(self.left_layout)
        self.right_map_frame.setLayout(self.right_layout)

        times = self.data_sources[self.model].getAvailableTimes()

        ## create dropdown menus
        models = sorted(self.data_sources.keys())
        self.model_dropdown = self.dropdown_menu(models)
        self.model_dropdown.setCurrentIndex(models.index(self.model))

        projs = [ ('npstere', 'Northern Hemisphere'), ('merc', 'Tropics'), ('spstere', 'Southern Hemisphere') ]
        if self.config.has_section('map'):
            proj = self.config.get('map', 'proj')
            proj_idx = zip(*projs)[0].index(proj)
        else:
            proj_idx = 0
        self.map_dropdown = self.dropdown_menu(zip(*projs)[1])
        self.map_dropdown.setCurrentIndex(proj_idx)

        self.run_dropdown = self.dropdown_menu([ t.strftime(Picker.run_format) for t in times ])
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
        self.right_layout.setColumnMinimumWidth(0, 500)
        self.right_layout.addWidget(self.map_label, 0, 0, 1, 1)
        self.right_layout.addWidget(self.save_view_button, 0, 1, 1, 1)
        self.right_layout.addWidget(self.map_dropdown, 1, 0, 1, 2)
        self.right_layout.addWidget(self.view, 2, 0, 1, 2)

        ## add the left and right sides to the main window
        self.layout.addWidget(self.left_data_frame, 0, 0, 1, 1)
        self.layout.addWidget(self.right_map_frame, 0, 1, 1, 1)
        self.left_data_frame.setMaximumWidth(280)

    def create_map_view(self):
        """
        Create a clickable map that will be displayed in the GUI.
        Will eventually be re-written to be more general.

        Returns
        -------
        view : QWebView object
        """

        view = MapWidget(self.data_sources[self.model], self.run, self.async, width=800, height=500, cfg=self.config)
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
                fcst_str = (self.run + date.timedelta(hours=fh)).strftime(Picker.date_format) + "   (F%03d)" % fh
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
                self.run_dropdown.addItem(data_time.strftime(Picker.run_format))

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

            fcst_hours = self.data_sources[self.model].getForecastHours()

            if fcst_hours != [0] and len(self.prof_idx) > 0 or fcst_hours == [0]:
                self.prof_idx.sort()
                self.skewApp()

    def get_model(self, index):
        """
        Get the user's model selection
        """
        self.model = self.model_dropdown.currentText()

        self.update_run_dropdown()
        self.async.join(self.async_id)

        self.update_list()
        self.view.setDataSource(self.data_sources[self.model], self.run)

    def get_run(self, index):
        """
        Get the user's run hour selection for the model
        """
        self.run = date.datetime.strptime(self.run_dropdown.currentText(), Picker.run_format)
        self.view.setCurrentTime(self.run)
        self.update_list()

    def get_map(self):
        """
        Get the user's map selection
        """
        proj = {'Northern Hemisphere':'npstere', 'Tropics':'merc', 'Southern Hemisphere':'spstere'}[self.map_dropdown.currentText()]
        self.view.setProjection(proj)

    def save_view(self):
        """
        Save the map projection to the config file
        """
        self.view.saveProjection(self.config)

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

    def skewApp(self, filename=None):
        """
        Create the SPC style SkewT window, complete with insets
        and magical funtimes.
        :return:
        """

        profs = []
        dates = []
        failure = False

        exc = ""

        ## if the profile is an archived file, load the file from
        ## the hard disk
        if filename is not None:
            model = "Archive"
            try:
                prof_collection, stn_id = self.loadArchive(filename)
                disp_name = stn_id
                prof_idx = range(len(dates))
            except Exception as e:
                exc = str(e)
                if debug:
                    print traceback.format_exc()
                failure = True

            run = None
            fhours = None
            observed = True
        else:
        ## otherwise, download with the data thread
            prof_idx = self.prof_idx
            disp_name = self.disp_name
            run = self.run
            model = self.model
            observed = self.data_sources[model].isObserved()

            if self.data_sources[model].getForecastHours() == [ 0 ]:
                prof_idx = [ 0 ]

            ret = loadData(self.data_sources[model], self.loc, run, prof_idx)

            if isinstance(ret[0], Exception):
                exc = str(ret[0])
                failure = True
            else:
                prof_collection = ret[0]

            run = "%02dZ" % run.hour
            fhours = [ "F%03d" % fh for idx, fh in enumerate(self.data_sources[self.model].getForecastHours()) if idx in prof_idx ]

        if failure:
            msgbox = QMessageBox()
            msgbox.setText("An error has occurred while retrieving the data.")
            msgbox.setInformativeText("This probably means the data are missing for some reason. Try another site or model or try again later.")
            msgbox.setDetailedText(exc)
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.exec_()
        else:
            prof_collection.setMeta('model', model)
            prof_collection.setMeta('run', run)
            prof_collection.setMeta('loc', disp_name)
            prof_collection.setMeta('fhour', fhours)
            prof_collection.setMeta('observed', observed)

            if not observed:
                prof_collection.setAsync(Picker.async)

            if self.skew is None:
                self.skew = SPCWindow(cfg=self.config)
                self.skew.closed.connect(self.skewAppClosed)
                self.skew.show()

            self.skew.raise_()
            self.skew.setFocus()
            self.skew.addProfileCollection(prof_collection)

    def skewAppClosed(self):
        self.skew = None

    def loadArchive(self, filename):
        """
        Get the archive sounding based on the user's selections.
        """

        try:
            dec = SPCDecoder(filename)
        except:
            try:
                dec = BufDecoder(filename)
            except:
                raise IOError("Could not figure out the format of '%s'!" % filename)

        profs = dec.getProfiles()
        stn_id = dec.getStnId()

        return profs, stn_id

@progress(Picker.async)
def loadData(data_source, loc, run, indexes, __text__=None, __prog__=None):

    if __text__ is not None:
        __text__.emit("Decoding File")

    url = data_source.getURL(loc, run)
    decoder = data_source.getDecoder(loc, run)
    dec = decoder(url)

    if __text__ is not None:
        __text__.emit("Creating Profiles")

    profs = dec.getProfiles(indexes=indexes)
    return profs

class Main(QMainWindow):
    HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")
    cfg_file_name = os.path.join(HOME_DIR,'sharppy.ini')

    def __init__(self):
        super(Main, self).__init__()

        ## All of these variables get set/reset by the various menus in the GUI
        self.config = ConfigParser.RawConfigParser()
        self.config.read(Main.cfg_file_name)

        self.__initUI()

    def __initUI(self):
        self.picker = Picker(self.config)
        self.setCentralWidget(self.picker)
        self.createMenuBar()
        
        ## set the window title
        self.setWindowTitle('SHARPpy Sounding Picker')
        
        self.show()
        self.raise_()

    def createMenuBar(self):
        bar = self.menuBar()
        filemenu = bar.addMenu("File")

        opendata = QAction("Open", self, shortcut=QKeySequence("Ctrl+O"))
        opendata.triggered.connect(self.openFile)
        filemenu.addAction(opendata)

        exit = QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"))
        exit.triggered.connect(self.exitApp)        
        filemenu.addAction(exit)

        pref = QAction("Preferences", self)
        filemenu.addAction(pref)

        helpmenu = bar.addMenu("Help")

        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)

        helpmenu.addAction(about)

    def exitApp(self):
        self.close()

    def openFile(self):
        if self.config.has_section('archive'):
            path = self.config.get('archive', 'path')
        else:
            path = expanduser('~')

        link, _ = QFileDialog.getOpenFileName(self, 'Open file', path)

        if link == '':
            return

        path, _ = os.path.split(link)
        if not self.config.has_section('archive'):
            self.config.add_section('archive')
        self.config.set('archive', 'path', path)

        self.picker.skewApp(filename=link)

    def aboutbox(self):
        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        str = """
        SHARPpy v%s %s

        Sounding and Hodograph Analysis and Research
        Program for Python

        (C) 2014-%d by Patrick Marsh, John Hart,
        Kelton Halbert, Greg Blumberg, and Tim Supinie.

        SHARPPy is a collection of open source sounding
        and hodograph analysis routines, a sounding
        plotting package, and an interactive application
        for analyzing real-time soundings all written in
        Python. It was developed to provide the
        atmospheric science community a free and
        consistent source of routines for convective
        indices. SHARPPy is constantly updated and
        vetted by professional meteorologists and
        climatologists within the scientific community to
        help maintain a standard source of sounding
        routines.

        Website: http://sharppy.github.io/SHARPpy/
        Contact: sharppy.project@gmail.com
        Contribute: https://github.com/sharppy/SHARPpy/
        """ % (__version__, __version_name__, cur_year)
        msgBox.setText(str)
        msgBox.exec_()

    def keyPressEvent(self, e):
        if e.matches(QKeySequence.Open):
            self.openFile()

        if e.matches(QKeySequence.Quit):
            self.exitApp()

    def closeEvent(self, e):
        self.config.write(open(Main.cfg_file_name, 'w'))

if __name__ == '__main__':
    # Create an application
    app = QApplication([])
    win = Main()
    sys.exit(app.exec_())
