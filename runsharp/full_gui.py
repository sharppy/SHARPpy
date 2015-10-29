import sys, os
import numpy as np
import warnings
import utils.frozenutils as frozenutils

HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    debug = True
    sys.path.insert(0, os.path.normpath(os.getcwd() + "/.."))
else:
    debug = False
    np.seterr(all='ignore')
    warnings.simplefilter('ignore')

if frozenutils.isFrozen():
    if not os.path.exists(HOME_DIR):
        os.makedirs(HOME_DIR)

    outfile = open(os.path.join(HOME_DIR, 'sharppy-out.txt'), 'w')

    sys.stdout = outfile
    sys.stderr = outfile
    
from sharppy.viz.SPCWindow import SPCWindow
from sharppy.viz.map import MapWidget 
from sharppy.viz.preferences import PrefDialog
import sharppy.sharptab.profile as profile
from sharppy.io.spc_decoder import SPCDecoder
from sharppy.io.buf_decoder import BufDecoder
from sharppy.io.arw_decoder import ARWDecoder
from sharppy.version import __version__, __version_name__
from datasources import data_source
from utils.async import AsyncThreads
from utils.progress import progress

from PySide.QtCore import *
from PySide.QtGui import *
import datetime as date
from functools import wraps, partial
import cProfile
from os.path import expanduser
import ConfigParser
import traceback
from functools import wraps, partial

try:
    from netCDF4 import Dataset
    nc = True
except:
    nc = False
    print "No netCDF4 Python install detected. Will not be able to open netCDF files on the local disk."

class crasher(object):
    def __init__(self, **kwargs):
        self._exit = kwargs.get('exit', False)

    def __get__(self, obj, cls):
        return partial(self.__call__, obj)

    def __call__(self, func):
        def doCrasher(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except:
                ret = None
                msg = "Well, this is embarrassing.\nSHARPpy broke. This is probably due to an issue with one of the data source servers, but if it keeps happening, send the detailed information to the developers."
                data = "SHARPpy v%s %s\n" % (__version__, __version_name__) + \
                       "Crash time: %s\n" % str(date.datetime.now()) + \
                       traceback.format_exc()

                if frozenutils.isFrozen():
                    msg1, msg2 = msg.split("\n")

                    msgbox = QMessageBox()
                    msgbox.setText(msg1)
                    msgbox.setInformativeText(msg2)
                    msgbox.setDetailedText(data)
                    msgbox.setIcon(QMessageBox.Critical)
                    msgbox.exec_()
                else:
                    print
                    print msg
                    print
                    print "Detailed Information:"
                    print data

                if self._exit:
                    sys.exit(1)
            return ret
        return doCrasher

class Picker(QWidget):
    date_format = "%Y-%m-%d %HZ"
    run_format = "%d %B %Y / %H%M UTC"

    async = AsyncThreads(2, debug)

    def __init__(self, config, **kwargs):
        """
        Construct the main picker widget: a means for interactively selecting
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
        ## this is the default model initialization time
        self.run = [ t for t in self.data_sources[self.model].getAvailableTimes() if t.hour in [0, 12] ][-1]

        urls = data_source.pingURLs(self.data_sources)
        self.has_connection = any( urls.values() )

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
        self.view.hasInternet(self.has_connection)

        self.button = QPushButton('Generate Profiles')
        self.button.clicked.connect(self.complete_name)
        self.button.setDisabled(True)

        self.select_flag = False
        self.all_profs = QPushButton("Select All")
        self.all_profs.clicked.connect(self.select_all)
        self.all_profs.setDisabled(True)

        self.save_view_button = QPushButton('Save Map View as Default')
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
        try:
            self.run_dropdown.setCurrentIndex(times.index(self.run))
        except ValueError:
            print "Run dropdown is missing its times ... ?"
            print times

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
            self.button.setDisabled(True)
        elif self.model == "Local WRF-ARW":
            self.loc = point
            self.disp_name = "User Selected"
            self.button.setText(self.disp_name + ' | Generate Profiles')
            self.button.setEnabled(True)
            self.areal_lon, self.areal_y = point

        else:
            self.loc = point #url.toString().split('/')[-1]
            if point['icao'] != "":
                self.disp_name = point['icao']
            elif point['iata'] != "":
                self.disp_name = point['iata']
            else:
                self.disp_name = point['srcid'].upper()

            self.button.setText(self.disp_name + ' | Generate Profiles')
            if self.has_connection:
                self.button.setEnabled(True) 

    @crasher(exit=False)
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
            prof_collection, stn_id = self.loadArchive(filename)
            disp_name = stn_id
            prof_idx = range(len(dates))

            run = prof_collection.getCurrentDate()
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
                exc = ret[0]
                failure = True
            else:
                prof_collection = ret[0]

            fhours = [ "F%03d" % fh for idx, fh in enumerate(self.data_sources[self.model].getForecastHours()) if idx in prof_idx ]

        if not failure:
            prof_collection.setMeta('model', model)
            prof_collection.setMeta('run', run)
            prof_collection.setMeta('loc', disp_name)
            prof_collection.setMeta('fhour', fhours)
            prof_collection.setMeta('observed', observed)

            if not observed:
                # If it's not an observed profile, then generate profile objects in background.
                prof_collection.setAsync(Picker.async)

            if self.skew is None:
                # If the SPCWindow isn't shown, set it up.
                self.skew = SPCWindow(parent=self.parent(), cfg=self.config)
                self.skew.closed.connect(self.skewAppClosed)
                self.skew.show()

            self.focusSkewApp()
            self.skew.addProfileCollection(prof_collection)

    def skewAppClosed(self):
        """
        Handles the user closing the SPC window.
        """
        self.skew = None

    def focusSkewApp(self):
        if self.skew is not None:
            self.skew.activateWindow()
            self.skew.setFocus()
            self.skew.raise_()

    def loadArchive(self, filename):
        """
        Get the archive sounding based on the user's selections.
        Also reads it using the Decoders and gets both the stationID and the profile objects
        for that archive sounding.
        """

        try:
            dec = SPCDecoder(filename)
        except Exception as e:
            try:
                dec = BufDecoder(filename)
            except:
                raise IOError("Could not figure out the format of '%s'!" % filename)

        profs = dec.getProfiles()
        stn_id = dec.getStnId()

        return profs, stn_id

    def hasConnection(self):
        return self.has_connection

@progress(Picker.async)
def loadData(data_source, loc, run, indexes, __text__=None, __prog__=None):
    """
    Loads the data from a remote source. Has hooks for progress bars.
    """
    if __text__ is not None:
        __text__.emit("Decoding File")
    if data_source.getName() == "Local WRF-ARW":
        url = data_source.getURLList(outlet="Local")[0].replace("file://", "")
        decoder = ARWDecoder
        dec = decoder((url, loc[0], loc[1]))
    else:
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
        """
        Initializes the window and reads in the configuration from the file.
        """
        super(Main, self).__init__()

        ## All of these variables get set/reset by the various menus in the GUI
        self.config = ConfigParser.RawConfigParser()
        self.config.read(Main.cfg_file_name)
        if not self.config.has_section('paths'):
            self.config.add_section('paths')
            self.config.set('paths', 'load_txt', expanduser('~'))
        PrefDialog.initConfig(self.config)

        self.__initUI()

    def __initUI(self):
        """
        Puts the user inteface together
        """
        self.picker = Picker(self.config, parent=self)
        self.setCentralWidget(self.picker)
        self.createMenuBar()
        
        ## set the window title
        window_title = 'SHARPpy Sounding Picker'
        self.setWindowTitle(window_title)
        
        self.show()
        self.raise_()

    def createMenuBar(self):
        """
        Creates the menu bar
        """
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
        pref.triggered.connect(self.preferencesbox)

        helpmenu = bar.addMenu("Help")

        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)

        helpmenu.addAction(about)

    def exitApp(self):
        self.close()

    @crasher(exit=False)
    def openFile(self):
        """
        Opens a file on the local disk.
        """
        path = self.config.get('paths', 'load_txt')

        link, _ = QFileDialog.getOpenFileNames(self, 'Open file', path)
        
        if len(link) == 0 or link[0] == '':
            return

        path = os.path.dirname(link[0])
        self.config.set('paths', 'load_txt', path)

        # Loop through all of the files selected and load them into the SPCWindow
        if link[0].endswith("nc") and nc:
           ncfile = Dataset(link[0])
         
           xlon1 = ncfile.variables["XLONG"][0][:, 0]
           xlat1 = ncfile.variables["XLAT"][0][:, 0]

           xlon2 = ncfile.variables["XLONG"][0][:, -1]
           xlat2 = ncfile.variables["XLAT"][0][:, -1]

           xlon3 = ncfile.variables["XLONG"][0][0, :]
           xlat3 = ncfile.variables["XLAT"][0][0, :]

           xlon4 = ncfile.variables["XLONG"][0][-1, :]
           xlat4 = ncfile.variables["XLAT"][0][-1, :]

           delta = ncfile.variables["XTIME"][1] / 60.
           maxt = ncfile.variables["XTIME"][-1] / 60.


           ## write the CSV file 
           csvfile = open(HOME_DIR + "/datasources/wrf-arw.csv", 'w')
           csvfile.write("icao,iata,synop,name,state,country,lat,lon,elev,priority,srcid\n")

           for idx, val in np.ndenumerate(xlon1):
               lat = xlat1[idx]
               lon = xlon1[idx]
               csvfile.write(",,,,,," + str(lat) + "," + str(lon) + ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
           for idx, val in np.ndenumerate(xlon2):
               lat = xlat2[idx]
               lon = xlon2[idx]
               csvfile.write(",,,,,," + str(lat) + "," + str(lon) + ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
           for idx, val in np.ndenumerate(xlon3):
               lat = xlat3[idx]
               lon = xlon3[idx]
               csvfile.write(",,,,,," + str(lat) + "," + str(lon) + ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
           for idx, val in np.ndenumerate(xlon4):
               lat = xlat4[idx]
               lon = xlon4[idx]
               csvfile.write(",,,,,," + str(lat) + "," + str(lon) + ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
           csvfile.close()

           ## write the xml file
           xmlfile = open(HOME_DIR + "/datasources/wrf-arw.xml", 'w')
           xmlfile.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
           xmlfile.write('<sourcelist>\n')
           xmlfile.write('    <datasource name="Local WRF-ARW" ensemble="false" observed="false">\n')
           xmlfile.write('        <outlet name="Local" url="file://' + link[0] + '" format="wrf-arw">\n')
           xmlfile.write('            <time range="' + str(int(maxt)) + '" delta="' + str(int(delta)) + '" offset="0" delay="0" cycle="24" archive="1"/>\n')
           xmlfile.write('            <points csv="wrf-arw.csv" />\n')
           xmlfile.write('        </outlet>\n')
           xmlfile.write('    </datasource>\n')
           xmlfile.write('</sourcelist>\n')
           xmlfile.close()
        else: 
            for l in link:
                self.picker.skewApp(filename=l)

    def aboutbox(self):
        """
        Creates and shows the "about" box.
        """
        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        str = """
        SHARPpy v%s %s

        Sounding and Hodograph Analysis and Research
        Program for Python

        (C) 2014-%d by Patrick Marsh, John Hart,
        Kelton Halbert, Greg Blumberg, and Tim Supinie.

        SHARPpy is a collection of open source sounding
        and hodograph analysis routines, a sounding
        plotting package, and an interactive application
        for analyzing real-time soundings all written in
        Python. It was developed to provide the
        atmospheric science community a free and
        consistent source of routines for analyzing sounding
        data. SHARPpy is constantly updated and
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

    def preferencesbox(self):
        pref_dialog = PrefDialog(self.config, parent=self)
        pref_dialog.exec_()

    def keyPressEvent(self, e):
        """
        Handles key press events sent to the picker window.
        """
        if e.matches(QKeySequence.Open):
            self.openFile()

        if e.matches(QKeySequence.Quit):
            self.exitApp()

        if e.key() == Qt.Key_W:
            self.picker.focusSkewApp()

    def closeEvent(self, e):
        """
        Handles close events (gets called when the window closes).
        """
        self.config.write(open(Main.cfg_file_name, 'w'))

def main():
    @crasher(exit=True)
    def createWindow():
        return Main()

    # Create an application
    app = QApplication([])
    win = createWindow()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
