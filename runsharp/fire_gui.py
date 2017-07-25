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

DATA_DIR = os.path.abspath(os.path.join(os.getcwd(), 'sharppy_soundings'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ARCHIVE_DIR = os.path.abspath(os.path.join(os.getcwd(), 'sharppy_archive'))
if not os.path.exists(ARCHIVE_DIR):
    os.makedirs(ARCHIVE_DIR)
  
from sharppy.viz.SPCWindow import SPCWindow
from sharppy.viz.map import MapWidget 
import sharppy.sharptab.profile as profile
from sharppy.io.decoder import getDecoders, getDecoder
from sharppy._sharppy_version import __version__, __version_name__, __upstream_version_name__, __upstream_version__

from datasources import data_source
from utils.async import AsyncThreads
from utils.progress import progress

from PySide.QtCore import *
from PySide.QtGui import *
import datetime as date
from functools import wraps, partial
import cProfile
from os.path import expanduser, dirname, join, splitext, abspath, exists
from os import listdir, getcwd
import ConfigParser
import traceback
from functools import wraps, partial
from json import dumps
from bz2 import compress
from datetime import datetime

import sharppy.io.ibufr_decoder

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
class ArchivePicker(QWidget):
    def __init__(self, picker, **kwargs):
        super(ArchivePicker, self).__init__(**kwargs)
        self.picker = picker
        self.picker.add_archive_picker(self)
        self.toNiceModels = dict([(mod.lower().replace(' ', '_'), mod) for mod in self.picker.data_sources.keys()])
        self.fromNiceModels = dict([(mod, mod.lower().replace(' ', '_')) for mod in self.picker.data_sources.keys()])
        
        self.__initUI()
        self.update_date_list()
    def get_nice_model_name(self, *args):
        model = '_'.join(*args)
        if model in self.toNiceModels:
            return self.toNiceModels[model]
        else:
            return model.replace('_', ' ')
    def get_model_file_name(self, name):
        if name in self.fromNiceModels:
            return self.fromNiceModels[name]
        else:
            return name.lower().replace(' ', '_')
    def update_date_list(self):
        self.file_date_list.clear()
        self.file_model_list.clear()
        self.file_site_list.clear()
        self.load_button.setDisabled(True)
        self.archive_files = {}
        
        files = listdir(ARCHIVE_DIR)
        files.sort()
        
        for item in files:
            item_array = splitext(item)[0].split('_')
            if len(item_array) >= 3:
                date_string = item_array[0]
                if date_string not in self.archive_files:
                    self.archive_files[date_string] = {}
                if self.get_nice_model_name(item_array[1:-1]) not in self.archive_files[date_string]:
                    self.archive_files[date_string][self.get_nice_model_name(item_array[1:-1])] = []
                self.archive_files[date_string][self.get_nice_model_name(item_array[1:-1])].append(item_array[-1].upper())
        
        dates = self.archive_files.keys()
        dates.sort()
        for item in dates:
            self.file_date_list.addItem(datetime.strptime(item, '%Y%m%d%H').strftime(Picker.run_format))
        self.file_date_list.update()
    def update_model_list(self):
        self.file_model_list.clear()
        self.file_site_list.clear()
        self.load_button.setDisabled(True)
        
        models = self.archive_files[datetime.strptime(self.file_date_list.currentItem().text(),Picker.run_format).strftime('%Y%m%d%H')].keys()
        models.sort()
        
        for item in models:
            self.file_model_list.addItem(item)
        self.file_model_list.update()
    def update_site_list(self):
        self.file_site_list.clear()
        self.load_button.setDisabled(True)
        
        sites = self.archive_files[datetime.strptime(self.file_date_list.currentItem().text(),Picker.run_format).strftime('%Y%m%d%H')][self.file_model_list.currentItem().text()]
        sites.sort()
        for item in sites:
            self.file_site_list.addItem(item)
        self.file_site_list.update()
    def station_selected(self):
        self.load_button.setDisabled(False)
    def load_archive_file(self):
        file_name = join(ARCHIVE_DIR, '_'.join([datetime.strptime(self.file_date_list.currentItem().text(), Picker.run_format).strftime('%Y%m%d%H'),
                                                                  self.get_model_file_name(self.file_model_list.currentItem().text()),
                                                                  self.file_site_list.currentItem().text().lower()])+'.sharppy')
        self.picker.skewApp(filename=file_name)
    def __initUI(self):
        self.control_widget = QVBoxLayout()
        self.setLayout(self.control_widget)
        self.file_list_frame = QWidget()
        self.file_list_layout = QHBoxLayout()
        self.file_list_frame.setLayout(self.file_list_layout)
        self.file_date_frame = QWidget()
        self.file_date_layout = QVBoxLayout()
        self.file_date_frame.setLayout(self.file_date_layout)
        self.file_date_label = QLabel('Date:')
        self.file_date_list = QListWidget()
        self.file_date_list.itemClicked.connect(self.update_model_list)
        self.file_date_layout.addWidget(self.file_date_label)
        self.file_date_layout.addWidget(self.file_date_list)
        self.file_model_frame = QWidget()
        self.file_model_layout = QVBoxLayout()
        self.file_model_frame.setLayout(self.file_model_layout)
        self.file_model_label = QLabel('Model:')
        self.file_model_list = QListWidget()
        self.file_model_list.itemClicked.connect(self.update_site_list)
        self.file_model_layout.addWidget(self.file_model_label)
        self.file_model_layout.addWidget(self.file_model_list)
        self.file_site_frame = QWidget()
        self.file_site_layout = QVBoxLayout()
        self.file_site_frame.setLayout(self.file_site_layout)
        self.file_site_label = QLabel('Site:')
        self.file_site_list = QListWidget()
        self.file_site_list.itemClicked.connect(self.station_selected)
        self.file_site_layout.addWidget(self.file_site_label)
        self.file_site_layout.addWidget(self.file_site_list)
        self.button_frame = QWidget()
        self.button_layout = QHBoxLayout()
        self.button_frame.setLayout(self.button_layout)
        self.refresh_button = QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.update_date_list)
        self.load_button = QPushButton('Load')
        self.load_button.clicked.connect(self.load_archive_file)
        self.spacer = QLabel('')
        self.spacer2 = QLabel('')
        self.spacer3 = QLabel('')
        self.spacer4 = QLabel('')
        self.file_list_layout.addWidget(self.file_date_frame)
        self.file_list_layout.addWidget(self.file_model_frame)
        self.file_list_layout.addWidget(self.file_site_frame)
        self.control_widget.addWidget(self.file_list_frame)
        self.button_layout.addWidget(self.spacer)
        self.button_layout.addWidget(self.spacer2)
        self.button_layout.addWidget(self.spacer3)
        self.button_layout.addWidget(self.spacer4)
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addWidget(self.load_button)
        self.control_widget.addWidget(self.button_frame)
class LocalPicker(QWidget):
    async = AsyncThreads(2, debug)
    def __init__(self, picker, **kwargs):
        super(LocalPicker, self).__init__(**kwargs)
        self.picker = picker
        self.search_directory = DATA_DIR
        self.__initUI()
    def __initUI(self):
        self.control_layout = QVBoxLayout()
        self.setLayout(self.control_layout)
        
        self.button_frame = QWidget()
        self.button_layout = QHBoxLayout()
        self.button_frame.setLayout(self.button_layout)
        
        self.file_label = QLabel("Select File (Current Folder: " + self.search_directory + " )")
        self.file_list = QListWidget()
        
        self.adjust_time_widget = QWidget()
        self.adjust_time_layout = QHBoxLayout()
        self.adjust_time_layout.addStretch(1)
        self.adjust_time_widget.setLayout(self.adjust_time_layout)
        
        self.adjust_time = QCheckBox('Adjust time to model times')
        self.adjust_time_hours = QComboBox()
        for x in [1, 3]:
            self.adjust_time_hours.addItem(str(x))
        
        self.change_dir_button = QPushButton('Change Directory')
        self.change_dir_button.clicked.connect(self.change_folder)
        
        self.update_button = QPushButton('Refresh')
        self.update_button.clicked.connect(self.update_files)
        
        self.button = QPushButton('Load Profile')
        self.button.clicked.connect(self.open_bufr)
        
        self.update_files()
        self.control_layout.addWidget(self.file_label)
        self.control_layout.addWidget(self.file_list)
        self.adjust_time_layout.addWidget(self.adjust_time)
        self.adjust_time_layout.addWidget(self.adjust_time_hours)
        self.control_layout.addWidget(self.adjust_time_widget)
        self.button_layout.addWidget(self.change_dir_button)
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.button)
        self.control_layout.addWidget(self.button_frame)
    def open_bufr(self):
        #sharppy.io.ibufr_decoder.TIME_ADJUST = 1
        if self.adjust_time.isChecked():
            sharppy.io.ibufr_decoder.TIME_ADJUST = int(self.adjust_time_hours.currentText())
        else:
            sharppy.io.ibufr_decoder.TIME_ADJUST = False
        self.picker.skewApp(filename=join(self.search_directory, self.file_list.selectedItems()[0].text()))
    def update_files(self):
        self.file_list.clear()
        bufr_file_list = listdir(self.search_directory)
        bufr_file_list.sort()
        for item in bufr_file_list:
            if splitext(item)[1].lower() == '.bufr' or splitext(item)[1].lower() == '.buf' or splitext(item)[1].lower() == '.txt':
                self.file_list.addItem(item)
        self.file_list.update()
    def change_folder(self):
        new_path = QFileDialog.getExistingDirectory(self, "Change Folder", self.search_directory, QFileDialog.ShowDirsOnly)
        if new_path is not None and new_path != '':
            self.search_directory = abspath(new_path)
            self.file_label.setText("Select File (Current Folder: " + self.search_directory + " )")
            self.update_files()
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
        self.archive_picker = None
        ## default the sounding location to OUN because obviously I'm biased
        self.loc = None
        ## the index of the item in the list that corresponds
        ## to the profile selected from the list
        self.prof_idx = None
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

        self.archive_sounding = QCheckBox('Archive')
        self.archive_sounding.setCheckState(Qt.CheckState.Checked)

        self.save_view_button = QPushButton('Save Map View as Default')
        self.save_view_button.clicked.connect(self.save_view)

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

        self.run_list = QListWidget()
        for item in [ t.strftime(Picker.run_format) for t in times ]:
            self.run_list.addItem(item)
        try:
            self.run_list.setCurrentRow(times.index(self.run))
        except ValueError:
            print "Run dropdown is missing its times ... ?"
            print times

        ## connect the click actions to functions that do stuff
        self.model_dropdown.activated.connect(self.get_model)
        self.map_dropdown.activated.connect(self.get_map)
        #self.run_dropdown.activated.connect(self.get_run)
        self.run_list.itemClicked.connect(self.get_run)

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
        self.left_layout.addWidget(self.run_list)
        self.left_layout.addWidget(self.archive_sounding)
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

    def add_archive_picker(self, picker):
        self.archive_picker = picker

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
            self.run_list.clear()

            if self.model == "Observed":
                self.run = [ t for t in times if t.hour in [ 0, 12 ] ][-1]
            else:
                self.run = times[-1]

            for data_time in times:
                self.run_list.addItem(data_time.strftime(Picker.run_format))

            self.run_list.update()
            self.run_list.setCurrentRow(times.index(self.run))

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
            self.skewApp()

    def get_model(self, index):
        """
        Get the user's model selection
        """
        self.model = self.model_dropdown.currentText()

        self.update_run_dropdown()
        self.async.join(self.async_id)

        self.view.setDataSource(self.data_sources[self.model], self.run)

    def get_run(self, index):
        """
        Get the user's run hour selection for the model
        """
        self.run = date.datetime.strptime(self.run_list.currentItem().text(), Picker.run_format)
        self.view.setCurrentTime(self.run)

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
            prof_collection, stn_id = self.loadArchive(filename)
            disp_name = stn_id
            prof_idx = range(len(dates))

            run = prof_collection.getCurrentDate()
            
            if not prof_collection.hasMeta('fhours'):
                fhours = ["F{0:03d}".format((lambda y: int(round(((y.days*86400.0)+y.seconds)/3600.0 )))(prof_collection._dates[x]-prof_collection._dates[0])) for x in range(len(prof_collection._dates))]
            else:
                fhours = prof_collection.getMeta('fhours')
            
            if not prof_collection.hasMeta('observed'):
                observed = True
            else:
                observed = prof_collection.getMeta('observed')
                
            if not prof_collection.hasMeta('model'):
                model = "Archive"
            else:
                model = prof_collection.getMeta('model')
        else:
        ## otherwise, download with the data thread
            prof_idx = self.prof_idx
            disp_name = self.disp_name
            run = self.run
            model = self.model
            observed = self.data_sources[model].isObserved()

            if self.data_sources[model].getForecastHours() == [ 0 ]:
                prof_idx = [ 0 ]

            ret = loadData(self.data_sources[model], self.loc, run, prof_idx, archive=self.archive_sounding.isChecked())

            if isinstance(ret[0], Exception):
                exc = ret[0]
                failure = True
            else:
                prof_collection = ret[0]
                if self.archive_picker is not None:
                    self.archive_picker.update_date_list()

        if not failure:
            fhours = ["F{0:03d}".format((lambda y: int(round(((y.days*86400.0)+y.seconds)/3600.0 )))(prof_collection._dates[x]-prof_collection._dates[0])) for x in range(len(prof_collection._dates))]
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
                self.skew.setWindowIcon(self.parent().windowIcon())
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

        for decname, deccls in getDecoders().iteritems():
            try:
                dec = deccls(filename)
                break
            except:
                dec = None
                continue

        if dec is None:
            raise IOError("Could not figure out the format of '%s'!" % filename)

        profs = dec.getProfiles(indexes=None)
        stn_id = dec.getStnId()

        return profs, stn_id

    def hasConnection(self):
        return self.has_connection

@progress(Picker.async)
def loadData(data_source, loc, run, indexes, __text__=None, __prog__=None, archive=False):
    """
    Loads the data from a remote source. Has hooks for progress bars.
    """
        
    arc_file = join(ARCHIVE_DIR, '{date:s}_{model:s}_{site:s}.sharppy'.format(date=run.strftime('%Y%m%d%H'), model=data_source.getName().lower().replace(' ', '_'), site=loc['srcid'].lower()))
    
    if __text__ is not None:
        __text__.emit("Decoding File")

    if exists(arc_file):
        url = arc_file
        decoder  = getDecoder('archive')
    else:
        url = data_source.getURL(loc, run)
        decoder = data_source.getDecoder(loc, run)
    dec = decoder(url)

    if __text__ is not None:
        __text__.emit("Creating Profiles")

    if archive:
        with open(arc_file, 'wb') as out_file:
            out_file.write(compress(dumps(dec.getProfiles(indexes=None).serialize(stringify_date=True))))

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

        self.resize(969, 635)

        self.__initUI()

    def __initUI(self):
        """
        Puts the user inteface together
        """
        self.imet_tabs = QTabWidget(parent=self)

        self.picker = Picker(self.config, parent=self)
        self.local_picker = LocalPicker(self.picker, parent=self)
        self.archive_picker = ArchivePicker(self.picker, parent=self)
        self.imet_tabs.addTab(self.local_picker, 'Incident Sounding')
        self.imet_tabs.addTab(self.picker, 'Model Data')
        self.imet_tabs.addTab(self.archive_picker, 'Archive')
        self.setCentralWidget(self.imet_tabs)
        self.createMenuBar()
        
        ## set the window title
        window_title = 'SHARPpy Sounding Picker'
        self.setWindowTitle(window_title)
        icon = abspath(join(dirname(__file__), 'icons/SHARPpy_imet.png'))
        self.setWindowIcon(QIcon(icon))
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
        for l in link:
            self.picker.skewApp(filename=l)

    def aboutbox(self):
        """
        Creates and shows the "about" box.
        """
        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        str = """
        SHARPpy IMET v{0:s} {1:s}

        Developed by Nickolai Reimer WFO Billings

        Based on SHARPpy Beta v{3:s} {2:s}
        Sounding and Hodograph Analysis and Research
        Program for Python

        (C) 2014-{4:d} by Patrick Marsh, John Hart,
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
        
        Using Bufrpy (C) Tuure Laurinolli / FMI
        
        Contribute: https://github.com/tazle/bufrpy
        """.format(__version__, __version_name__, __upstream_version_name__, __upstream_version__, cur_year)
        msgBox.setText(str)
        msgBox.exec_()

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
    app.setWindowIcon(win.windowIcon())
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
