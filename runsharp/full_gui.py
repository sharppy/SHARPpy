import os
os.environ['QT_API'] = 'pyside2' # Force PySide2 to be used in QtPy
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
from sharppy.viz.map import MapWidget
import argparse
import traceback
from sutils.config import Config
from os.path import expanduser
import cProfile
from functools import wraps, partial
import datetime as date

from sutils.progress import progress
from sutils.async_threads import AsyncThreads
from sutils.ver_updates import check_latest
from datasources import data_source
from sharppy.io.arw_decoder import ARWDecoder
from sharppy.io.decoder import getDecoders
import sharppy.sharptab.profile as profile
from sharppy.viz.preferences import PrefDialog
from sharppy.viz.SPCWindow import SPCWindow
from sharppy._version import get_versions
import sys
import glob as glob
import numpy as np
import warnings
import sutils.frozenutils as frozenutils
import logging
import qtpy
import platform

HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")
NUCAPS_times_file = os.path.join(HOME_DIR, "datasources", "nucapsTimes.txt") # JTS
LOG_FILE = os.path.join(HOME_DIR, 'sharppy.log')
if not os.path.isdir(HOME_DIR):
    os.mkdir(HOME_DIR)

if os.path.exists(LOG_FILE):
    log_file_size = os.path.getsize(LOG_FILE)
    MAX_FILE_SIZE = 1024 * 1024
    if log_file_size > MAX_FILE_SIZE:
        # Delete the log file as it's grown too large
        os.remove(LOG_FILE)

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Start the logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(pathname)s %(funcName)s Line #: %(lineno)d %(levelname)-8s %(message)s',
                    filename=LOG_FILE,
                    filemode='w')
console = logging.StreamHandler()
# set a format which is simpler for console use
formatter = logging.Formatter(
    '%(asctime)s %(pathname)s %(funcName)s Line #: %(lineno)d %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

if len(sys.argv) > 1 and '--debug' in sys.argv:
    debug = True
    sys.path.insert(0, os.path.normpath(os.getcwd() + "/.."))
    console.setLevel(logging.DEBUG)
else:
    console.setLevel(logging.CRITICAL)
    debug = False
    np.seterr(all='ignore')
    warnings.simplefilter('ignore')

if frozenutils.isFrozen():
    if not os.path.exists(HOME_DIR):
        os.makedirs(HOME_DIR)
    BINARY_VERSION = True
    outfile = open(os.path.join(HOME_DIR, 'sharppy-out.txt'), 'w')
    console.setLevel(logging.DEBUG)
    sys.stdout = outfile
    sys.stderr = outfile
else:
    BINARY_VERSION = False

__version__ = get_versions()['version']
ver = get_versions()
del get_versions

logging.info('Started logging output for SHARPpy')
logging.info('SHARPpy version: ' + str(__version__))
logging.info('numpy version: ' + str(np.__version__))
logging.info('qtpy version: ' + str(qtpy.__version__))
logging.info("Python version: " + str(platform.python_version()))
logging.info("Qt version: " + str(qtpy.QtCore.__version__))
logging.info("OS version: " + str(platform.platform()))
# from sharppy._version import __version__#, __version_name__

if BINARY_VERSION:
    logging.info("This is a binary version of SHARPpy.")

__version_name__ = 'Andover'
try:
    from netCDF4 import Dataset
    has_nc = True
except ImportError:
    has_nc = False
    logging.info("No netCDF4 Python install detected.")


def versioning_info(include_sharppy=False):
    txt = ""
    if include_sharppy is True:
        txt += "SHARPpy version: " + str(__version__) + '\n'
    txt += "Numpy version: " + str(np.__version__) + '\n'
    txt += "Python version: " + str(platform.python_version()) + '\n'
    txt += "PySide/Qt version: " + str(qtpy.QtCore.__version__)
    return txt

class crasher(object):
    def __init__(self, **kwargs):
        self._exit = kwargs.get('exit', False)

    def __get__(self, obj, cls):
        return partial(self.__call__, obj)

    def __call__(self, func):
        def doCrasher(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                ret = None
                msg = "Well, this is embarrassing.\nSHARPpy broke. This is probably due to an issue with one of the data source servers, but if it keeps happening, send the detailed information to the developers."
                data = "SHARPpy v%s %s\n" % (__version__, __version_name__) + \
                       "Crash time: %s\n" % str(date.datetime.now()) + \
                       traceback.format_exc()
                logging.exception(e)
                print("Exception:", e)
                # HERE IS WHERE YOU CAN CATCH A DATAQUALITYEXCEPTION
                if frozenutils.isFrozen():
                    msg1, msg2 = msg.split("\n")

                    msgbox = QMessageBox()
                    msgbox.setText(msg1)
                    msgbox.setInformativeText(msg2)
                    msgbox.setDetailedText(data)
                    msgbox.setIcon(QMessageBox.Critical)
                    msgbox.exec_()
                else:
                    print()
                    print(msg)
                    print()
                    print("Detailed Information:")
                    print(data)

                # Check the flag that indicates if the program should exit when it crashes
                if self._exit:
                    sys.exit(1)
            return ret
        return doCrasher


class Calendar(QCalendarWidget):
    def __init__(self, *args, **kwargs):
        dt_earliest = kwargs.pop('dt_earliest', date.datetime(1946, 1, 1))
        dt_avail = kwargs.pop('dt_avail', date.datetime.utcnow().replace(
            minute=0, second=0, microsecond=0))
        self.max_date = dt_avail.date()
        super(Calendar, self).__init__(*args, **kwargs)

        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        self.setEarliestAvailable(dt_earliest)
        self.setLatestAvailable(dt_avail)

        for day in [Qt.Sunday, Qt.Saturday]:
            txt_fmt = self.weekdayTextFormat(day)
            txt_fmt.setForeground(QBrush(Qt.black))
            self.setWeekdayTextFormat(day, txt_fmt)

    def paintCell(self, painter, rect, date):
        QCalendarWidget.paintCell(self, painter, rect, date)
        if date.toPython() > self.max_date or date.toPython() < self.min_date:
            color = QColor('#808080')
            color.setAlphaF(0.5)
            painter.fillRect(rect, color)

    def setLatestAvailable(self, dt_avail):
        qdate_avail = QDate(dt_avail.year, dt_avail.month, dt_avail.day)
        #self.setMaximumDate(qdate_avail)
        self.max_date = qdate_avail.toPython()
        #if self.selectedDate().toPython() > qdate_avail.toPython():
        ##    self.setSelectedDate(qdate_avail)
        #else:
        self.setSelectedDate(self.selectedDate())

    def setEarliestAvailable(self, dt_earliest):
        qdate_earliest = QDate(dt_earliest.year, dt_earliest.month, dt_earliest.day)
        self.min_date = dt_earliest.date()
        #self.setMinimumDate(qdate_earliest)


class Picker(QWidget):
    date_format = "%Y-%m-%d %HZ"
    run_format = "%d %B %Y / %H%M UTC"

    async_obj = AsyncThreads(2, debug)

    def __init__(self, config, **kwargs):
        """
        Construct the main picker widget: a means for interactively selecting
        which sounding profile(s) to view.
        """
        super(Picker, self).__init__(**kwargs)
        self.data_sources = data_source.loadDataSources()
        self.config = config
        self.skew = None

        # default the sounding location to OUN because obviously I'm biased
        self.loc = None
        # the index of the item in the list that corresponds
        # to the profile selected from the list
        self.prof_idx = []
        # set the default profile type to Observed
        self.model = "Observed"
        # this is the default model initialization time
        self.all_times = sorted(self.data_sources[self.model].getAvailableTimes())
        self.run = [t for t in self.all_times if t.hour in [0, 12]][-1]

        urls = data_source.pingURLs(self.data_sources)
        self.has_connection = any(urls.values())
        self.strictQC = True

        # JTS - list all overpass times for the selected day
        self.nucaps_daily_times = []

        # initialize the UI
        self.__initUI()

    def __initUI(self):
        """
        Initialize the main user interface.
        """

        # Give the main window a layout. Using GridLayout
        # in order to control placement of objects.

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

        # create subwidgets that will hold the individual GUI items
        self.left_data_frame = QWidget()
        self.right_map_frame = QWidget()
        # set the layouts for these widgets
        self.left_layout = QVBoxLayout()
        self.right_layout = QGridLayout()  # QVBoxLayout()
        self.left_data_frame.setLayout(self.left_layout)

        self.right_map_frame.setLayout(self.right_layout)
        #print(self.run)
        self.cal = Calendar(self, dt_avail=self.run)
        self.cal.setSelectedDate(self.run)
        self.cal.clicked.connect(self.update_from_cal)
        self.cal_date = self.cal.selectedDate()
        filt_times = [t for t in self.all_times if t.day == self.cal_date.day(
        ) and t.year == self.cal_date.year() and t.month == self.cal_date.month()]

        # create dropdown menus
        models = sorted(self.data_sources.keys())
        self.model_dropdown = self.dropdown_menu(models)
        self.model_dropdown.setCurrentIndex(models.index(self.model))

        # Setup the map
        projs = [('npstere', 'Northern Hemisphere'),
                 ('merc', 'Tropics'), ('spstere', 'Southern Hemisphere')]
        if ('map', 'proj') in self.config:
            proj = self.config['map', 'proj']
            proj_idx = list(zip(*projs))[0].index(proj)
        else:
            proj_idx = 0
        self.map_dropdown = self.dropdown_menu(list(zip(*projs))[1])
        self.map_dropdown.setCurrentIndex(proj_idx)

        # Set up the run dropdown box and select the correct index
        self.run_dropdown = self.dropdown_menu(
            [t.strftime(Picker.run_format) for t in filt_times])

        try:
            self.run_dropdown.setCurrentIndex(filt_times.index(self.run))
        except ValueError as e:
            logging.error("Run dropdown is missing its times ... ?")
            logging.exception(e)

        # connect the click actions to functions that do stuff
        self.model_dropdown.activated.connect(self.get_model)
        self.map_dropdown.activated.connect(self.get_map)
        self.run_dropdown.activated.connect(self.get_run)

        # Create text labels to describe the various menus
        self.type_label = QLabel("Select Sounding Source")
        self.date_label = QLabel("Select Forecast Time")
        self.map_label = QLabel("Select Map Area")
        self.run_label = QLabel("Select Cycle")
        self.date_label.setDisabled(True)

        # add the elements to the left side of the GUI
        self.left_layout.addWidget(self.type_label)
        self.left_layout.addWidget(self.model_dropdown)
        self.left_layout.addWidget(self.run_label)
        self.left_layout.addWidget(self.cal)
        self.left_layout.addWidget(self.run_dropdown)
        self.left_layout.addWidget(self.date_label)
        self.left_layout.addWidget(self.profile_list)
        self.left_layout.addWidget(self.all_profs)
        self.left_layout.addWidget(self.button)

        # add the elements to the right side of the GUI
        self.right_layout.setColumnMinimumWidth(0, 500)
        self.right_layout.addWidget(self.map_label, 0, 0, 1, 1)
        self.right_layout.addWidget(self.save_view_button, 0, 1, 1, 1)
        self.right_layout.addWidget(self.map_dropdown, 1, 0, 1, 2)
        self.right_layout.addWidget(self.view, 2, 0, 1, 2)

        # add the left and right sides to the main window
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

        # minimumWidth=800, minimumHeight=500,
        view = MapWidget(
            self.data_sources[self.model], self.run, self.async_obj, cfg=self.config)
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
        logging.debug("Calling full_gui.dropdown_menu")
        # create the dropdown menu
        dropdown = QComboBox()
        # set the text as editable so that it can have centered text
        dropdown.setEditable(True)
        dropdown.lineEdit().setReadOnly(True)
        dropdown.lineEdit().setAlignment(Qt.AlignCenter)

        # add each item in the list to the dropdown
        for item in item_list:
            dropdown.addItem(item)

        return dropdown

    def update_from_cal(self, dt, updated_model=False):
        """
        Update the dropdown list and the forecast times list if a new date
        is selected in the calendar app.
        """

        self.update_run_dropdown(updated_model=updated_model)

        self.view.setDataSource(self.data_sources[self.model], self.run)
        self.update_list()

    def update_list(self):
        """
        Update the list with new forecast times.

        :param list:
        :return:
        """
        logging.debug("Calling full_gui.update_list")
        if self.select_flag:
            self.select_all()
        self.profile_list.clear()
        self.prof_idx = []
        timelist = []

        # If the run is outside the available times.
        if self.run == date.datetime(1700, 1, 1, 0, 0, 0):
            self.profile_list.setDisabled(True)
            self.all_profs.setDisabled(True)
            self.date_label.setDisabled(True)
        else:
            fcst_hours = self.data_sources[self.model].getForecastHours()
            if fcst_hours != [0]:
                self.profile_list.setEnabled(True)
                self.all_profs.setEnabled(True)
                self.date_label.setEnabled(True)
                for fh in fcst_hours:
                    fcst_str = (self.run + date.timedelta(hours=fh)
                                ).strftime(Picker.date_format) + "   (F%03d)" % fh
                    timelist.append(fcst_str)
            else:
                self.profile_list.setDisabled(True)
                self.all_profs.setDisabled(True)
                self.date_label.setDisabled(True)

        # Loop throught the timelist and each string to the list
        for item in timelist:
            self.profile_list.addItem(item)

        self.profile_list.update()
        self.all_profs.setText("Select All")
        self.select_flag = False

    def update_datasource_dropdown(self, selected="Observed"):
        """
        Updates the dropdown menu that contains the available
        data sources
        :return:
        """
        logging.debug("Calling full_gui.update_datasource_dropdown")

        for i in range(self.model_dropdown.count()):
            self.model_dropdown.removeItem(0)

        self.data_sources = data_source.loadDataSources()
        models = sorted(self.data_sources.keys())
        for model in models:
            self.model_dropdown.addItem(model)

        self.model_dropdown.setCurrentIndex(models.index(selected))
        self.get_model(models.index(selected))

    def update_run_dropdown(self, updated_model=False):
        """
        Updates the dropdown menu that contains the model run
        information.
        :return:
        """
        logging.debug("Calling full_gui.update_run_dropdown")

        if self.model.startswith("Local"):
            url = self.data_sources[self.model].getURLList(
                outlet="Local")[0].replace("file://", "")

            def getTimes():
                return self.data_sources[self.model].getAvailableTimes(url)
        else:
            def getTimes():
                return self.data_sources[self.model].getAvailableTimes(dt=self.cal_date)

        self.cal_date = self.cal.selectedDate()

        # Function to update the times.
        def update(times):
            self.run_dropdown.clear()  # Clear all of the items from the dropdown
            times = times[0]
            time_span = self.data_sources[self.model].updateTimeSpan()
            for outlet in time_span:
                if np.asarray(outlet).all() == None:
                    span = True
                else:
                    dt_earliest = outlet[0]
                    dt_avail = outlet[1]
                    span = False
            if span is True and len(times) > 0:
                dt_avail = max(times)
                dt_earliest = min(times)
            self.cal.setLatestAvailable(dt_avail)
            self.cal.setEarliestAvailable(dt_earliest)
            self.cal_date = self.cal.selectedDate()
            self.cal.update()

            # Filter out only times for the specified date.
            filtered_times = []
            for i, data_time in enumerate(times):
                if data_time.day == self.cal_date.day() and data_time.year == self.cal_date.year() and data_time.month == self.cal_date.month():
                    self.run_dropdown.addItem(data_time.strftime(Picker.run_format))
                    filtered_times.append(i)

            if len(filtered_times) > 0:
                filtered_times = np.sort(np.asarray(filtered_times))
                times = times[filtered_times.min(): filtered_times.max()+1]
                # Pick the index for which to highlight
                if self.model == "Observed":
                    try:
                        # Try to grab the 0 or 12 UTC data for this day (or 3 or 15 if before 5/1/1957)
                        if self.cal_date.toPython() >= date.datetime(1957,5,1).date():
                            synoptic_times = [0,12]
                        else:
                            synoptic_times = [3,15]
                        self.run = [t for t in times if t.hour in synoptic_times and t.day == self.cal_date.day(
                        ) and t.month == self.cal_date.month() and t.year == self.cal_date.year()][-1]
                    except Exception as e:
                        logging.exception(e)
                        self.run = times[-1]
                else:
                    self.run = times[-1]
            else:
                self.run = date.datetime(1700, 1, 1, 0, 0, 0)
            self.run_dropdown.update()

            if len(filtered_times) > 0:
                # JTS -  Handle how real-time and off-line NUCAPS data is displayed.
                if self.model == "NUCAPS Case Study NOAA-20" \
                    or self.model == "NUCAPS Case Study Suomi-NPP" \
                    or self.model == "NUCAPS Case Study Aqua" \
                    or self.model == "NUCAPS Case Study MetOp-A" \
                    or self.model == "NUCAPS Case Study MetOp-B" \
                    or self.model == "NUCAPS Case Study MetOp-C":
                    self.run_dropdown.clear()
                    self.run_dropdown.addItem(self.tr("- Viewing archived data - "))
                    self.run_dropdown.setCurrentIndex(0)
                    self.run_dropdown.update()
                    self.run_dropdown.setEnabled(False)
                elif self.model == "NUCAPS CONUS NOAA-20" \
                    or self.model == "NUCAPS CONUS Suomi-NPP" \
                    or self.model == "NUCAPS CONUS Aqua" \
                    or self.model == "NUCAPS CONUS MetOp-A" \
                    or self.model == "NUCAPS CONUS MetOp-B" \
                    or self.model == "NUCAPS CONUS MetOp-C" \
                    or self.model == "NUCAPS Caribbean NOAA-20" \
                    or self.model == "NUCAPS Caribbean Suomi-NPP" \
                    or self.model == "NUCAPS Caribbean Aqua" \
                    or self.model == "NUCAPS Caribbean MetOp-A" \
                    or self.model == "NUCAPS Caribbean MetOp-B" \
                    or self.model == "NUCAPS Caribbean MetOp-C" \
                    or self.model == "NUCAPS Alaska NOAA-20" \
                    or self.model == "NUCAPS Alaska Suomi-NPP" \
                    or self.model == "NUCAPS Alaska Aqua" \
                    or self.model == "NUCAPS Alaska MetOp-A" \
                    or self.model == "NUCAPS Alaska MetOp-B" \
                    or self.model == "NUCAPS Alaska MetOp-C":

                    # Load the empty csv for days that have no data and refresh the map.
                    self.data_sources = data_source.loadDataSources()
                    self.run_dropdown.setCurrentIndex(times.index(self.run))
                    self.run_dropdown.update()
                    self.run_dropdown.setEnabled(True)

                    # Re-acquire the list of available times for the newly-selected data source.
                    self.nucaps_daily_times = times
                else:
                    self.run_dropdown.setCurrentIndex(times.index(self.run))
                    self.run_dropdown.update()
                    self.run_dropdown.setEnabled(True)
            elif len(filtered_times) == 0:
                if self.model == "Observed" \
                    or self.model == "NUCAPS Case Study NOAA-20" \
                    or self.model == "NUCAPS Case Study Suomi-NPP" \
                    or self.model == "NUCAPS Case Study Aqua" \
                    or self.model == "NUCAPS Case Study MetOp-A" \
                    or self.model == "NUCAPS Case Study MetOp-B" \
                    or self.model == "NUCAPS Case Study MetOp-C":
                    string = "obs"
                elif self.model == "NUCAPS CONUS NOAA-20" \
                    or self.model == "NUCAPS CONUS Suomi-NPP" \
                    or self.model == "NUCAPS CONUS Aqua" \
                    or self.model == "NUCAPS CONUS MetOp-A" \
                    or self.model == "NUCAPS CONUS MetOp-B" \
                    or self.model == "NUCAPS CONUS MetOp-C" \
                    or self.model == "NUCAPS Caribbean NOAA-20" \
                    or self.model == "NUCAPS Caribbean Suomi-NPP" \
                    or self.model == "NUCAPS Caribbean Aqua" \
                    or self.model == "NUCAPS Caribbean MetOp-A" \
                    or self.model == "NUCAPS Caribbean MetOp-B" \
                    or self.model == "NUCAPS Caribbean MetOp-C" \
                    or self.model == "NUCAPS Alaska NOAA-20" \
                    or self.model == "NUCAPS Alaska Suomi-NPP" \
                    or self.model == "NUCAPS Alaska Aqua" \
                    or self.model == "NUCAPS Alaska MetOp-A" \
                    or self.model == "NUCAPS Alaska MetOp-B" \
                    or self.model == "NUCAPS Alaska MetOp-C":
                    # Load the empty csv for days that have no data and refresh the map.
                    string = "obs"
                    self.data_sources = data_source.loadDataSources()
                else:
                    string = "runs"
                self.run_dropdown.addItem(self.tr("- No " + string + " available - "))
                self.run_dropdown.setCurrentIndex(0)
                self.run_dropdown.update()
                self.run_dropdown.setEnabled(False)

        # Post the getTimes to update.  This will re-write the list of times in the dropdown box that
        # match the date selected in the calendar.
        async_id = self.async_obj.post(getTimes, update)
        self.async_obj.join(async_id)

    def map_link(self, point):
        """
        Change the text of the button based on the user click.
        """
        logging.debug("Calling full_gui.map_link")

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
            self.loc = point  # url.toString().split('/')[-1]
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
        logging.debug("Calling full_gui.complete_name")
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
                n_tries = 0
                while True:
                    try:
                        self.skewApp(ntry=n_tries)
                    except data_source.DataSourceError as e1:
                        # We've run out of data sources. Uh-oh.
                        logging.exception(e1)
                        if self.skew is not None:
                            self.skew.closeIfEmpty()
                        raise IOError("No outlet found with the requested profile!")
                    except Exception as e:
                        if debug:
                            print(traceback.format_exc())
                        n_tries += 1
                        logging.exception(e)
                    else:
                        break

    def get_model(self, index):
        """
        Get the user's model selection
        """
        logging.debug("Calling full_gui.get_model")

        self.model = self.model_dropdown.currentText()

        self.update_from_cal(None, updated_model=True)
        self.run_label.setEnabled(True)
        self.cal.setEnabled(True)

    def get_run(self, index):
        """
        Get the user's run hour selection for the model
        """
        logging.debug("Calling full_gui.get_run")

        # JTS - The region and satID strings will be used to construct the dynamic path to the csv files in data_source.py.
        if self.model == "NUCAPS CONUS NOAA-20":
            region = 'conus'
            satID = 'j01'
        elif self.model == "NUCAPS CONUS Aqua":
            region = 'conus'
            satID = 'aq0'
        elif self.model == "NUCAPS CONUS MetOp-A":
            region = 'conus'
            satID = 'm02'
        elif self.model == "NUCAPS CONUS MetOp-B":
            region = 'conus'
            satID = 'm01'
        elif self.model == "NUCAPS CONUS MetOp-C":
            region = 'conus'
            satID = 'm03'
        elif self.model == "NUCAPS Caribbean NOAA-20":
            region = 'caribbean'
            satID = 'j01'
        elif self.model == "NUCAPS Alaska NOAA-20":
            region = 'alaska'
            satID = 'j01'

        # Write the data source, region, satellite ID, year, month, day and time info to a temporary text file.
        if self.model.startswith("NUCAPS"):
            nucaps_year = self.cal_date.year()
            nucaps_month = None
            nucaps_day = None

            if self.cal_date.month() < 10:
                nucaps_month = f'0{self.cal_date.month()}'
            else:
                nucaps_month = self.cal_date.month()
            if self.cal_date.day() < 10:
                nucaps_day = f'0{self.cal_date.day()}'
            else:
                nucaps_day = self.cal_date.day()

            nucaps_time = self.run_dropdown.currentText()[-8:-4]
            selected_ds = self.model
            overpass_string = self.run_dropdown.currentText()

            nucapsTimesList = []
            nucapsTimesList.append(f'{selected_ds},{region},{satID},{nucaps_year},{nucaps_month},{nucaps_day},{nucaps_time}')
            file = open(NUCAPS_times_file, "w")
            for line in nucapsTimesList:
                file.write(f'{line}')
            file.close()

            # Hack to get the screen to refresh and display the points.
            # Auto-update the map
            self.update_from_cal(None, updated_model=False)

            # Convert overpass_string to a datetime object.
            self.run = date.datetime.strptime(overpass_string, Picker.run_format)

            # Change the run_dropdown back to the user-selected overpass.
            self.run_dropdown.setCurrentIndex(self.nucaps_daily_times.index(self.run))

            self.view.setCurrentTime(self.run)

            # Cleanup - remove temporary file once data source has been reloaded.
            if os.path.isfile(NUCAPS_times_file):
                os.remove(NUCAPS_times_file)
        else:
            self.run = date.datetime.strptime(self.run_dropdown.currentText(), Picker.run_format)
            self.view.setCurrentTime(self.run)
            self.update_list()

    def get_map(self):
        """
        Get the user's map selection
        """
        logging.debug("Calling full_gui.get_map")
        proj = {'Northern Hemisphere': 'npstere', 'Tropics': 'merc',
                'Southern Hemisphere': 'spstere'}[self.map_dropdown.currentText()]
        self.view.setProjection(proj)

    def save_view(self):
        """
        Save the map projection to the config file
        """
        self.view.saveProjection(self.config)

    def select_all(self):
        logging.debug("Calling full_gui.select_all")
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

    def skewApp(self, filename=None, ntry=0):
        logging.debug("Calling full_gui.skewApp")

        """
        Create the SPC style SkewT window, complete with insets
        and magical funtimes.
        :return:
        """
        logging.debug("Calling full_gui.skewApp")

        failure = False

        exc = ""

        # if the profile is an archived file, load the file from
        # the hard disk
        if filename is not None:
            logging.info("Trying to load file from local disk...")

            model = "Archive"
            prof_collection, stn_id = self.loadArchive(filename)
            logging.info(
                "Successfully loaded the profile collection for this file...")
            disp_name = stn_id
            observed = True
            fhours = None

            # Determine if the dataset passed was from a model or is observed
            if len(prof_collection._dates) > 1:
                prof_idx = self.prof_idx
                fhours = ["F%03d" % fh for idx, fh in enumerate(
                    self.data_sources[self.model].getForecastHours()) if idx in prof_idx]
                observed = False
            else:
                fhours = None
                observed = True

            run = prof_collection.getCurrentDate()

        else:
            # otherwise, download with the data thread
            logging.info("Loading a real-time data stream...")
            prof_idx = self.prof_idx
            disp_name = self.disp_name
            run = self.run
            model = self.model
            observed = self.data_sources[model].isObserved()

            if self.data_sources[model].getForecastHours() == [0]:
                prof_idx = [0]

            logging.info("Program is going to load the data...")
            ret = loadData(
                self.data_sources[model], self.loc, run, prof_idx, ntry=ntry)

            # failure variable makes sure the data actually exists online.
            if isinstance(ret[0], Exception):
                exc = ret[0]
                failure = True
                logging.info(
                    "There was a problem with loadData() in obtaining the data from the Internet.")
            else:
                logging.info("Data was found and successfully decoded!")
                prof_collection = ret[0]

            fhours = ["F%03d" % fh for idx, fh in enumerate(self.data_sources[self.model].getForecastHours()) if
                      idx in prof_idx]

        # If the observed or model profile (not Archive) successfully loaded)
        if not failure:
            prof_collection.setMeta('model', model)
            prof_collection.setMeta('run', run)
            prof_collection.setMeta('loc', disp_name)
            prof_collection.setMeta('fhour', fhours)
            prof_collection.setMeta('observed', observed)

            if not prof_collection.getMeta('observed'):
                # If it's not an observed profile, then generate profile objects in background.
                prof_collection.setAsync(Picker.async_obj)

            if self.skew is None:
                logging.debug("Constructing SPCWindow")
                # If the SPCWindow isn't shown, set it up.
                self.skew = SPCWindow(parent=self.parent(), cfg=self.config)
                self.parent().config_changed.connect(self.skew.centralWidget().updateConfig)
                self.skew.closed.connect(self.skewAppClosed)
                self.skew.show()

            logging.debug("Focusing on the SkewApp")
            self.focusSkewApp()
            logging.debug("Adding the profile collection to SPCWindow")
            self.skew.addProfileCollection(prof_collection, check_integrity=self.strictQC)
        else:
            print("There was an exception:", exc)

            raise exc

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

    def keyPressEvent(self, e):
        if e.key() == 61 or e.key() == 45:
            self.view.keyPressEvent(e)

    def loadArchive(self, filename):
        """
        Get the archive sounding based on the user's selections.
        Also reads it using the Decoders and gets both the stationID and the profile objects
        for that archive sounding.  Tries a variety of decoders available to the program.
        """
        logging.debug(
            "Looping over all decoders to find which one to use to decode User Selected file.")
        for decname, deccls in getDecoders().items():
            try:
                dec = deccls(filename)
                break
            except Exception as e:
                logging.exception(e)
                dec = None
                continue

        if dec is None:
            raise IOError(
                "Could not figure out the format of '%s'!" % filename)
        # Returns the set of profiles from the file that are from the "Profile" class.
        logging.debug('Get the profiles from the decoded file.')
        profs = dec.getProfiles()
        stn_id = dec.getStnId()
        return profs, stn_id

    def hasConnection(self):
        return self.has_connection

    def setStrictQC(self, val):
        self.strictQC = val

@progress(Picker.async_obj)
def loadData(data_source, loc, run, indexes, ntry=0, __text__=None, __prog__=None):
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
        decoder, url = data_source.getDecoderAndURL(loc, run, outlet_num=ntry)
        logging.info("Using decoder: " + str(decoder))
        logging.info("Data URL: " + url)
        dec = decoder(url)

    if __text__ is not None:
        __text__.emit("Creating Profiles")

    profs = dec.getProfiles(indexes=indexes)
    return profs


class Main(QMainWindow):
    config_changed = Signal(Config)

    HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")
    cfg_file_name = os.path.join(HOME_DIR, 'sharppy.ini')

    def __init__(self):
        """
        Initializes the window and reads in the configuration from the file.
        """
        super(Main, self).__init__()

        # All of these variables get set/reset by the various menus in the GUI
#       self.config = ConfigParser.RawConfigParser()
#       self.config.read(Main.cfg_file_name)
#       if not self.config.has_section('paths'):
#           self.config.add_section('paths')
#           self.config.set('paths', 'load_txt', expanduser('~'))
        self.config = Config(Main.cfg_file_name)
        paths_init = {('paths', 'load_txt'): expanduser("~")}
        self.config.initialize(paths_init)

        PrefDialog.initConfig(self.config)

        self.__initUI()

    def __initUI(self):
        """
        Puts the user inteface together
        """
        self.picker = Picker(self.config, parent=self)
        self.setCentralWidget(self.picker)
        self.createMenuBar()

        # set the window title
        window_title = 'SHARPpy Sounding Picker'
        self.setWindowTitle(window_title)

        self.show()
        self.raise_()
        #import time
        #time.sleep(3)
        #self.grab().save('./screenshot.png', 'png')

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
        path = self.config['paths', 'load_txt']

        link, _ = QFileDialog.getOpenFileNames(self, 'Open file', path)

        if len(link) == 0 or link[0] == '':
            return

        path = os.path.dirname(link[0])
        self.config['paths', 'load_txt'] = path

        # Loop through all of the files selected and load them into the SPCWindow
        if link[0].endswith("nc") and has_nc:
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

            # write the CSV file
            csvfile = open(HOME_DIR + "/datasources/wrf-arw.csv", 'w')
            csvfile.write(
                "icao,iata,synop,name,state,country,lat,lon,elev,priority,srcid\n")

            for idx, val in np.ndenumerate(xlon1):
                lat = xlat1[idx]
                lon = xlon1[idx]
                csvfile.write(",,,,,," + str(lat) + "," + str(lon) +
                              ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
            for idx, val in np.ndenumerate(xlon2):
                lat = xlat2[idx]
                lon = xlon2[idx]
                csvfile.write(",,,,,," + str(lat) + "," + str(lon) +
                              ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
            for idx, val in np.ndenumerate(xlon3):
                lat = xlat3[idx]
                lon = xlon3[idx]
                csvfile.write(",,,,,," + str(lat) + "," + str(lon) +
                              ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
            for idx, val in np.ndenumerate(xlon4):
                lat = xlat4[idx]
                lon = xlon4[idx]
                csvfile.write(",,,,,," + str(lat) + "," + str(lon) +
                              ",0,,LAT" + str(lat) + "LON" + str(lon) + "\n")
            csvfile.close()

            # write the xml file
            xmlfile = open(HOME_DIR + "/datasources/wrf-arw.xml", 'w')
            xmlfile.write(
                '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
            xmlfile.write('<sourcelist>\n')
            xmlfile.write(
                '    <datasource name="Local WRF-ARW" ensemble="false" observed="false">\n')
            xmlfile.write('        <outlet name="Local" url="file://' +
                          link[0] + '" format="wrf-arw">\n')
            xmlfile.write('            <time range="' + str(int(maxt)) + '" delta="' +
                          str(int(delta)) + '" offset="0" delay="0" cycle="24" archive="1"/>\n')
            xmlfile.write('            <points csv="wrf-arw.csv" />\n')
            xmlfile.write('        </outlet>\n')
            xmlfile.write('    </datasource>\n')
            xmlfile.write('</sourcelist>\n')
            xmlfile.close()

            self.picker.update_datasource_dropdown(selected="Local WRF-ARW")
        else:
            for l in link:
                self.picker.skewApp(filename=l)

    def aboutbox(self):
        """
        Creates and shows the "about" box.
        """
        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        documentationButton = msgBox.addButton(self.tr("Online Docs"), QMessageBox.ActionRole)
        bugButton = msgBox.addButton(self.tr("Report Bug"), QMessageBox.ActionRole)
        githubButton = msgBox.addButton(self.tr("Github"), QMessageBox.ActionRole)
        msgBox.addButton(QMessageBox.Close)
#        closeButton = msgBox.addButton(self.tr("Close"), QMessageBox.RejectRole)
        msgBox.setDefaultButton(QMessageBox.Close)
        txt = "SHARPpy v%s %s\n\n" % (__version__, __version_name__)
        txt += "Sounding and Hodograph Analysis and Research Program for Python\n\n"
        txt += "(C) 2014-%d by Patrick Marsh, John Hart, Kelton Halbert, Greg Blumberg, and Tim Supinie." % cur_year
        desc = "\n\nSHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding " + \
               "plotting package, and an interactive application " + \
               "for analyzing real-time soundings all written in " + \
               "Python. It was developed to provide the " + \
               "atmospheric science community a free and " + \
               "consistent source of routines for analyzing sounding data. SHARPpy is constantly updated and " + \
               "vetted by professional meteorologists and " + \
               "climatologists within the scientific community to " + \
               "help maintain a standard source of sounding routines.\n\n"
        txt += desc
        txt += versioning_info()
        #txt += "PySide version: " + str(PySide.__version__) + '\n'
        #txt += "Numpy version: " + str(np.__version__) + '\n'
        #txt += "Python version: " + str(platform.python_version()) + '\n'
        #txt += "Qt version: " + str(PySide.QtCore.__version__)
        txt += "\n\nContribute: https://github.com/sharppy/SHARPpy/"
        msgBox.setText(txt)
        msgBox.exec_()

        if msgBox.clickedButton() == documentationButton:
            QDesktopServices.openUrl(QUrl('http://sharppy.github.io/SHARPpy/'))
        elif msgBox.clickedButton() == githubButton:
            QDesktopServices.openUrl(QUrl('https://github.com/sharppy/SHARPpy'))
        elif msgBox.clickedButton() == bugButton:
            QDesktopServices.openUrl(QUrl('https://github.com/sharppy/SHARPpy/issues'))

    def preferencesbox(self):
        pref_dialog = PrefDialog(self.config, parent=self)
        pref_dialog.exec_()
        self.config_changed.emit(self.config)

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
        # JTS - Cleanup; Remove nucapsTimes.txt when main GUI closes.
        if os.path.isfile(NUCAPS_times_file):
            os.remove(NUCAPS_times_file)

        self.config.toFile()

def newerRelease(latest):
    #msgBox = QMessageBox()
    txt = "A newer version of SHARPpy (" + latest[1] + ") was found.\n\n"
    txt += "Do you want to launch a web browser to download the new version from Github?  "
    txt += "(if you downloaded from pip or conda you may want to use those commands instead.)"
    ret_code = QMessageBox.information(None, "New SHARPpy Version!" , txt, QMessageBox.Yes, QMessageBox.No)
    if ret_code == QMessageBox.Yes:
        QDesktopServices.openUrl(QUrl(latest[2]))

@crasher(exit=True)
def createWindow(file_names, collect=False, close=True, output='./', strictQC=False):
    main_win = Main()
    for fname in file_names:
        txt = OKGREEN + "Creating image for '%s' ..." + ENDC
        print(txt % fname)
        main_win.picker.setStrictQC(strictQC)
        main_win.picker.skewApp(filename=fname)
        if not collect:
            fpath, fbase = os.path.split(fname)

            if '.' in fbase:
                img_base = ".".join(fbase.split(".")[:-1] + ['png'])
            else:
                img_base = fbase + '.png'

            img_name = os.path.join(fpath, img_base)
            main_win.picker.skew.spc_widget.pixmapToFile(output + img_name)
            if fname != file_names[-1] or close:
                main_win.picker.skew.close()

    if collect:
        main_win.picker.skew.spc_widget.toggleCollectObserved()
        img_name = collect[0]
        main_win.picker.skew.spc_widget.pixmapToFile(output + img_name)
        if close:
            main_win.picker.skew.close()

    return main_win

@crasher(exit=False)
def search_and_plotDB(model, station, datetime, close=True, output='./'):
    main_win = Main()
    main_win.picker.prof_idx = [0]
    main_win.picker.run = datetime
    main_win.picker.model = model
    main_win.picker.loc = main_win.picker.data_sources[model].getPoint(station)
    main_win.picker.disp_name = main_win.picker.loc['icao']
    try:
        main_win.picker.skewApp()
    except data_source.DataSourceError as e:
        logging.exception(e)
        print(FAIL + "Couldn't find data for the requested time and location." + ENDC)
        return main_win

    string = OKGREEN + "Creating image for station %s using data source %s at time %s ..." + ENDC
    print( string % (station, model, datetime.strftime('%Y%m%d/%H%M')))
    main_win.picker.skew.spc_widget.pixmapToFile(output + datetime.strftime('%Y%m%d.%H%M_' + model + '.png'))
    if close:
        main_win.picker.skew.close()
    return main_win

def test(fn):
    # Run the binary and output a test profile
    if QApplication.instance() is None:
        app = QApplication([])
    else:
        app = QApplication.instance()
    win = createWindow(fn, strictQC=False)
    win.close()

def parseArgs():
    desc = """This binary launches the SHARPpy Picker and GUI from the command line.  When
           run from the command line without arguments, this binary simply launches the Picker
           and loads in the various datasets within the user's ~/.sharppy directory.  When the
           --debug flag is set, the GUI is run in debug mode.

           When a set of files are passed as a command line argument, the program will
           generate images of the SHARPpy GUI for each sounding.  Soundings can be overlaid
           on top of one another if the collect flag is set.  In addition, data from the
           datasources can be plotted using the datasource, station, and datetime arguments."""
    data_sources = [key for key in data_source.loadDataSources().keys()]
    ep = "Available Datasources: " + ', '.join(data_sources)
    ap = argparse.ArgumentParser(description=desc, epilog=ep)

    ap.add_argument('file_names', nargs='*',
                    help='a list of files to read and plot')
    ap.add_argument('--debug', dest='debug', action='store_true',
                    help='turns on debug mode for the GUI')
    ap.add_argument('--version', dest='version', action='store_true',
                    help="print out versioning information")
    ap.add_argument('--collect', dest='collect', action='store_true',
                    help="overlay profiles from filename on top of one another in GUI image")
    #ap.add_argument('--noclose', dest='close', action='store_false',
    #                help="do not close the GUI after viewing the image")
    group = ap.add_argument_group("datasource access arguments")

    group.add_argument('--datasource', dest='ds', type=str,
                    help="the name of the datasource to search")
    group.add_argument('--station', dest='stn', type=str,
                    help="the name of the station to plot (ICAO, IATA)")
    group.add_argument('--datetime', dest='dt', type=str,
                    help="the date/time of the data to plot (YYYYMMDD/HH)")
    ap.add_argument('--output', dest='output', type=str,
                    help="the output directory to store the images", default='./')
    args = ap.parse_args()

    # Print out versioning information and quit
    if args.version is True:
        ap.exit(0, versioning_info(True) + '\n')

    # Catch invalid data source
    if args.ds is not None and args.ds not in data_sources:
        txt = FAIL + "Invalid data source passed to the program.  Exiting." + ENDC
        ap.error(txt)

    # Catch invalid datetime format
    if args.dt is not None:
        try:
            date.datetime.strptime(args.dt , '%Y%m%d/%H')
        except:
            txt = FAIL + "Invalid datetime passed to the program. Exiting." + ENDC
            ap.error(txt)

    return args

def main():
    args = parseArgs()

    # Create an application
    #app = QApplication([])
    #app.setAttribute(Qt.AA_EnableHighDpiScaling)
    #app.setAttribute(Qt.AA_UseHighDpiPixmaps)
#
    #app.setStyle("fusion")
    if QApplication.instance() is None:
        app = QApplication([])
    else:
        app = QApplication.instance()

    #win = createWindow(args.file_names, collect=args.collect, close=False)
    # Check to see if there's a newer version of SHARPpy on Github Releases
#     latest = check_latest()

#     if latest[0] is False:
#         logging.info("A newer release of SHARPpy was found on Github Releases.")
#     else:
#         logging.info("This is the most recent version of SHARPpy.")

    # Alert the user that there's a newer version on Github (and by extension through CI also on pip and conda)
    # if latest[0] is False:
    #     newerRelease(latest)

    if args.dt is not None and args.ds is not None and args.stn is not None:
        dt = date.datetime.strptime(args.dt, "%Y%m%d/%H")
        win = search_and_plotDB(args.ds, args.stn, dt, args.output)
        win.close()
    elif args.file_names != []:
        win = createWindow(args.file_names, collect=args.collect, close=True, output=args.output)
        win.close()
    else:
        main_win = Main()
        #app.exec_()
        sys.exit(app.exec_())

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    main()