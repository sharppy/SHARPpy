__author__ = 'keltonhalbert, wblumberg'

import logging
from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics #, plotGeneric
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP, plotWinter
from sharppy.viz import plotSHIP, plotSTPEF, plotFire, plotVROT
from PySide.QtCore import *
from PySide.QtGui import *
import sharppy.sharptab.profile as profile
import sharppy.sharptab as tab
import sharppy.io as io
from utils.config import Config
from datetime import datetime, timedelta
import numpy as np
import platform
from os.path import expanduser
import os
import re
import logging
#from sharppy._sharppy_version import __version__, __version_name__
from sharppy._version import get_versions
__codename__ = "Andover"
__version__ = get_versions()['version']
del get_versions
__version_name__ = ''

def _modifySheet(sheet, name, value):
    return re.sub("(?<= %s: )#[0-9A-Fa-f]{6}" % name, value, sheet)


class SPCWidget(QWidget):
    """
    This will create the full SPC window, handle the organization
    of the insets, and handle all click/key events and features.
    """

    inset_generators = {
        'SARS':plotAnalogues,
        'STP STATS':plotSTP,
        'COND STP':plotSTPEF,
        'WINTER':plotWinter,
        'FIRE':plotFire,
        'SHIP':plotSHIP,
        'VROT':plotVROT,
    }

    inset_names = {
        'SARS':'Sounding Analogues',
        'STP STATS':'Sig-Tor Stats',
        'COND STP':'EF-Scale Probs (Sig-Tor)',
        'WINTER':'Winter Weather',
        'FIRE':'Fire Weather',
        'SHIP':'Sig-Hail Stats',
        'VROT':'EF-Scale Probs (V-Rot)',
    }

    inset_cfg = {
        ('insets', 'left_inset'):'SARS',
        ('insets', 'right_inset'):'STP STATS',
    }

    parcel_cfg = {
        ('parcel_types', 'pcl1'):'SFC',
        ('parcel_types', 'pcl2'):'ML',
        ('parcel_types', 'pcl3'):'FCST',
        ('parcel_types', 'pcl4'):'MU',
    }

    paths_cfg = {
        ('paths', 'save_img'):expanduser('~'),
        ('paths', 'save_txt'):expanduser('~'),
    }

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)

        super(SPCWidget, self).__init__(parent=parent)
        """
        """
        logging.debug("Initializing SPCWidget.")
        ## these are the keyword arguments used to define what
        ## sort of profile is being viewed
        self.prof_collections = []
        self.prof_ids = []
        self.default_prof = None
        self.pc_idx = 0
        self.config = kwargs.get("cfg")
        self.dgz = False
        self.pbl = False
        self.mode = ""

        ## these are used to display profiles
        self.parcel_type = "MU"

        self.coll_observed = False

        self.config.initialize(SPCWidget.inset_cfg)
        self.config.initialize(SPCWidget.parcel_cfg)
        self.config.initialize(SPCWidget.paths_cfg)

        ## these are the boolean flags used throughout the program
        self.swap_inset = False

        ## initialize empty variables to hold objects that will be
        ## used later
        self.left_inset_ob = None
        self.right_inset_ob = None

        ## these are used for insets and inset swapping
        insets = sorted(list(SPCWidget.inset_names.items()), key=lambda i: i[1])
        inset_ids, inset_names = list(zip(*insets))
        self.available_insets = inset_ids
        self.left_inset = self.config['insets', 'left_inset']
        self.right_inset = self.config['insets', 'right_inset']
        self.insets = {}

        self.parcel_types = [self.config['parcel_types', 'pcl1'], self.config['parcel_types', 'pcl2'], \
                             self.config['parcel_types', 'pcl3'], self.config['parcel_types', 'pcl4']]

        ## initialize the rest of the window attributes, layout managers, etc

        self.bg_color = QColor(self.config['preferences', 'bg_color'])
        self.fg_color = QColor(self.config['preferences', 'fg_color'])

        bg_hex = "#%02x%02x%02x" % (self.bg_color.red(), self.bg_color.green(), self.bg_color.blue())
        fg_hex = "#%02x%02x%02x" % (self.fg_color.red(), self.fg_color.green(), self.fg_color.blue())

        self.setStyleSheet("QWidget {background-color: " + bg_hex + ";}")
        ## set the the whole window's layout manager
        self.grid = QGridLayout()
        self.grid.setContentsMargins(1,1,1,1)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(2)
        self.setLayout(self.grid)

        ## handle the upper right portion of the window...
        ## hodograph, SRWinds, Storm Slinky, theta-e all go in this frame
        self.urparent = QFrame()
        self.urparent_grid = QGridLayout()
        self.urparent_grid.setContentsMargins(0, 0, 0, 0)
        self.urparent_grid.setVerticalSpacing(0)
        self.urparent.setLayout(self.urparent_grid)
        self.ur = QFrame()
        self.ur.setStyleSheet("QFrame {"
                         "  background-color: " + bg_hex + ";"
                         "  border-width: 0px;"
                         "  border-style: solid;"
                         "  border-color: " + fg_hex + ";"
                         "  margin: 0px;}")

        self.brand = QLabel("SHARPpy v%s %s" % (__version__, __version_name__))
        self.brand.setAlignment(Qt.AlignRight)
        self.brand.setStyleSheet("QFrame {"
                             "  background-color: " + bg_hex + ";"
                             "  text-align: right;"
                             "  padding-top: 4px;"
                             "  padding-bottom: 4px;"
                             "  font-size: 11px;"
                             "  color: " + fg_hex + ";}")

        ## this layout manager will handle the upper right portion of the window
        self.grid2 = QGridLayout()
        self.grid2.setHorizontalSpacing(0)
        self.grid2.setVerticalSpacing(0)
        self.grid2.setContentsMargins(0, 0, 0, 0)
        self.ur.setLayout(self.grid2)
        self.urparent_grid.addWidget(self.brand, 0, 0, 1, 0)
        self.urparent_grid.addWidget(self.ur, 1, 0, 50, 0)
        ## add the upper-right frame to the main frame
        self.grid.addWidget(self.urparent, 0, 1, 3, 1)

        ## Handle the Text Areas
        self.text = QFrame()
        self.text.setStyleSheet("QWidget {"
                            "  background-color: " + bg_hex + ";"
                            "  border-width: 2px;"
                            "  border-style: solid;"
                            "  border-color: #3399CC;}")
        self.grid3 = QGridLayout()
        self.grid3.setHorizontalSpacing(0)
        self.grid3.setContentsMargins(0, 0, 0, 0)
        self.text.setLayout(self.grid3)

        ## set to menu stuff
        self.setUpdatesEnabled(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showCursorMenu)

        ## initialize the data frames
        self.initData()
        self.loadWidgets()

    def getParcelObj(self, prof, name):
        if name == "SFC":
            return prof.sfcpcl
        elif name == "ML":
            return prof.mlpcl
        elif name == "FCST":
            return prof.fcstpcl
        elif name == "MU":
            return prof.mupcl
        elif name == 'EFF':
            return prof.effpcl
        elif name == "USER":
            return prof.usrpcl

    def getParcelName(self, prof, pcl):
        if pcl == prof.sfcpcl:
            return "SFC"
        elif pcl == prof.mlpcl:
            return "ML"
        elif pcl == prof.fcstpcl:
            return "FCST"
        elif pcl == prof.mupcl:
            return "MU"
        elif pcl == prof.effpcl:
            return "EFF"
        elif pcl == prof.usrpcl:
            return "USER"

    def saveimage(self):
        logging.debug("Save an image of the SPCWindow to the disk.")
        path = self.config['paths', 'save_img']
        file_types = "PNG (*.png)"
        file_name, result = QFileDialog.getSaveFileName(self, "Save Image", path, file_types)
        if result:
            self.pixmapToFile(file_name)
            self.config['paths', 'save_img'] = os.path.dirname(file_name)

    def pixmapToFile(self, file_name):
        fmt = file_name.split(".")[-1].upper()
        pixmap = QPixmap.grabWidget(self)
        pixmap.save(file_name, fmt, 100)

    def savetext(self):
        logging.debug("Save the data to the disk.")
        path = self.config['paths', 'save_txt']
        file_types = "TXT (*.txt)"
        file_name, result = QFileDialog.getSaveFileName(self, "Save Sounding Text", path, file_types)
        if result:
            self.default_prof.toFile(file_name)
            self.config['paths', 'save_txt'] = os.path.dirname(file_name)

    def initData(self):
        """
        Initializes all the widgets for the window.
        This gets initially called by __init__
        :return:
        """
        logging.debug("Initializing all widgets in the SPCWindow.")

        self.sound = plotSkewT(dgz=self.dgz, pbl=self.pbl)
#       self.sound.setPreferences(temp_color=temp_color, dewp_color=dewp_color, update_gui=False)
        self.hodo = plotHodo()

        ## initialize the non-swappable insets
        self.speed_vs_height = plotSpeed()
        self.inferred_temp_advection = plotAdvection()
        self.storm_slinky = plotSlinky()
        self.thetae_vs_pressure = plotThetae()
        self.srwinds_vs_height = plotWinds()
        self.watch_type = plotWatch()
        self.convective = plotText(self.parcel_types)
        self.kinematic = plotKinematics()

        # initialize swappable insets
        for inset, inset_gen in SPCWidget.inset_generators.items():
            self.insets[inset] = inset_gen()
#            self.insets[inset].setParent(self.text)

        self.updateConfig(self.config, update_gui=False)

        self.right_inset_ob = self.insets[self.right_inset]
        self.left_inset_ob = self.insets[self.left_inset]

        # Connect signals to slots
        self.convective.updatepcl.connect(self.updateParcel)

        self.sound.parcel.connect(self.defineUserParcel)
        self.sound.modified.connect(self.modifyProf)
        self.sound.reset.connect(self.resetProfModifications)
        self.sound.cursor_toggle.connect(self.hodo.cursorToggle)
        self.sound.cursor_move.connect(self.hodo.cursorMove)

        self.hodo.modified.connect(self.modifyProf)
        self.hodo.modified_vector.connect(self.modifyVector)
        self.hodo.reset.connect(self.resetProfModifications)
        self.hodo.reset_vector.connect(self.resetVector)
        self.hodo.toggle_vector.connect(self.toggleVector)

        self.insets["SARS"].updatematch.connect(self.updateSARS)

    def addProfileCollection(self, prof_col, prof_id, focus=True):
        logging.debug("Adding a Profile Collection to SPCWindow.")

        self.prof_collections.append(prof_col)
        self.prof_ids.append(prof_id)
        self.sound.addProfileCollection(prof_col)
        self.hodo.addProfileCollection(prof_col)

        if focus:
            self.pc_idx = len(self.prof_collections) - 1

        if not prof_col.getMeta('observed'):
            self.coll_observed = False
            self.sound.setAllObserved(self.coll_observed, update_gui=False)
            self.hodo.setAllObserved(self.coll_observed, update_gui=False)


        cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        for prof_col in self.prof_collections:
            if not prof_col.getMeta('observed'):
                prof_col.setCurrentDate(cur_dt)

        self.updateProfs()

    @Slot(str)
    def setProfileCollection(self, prof_id):
        logging.debug("Setting the Profile Collection to SPCWindow.")

        try:
            self.pc_idx = self.prof_ids.index(prof_id)
        except ValueError:
            print("Hmmm, that profile doesn't exist to be focused ...")
            return


        cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        for prof_col in self.prof_collections:
            if not prof_col.getMeta('observed'):
                prof_col.setCurrentDate(cur_dt)

        self.updateProfs()

    def rmProfileCollection(self, prof_id):
        logging.debug("Removing Profile Collection from SPCWindow.")
        try:
            pc_idx = self.prof_ids.index(prof_id)
        except ValueError:
            print("Hmmm, that profile doesn't exist to be removed ...")
            return

        prof_col = self.prof_collections.pop(pc_idx)
        self.prof_ids.pop(pc_idx)
        self.sound.rmProfileCollection(prof_col)
        self.hodo.rmProfileCollection(prof_col)

        # If we've removed an analog, remove it from the profile it's an analog to.
        if prof_col.hasMeta('filematch'):
            filematch = prof_col.getMeta('filematch')
            for pc in self.prof_collections:
                if pc.hasMeta('analogfile'):
                    keys, vals = list(zip(*list(pc.getMeta('analogfile').items())))
                    if filematch in vals:
                        keys = list(keys); vals = list(vals)

                        idx = vals.index(filematch)
                        vals.pop(idx)
                        keys.pop(idx)

                        pc.setMeta('analogfile', dict(list(zip(keys, vals))))
            self.insets['SARS'].clearSelection()

        if self.pc_idx == pc_idx:
            self.pc_idx = 0
        elif self.pc_idx > pc_idx:
            self.pc_idx -= 1
        self.updateProfs()

    def isAllObserved(self):
        return all( pc.getMeta('observed') for pc in self.prof_collections )

    def isInterpolated(self):
        return self.prof_collections[self.pc_idx].isInterpolated()

    def updateProfs(self):
        logging.debug("Calling SPCWidget.updateProfs")
        
        prof_col = self.prof_collections[self.pc_idx]
        self.default_prof = prof_col.getHighlightedProf()

        # update the profiles
        self.sound.setActiveCollection(self.pc_idx, update_gui=False)
        self.hodo.setActiveCollection(self.pc_idx)

        self.storm_slinky.setProf(self.default_prof)
        self.inferred_temp_advection.setProf(self.default_prof)
        self.speed_vs_height.setProf(self.default_prof)
        self.srwinds_vs_height.setProf(self.default_prof)
        self.thetae_vs_pressure.setProf(self.default_prof)
        self.watch_type.setProf(self.default_prof)
        self.convective.setProf(self.default_prof)
        self.kinematic.setProf(self.default_prof)

        for inset in list(self.insets.keys()):
            self.insets[inset].setProf(self.default_prof)

        # Update the parcels to match the new profiles
        parcel = self.getParcelObj(self.default_prof, self.parcel_type)
        self.sound.setParcel(parcel)
        self.storm_slinky.setParcel(parcel)

        deviant = 'right' if self.default_prof.latitude >= 0 else 'left'
        self.toggleVector(deviant)

    @Slot(tab.params.Parcel)
    def updateParcel(self, pcl):
        logging.debug("Calling SPCWidget.updateParcel")

        self.parcel_type = self.getParcelName(self.default_prof, pcl)

        self.sound.setParcel(pcl)
        self.storm_slinky.setParcel(pcl)

        self.config['parcel_types', 'pcl1'] = self.convective.pcl_types[0]
        self.config['parcel_types', 'pcl2'] = self.convective.pcl_types[1]
        self.config['parcel_types', 'pcl3'] = self.convective.pcl_types[2]
        self.config['parcel_types', 'pcl4'] = self.convective.pcl_types[3]

    @Slot(str)
    def updateSARS(self, filematch):
        prof_col = self.prof_collections[self.pc_idx]

        dec = io.spc_decoder.SPCDecoder(filematch)
        match_col = dec.getProfiles()

        match_col.setMeta('model', 'Analog')
        match_col.setMeta('run', prof_col.getCurrentDate())
        match_col.setMeta('base_time', prof_col.getCurrentDate())
        match_col.setMeta('observed', True)
        match_col.setMeta('filematch', filematch)
        match_col.setAnalogToDate(prof_col.getCurrentDate())

        dt = prof_col.getCurrentDate()
        if prof_col.hasMeta('analogfile'):
            analogfiles = prof_col.getMeta('analogfile')
            analogfiles[dt] = filematch
        else:
            analogfiles = {dt:filematch}

        prof_col.setMeta('analogfile', analogfiles)

        self.parentWidget().addProfileCollection(match_col, focus=False)

    @Slot(Config)
    def updateConfig(self, config, update_gui=True):
        logging.debug("Updating the SHARPpy GUI configuration.")
        self.config = config
        prefs = dict( (field, value) for (section, field), value in config if section == 'preferences')

        self.bg_color = QColor(prefs['bg_color'])
        self.fg_color = QColor(prefs['fg_color'])

        bg_hex = "#%02x%02x%02x" % (self.bg_color.red(), self.bg_color.green(), self.bg_color.blue())
        fg_hex = "#%02x%02x%02x" % (self.fg_color.red(), self.fg_color.green(), self.fg_color.blue())

        self.sound.setPreferences(update_gui=update_gui, **prefs)
        self.hodo.setPreferences(update_gui=update_gui, **prefs)

        self.storm_slinky.setPreferences(update_gui=update_gui, **prefs)
        self.inferred_temp_advection.setPreferences(update_gui=update_gui, **prefs)
        self.speed_vs_height.setPreferences(update_gui=update_gui, **prefs)
        self.srwinds_vs_height.setPreferences(update_gui=update_gui, **prefs)
        self.thetae_vs_pressure.setPreferences(update_gui=update_gui, **prefs)
        self.watch_type.setPreferences(update_gui=update_gui, **prefs)
        self.convective.setPreferences(update_gui=update_gui, **prefs)
        self.kinematic.setPreferences(update_gui=update_gui, **prefs)

        for inset in list(self.insets.keys()):
            self.insets[inset].setPreferences(update_gui=update_gui, **prefs)

        # Edit style sheets to modify the colors as we need to (surely there's a better way to do this?)
        sheet = self.styleSheet()
        sheet = _modifySheet(sheet, 'background-color', bg_hex)
        self.setStyleSheet(sheet)
        
        sheet = self.ur.styleSheet()
        sheet = _modifySheet(sheet, 'background-color', bg_hex)
        sheet = _modifySheet(sheet, 'border-color', fg_hex)
        self.ur.setStyleSheet(sheet)

        sheet = self.brand.styleSheet()
        sheet = _modifySheet(sheet, 'background-color', bg_hex)
        sheet = _modifySheet(sheet, 'color', fg_hex)
        self.brand.setStyleSheet(sheet)

        sheet = self.text.styleSheet()
        sheet = _modifySheet(sheet, 'background-color', bg_hex)
        self.text.setStyleSheet(sheet)


    @Slot(tab.params.Parcel)
    def defineUserParcel(self, parcel):
        self.prof_collections[self.pc_idx].defineUserParcel(parcel)
        self.updateProfs()
        self.setFocus()

    @Slot(int, dict)
    def modifyProf(self, idx, kwargs):
        # TODO: Use this as a template to modify layers of the sounding
        self.prof_collections[self.pc_idx].modify(idx, **kwargs)
        self.updateProfs()
        self.setFocus()

    @Slot(str, float, float)
    def modifyVector(self, deviant, vec_u, vec_v):
        self.prof_collections[self.pc_idx].modifyStormMotion(deviant, vec_u, vec_v)
        self.updateProfs()
        self.setFocus()

    @Slot(str)
    def toggleVector(self, deviant):
        self.sound.setDeviant(deviant)
        self.hodo.setDeviant(deviant)

        self.storm_slinky.setDeviant(deviant)
        self.srwinds_vs_height.setDeviant(deviant)
        self.watch_type.setDeviant(deviant)
        self.convective.setDeviant(deviant)
        self.kinematic.setDeviant(deviant)

        self.insets['SARS'].setDeviant(deviant)
        self.insets['STP STATS'].setDeviant(deviant)
        self.insets['COND STP'].setDeviant(deviant)
        self.setFocus()

    def interpProf(self):
        self.prof_collections[self.pc_idx].interp()
        self.updateProfs()
        self.setFocus()

    @Slot(list)
    def resetProfModifications(self, args):
        self.prof_collections[self.pc_idx].resetModification(*args)
        self.updateProfs()
        self.setFocus()

    def resetProfInterpolation(self):
        self.prof_collections[self.pc_idx].resetInterpolation()
        self.updateProfs()
        self.setFocus()

    def resetVector(self):
        self.prof_collections[self.pc_idx].resetStormMotion()
        self.updateProfs()
        self.setFocus()

    @Slot()
    def toggleCollectObserved(self):
        self.coll_observed = not self.coll_observed
        self.sound.setAllObserved(self.coll_observed)
        self.hodo.setAllObserved(self.coll_observed)

    def loadWidgets(self):
        logging.debug("Calling SPCWindow.loadWidgets")
        ## add the upper-right window insets
        self.grid2.addWidget(self.speed_vs_height, 0, 0, 11, 3)
        self.grid2.addWidget(self.inferred_temp_advection, 0, 3, 11, 2)
        self.grid2.addWidget(self.hodo, 0, 5, 8, 24)
        self.grid2.addWidget(self.storm_slinky, 8, 5, 3, 6)
        self.grid2.addWidget(self.thetae_vs_pressure, 8, 11, 3, 6)
        self.grid2.addWidget(self.srwinds_vs_height, 8, 17, 3, 6)
        self.grid2.addWidget(self.watch_type, 8, 23, 3, 6)

        # Draw the kinematic and convective insets
        self.grid3.addWidget(self.convective, 0, 0)
        self.grid3.addWidget(self.kinematic, 0, 1)

        # Set Left Inset
        self.grid3.addWidget(self.left_inset_ob, 0, 2)

        # Set Right Inset
        self.grid3.addWidget(self.right_inset_ob, 0, 3)

        ## do a check for setting the dendretic growth zone
        if self.left_inset == "WINTER" or self.right_inset == "WINTER":
            self.sound.setDGZ(True)
            self.dgz = True
 
        ## Do a check for setting the pbl
        if self.left_inset == "FIRE" or self.right_inset == "FIRE":
            self.sound.setPBLLevel(True)
            self.pbl = True

        self.grid.addWidget(self.sound, 0, 0, 3, 1)
        self.grid.addWidget(self.text, 3, 0, 1, 2)

    def advanceTime(self, direction):
        logging.debug("Calling SPCWidget.advanceTime")
        if len(self.prof_collections) == 0 or self.coll_observed:
            return

        prof_col = self.prof_collections[self.pc_idx]
        if prof_col.getMeta('observed'):
            cur_dt = prof_col.getCurrentDate()
            cur_loc = prof_col.getMeta('loc')
            idxs, dts = list(zip(*sorted(((idx, pc.getCurrentDate()) for idx, pc in enumerate(self.prof_collections) if pc.getMeta('loc') == cur_loc and pc.getMeta('observed')), key=lambda x: x[1])))

            dt_idx = dts.index(cur_dt)
            dt_idx = (dt_idx + direction) % len(dts)
            self.pc_idx = idxs[dt_idx]

            cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        else:
            cur_dt = prof_col.advanceTime(direction)

        for prof_col in self.prof_collections:
            if not prof_col.getMeta('observed'):
                prof_col.setCurrentDate(cur_dt)

        self.parcel_types = self.convective.pcl_types
        self.updateProfs()

        prof_col = self.prof_collections[self.pc_idx]
        if prof_col.hasMeta('analogfile'):
            match = prof_col.getMeta('analogfile')
            dt = prof_col.getCurrentDate()
            if dt in match:
                self.insets['SARS'].setSelection(match[dt])
            else:
                self.insets['SARS'].clearSelection()
        else:
            self.insets['SARS'].setParent(self.text)
            self.insets['SARS'].clearSelection()

    def advanceHighlight(self, direction):
        self.prof_collections[self.pc_idx].advanceHighlight(direction)
        self.updateProfs()

    def swapProfCollections(self):
        logging.debug("Calling SPCWidget.swapProfCollections")
        # See if we have any other observed profiles loaded at this time.
        prof_col = self.prof_collections[self.pc_idx]
        dt = prof_col.getCurrentDate()
        idxs, pcs = list(zip(*[ (idx, pc) for idx, pc in enumerate(self.prof_collections) if pc.getCurrentDate() == dt or self.coll_observed ]))
        loc_idx = pcs.index(prof_col)
        loc_idx = (loc_idx + 1) % len(pcs)
        self.pc_idx = idxs[loc_idx]

        self.updateProfs()

        if self.prof_collections[self.pc_idx].hasMeta('analogfile'):
            match = self.prof_collections[self.pc_idx].getMeta('analogfile')
            dt = prof_col.getCurrentDate()
            if dt in match:
                self.insets['SARS'].setSelection(match[dt])
            else:
                self.insets['SARS'].clearSelection()
        else:
            self.insets['SARS'].clearSelection()

    def closeEvent(self, e):
        logging.debug("SPCWindow closeEvent:" + str(e))
        self.sound.closeEvent(e)

        for prof_coll in self.prof_collections:
            prof_coll.cancelCopy()

    def makeInsetMenu(self, *exclude):
        # This will make the menu of the available insets.
        self.popupmenu=QMenu("Inset Menu")
        self.menu_ag = QActionGroup(self, exclusive=True)

        for inset in self.available_insets:
            if inset not in exclude:
                inset_action = QAction(self)
                inset_action.setText(SPCWidget.inset_names[inset])
                inset_action.setData(inset)
                inset_action.setCheckable(True)
                inset_action.triggered.connect(self.swapInset)
                a = self.menu_ag.addAction(inset_action)
                self.popupmenu.addAction(a)

    def showCursorMenu(self, pos):
        self.makeInsetMenu(self.left_inset, self.right_inset)
        if self.childAt(pos.x(), pos.y()) is self.right_inset_ob:
            self.inset_to_swap = "RIGHT"
            self.popupmenu.popup(self.mapToGlobal(pos))
            self.setFocus()

        elif self.childAt(pos.x(), pos.y()) is self.left_inset_ob:
            self.inset_to_swap = "LEFT"
            self.popupmenu.popup(self.mapToGlobal(pos))
            self.setFocus()

    def swapInset(self):
        logging.debug("Swapping the " + self.inset_to_swap + " inset.")
        ## This will swap either the left or right inset depending on whether or not the
        ## self.inset_to_swap value is LEFT or RIGHT.
        a = self.menu_ag.checkedAction()

        prefs = dict( (field, value) for (section, field), value in self.config if section == 'preferences')

        if self.inset_to_swap == "LEFT":
            if self.left_inset == "WINTER" and self.dgz:
                self.sound.setDGZ(False)
                self.dgz = False
 
            if self.left_inset == "FIRE" and self.pbl:
                self.sound.setPBLLevel(False)
                self.pbl = False
            
            # Delete and re-make the inset.  For some stupid reason, pyside/QT forces you to 
            #   delete something you want to remove from the layout.
            self.left_inset_ob.deleteLater()
            self.insets[self.left_inset] = SPCWidget.inset_generators[self.left_inset]()
            self.insets[self.left_inset].setProf(self.default_prof)
            self.insets[self.left_inset].setPreferences(update_gui=False, **prefs)
            self.insets[self.left_inset].setParent(self.text)

            self.left_inset = a.data()
            self.left_inset_ob = self.insets[self.left_inset]
            self.grid3.addWidget(self.left_inset_ob, 0, 2)
            self.config['insets', 'left_inset'] = self.left_inset

        elif self.inset_to_swap == "RIGHT":
            if self.right_inset == "WINTER" and self.dgz:
                self.sound.setDGZ(False)
                self.dgz = False

            if self.right_inset == "FIRE" and self.pbl:
                self.sound.setPBLLevel(False)
                self.pbl = False

            # Delete and re-make the inset.  For some stupid reason, pyside/QT forces you to 
            #   delete something you want to remove from the layout.
            self.right_inset_ob.deleteLater()
            self.insets[self.right_inset] = SPCWidget.inset_generators[self.right_inset]()
            self.insets[self.right_inset].setProf(self.default_prof)
            self.insets[self.right_inset].setPreferences(update_gui=False, **prefs)
            self.insets[self.right_inset].setParent(self.text)

            self.right_inset = a.data()
            self.right_inset_ob = self.insets[self.right_inset]
            self.grid3.addWidget(self.right_inset_ob, 0, 3)
            self.config['insets', 'right_inset'] = self.right_inset

        if a.data() == "WINTER":
            self.sound.setDGZ(True)
            self.dgz = True
        if a.data() == "FIRE":
            self.sound.setPBLLevel(True)
            self.pbl = True
 
        self.setFocus()
        self.update()

class SPCWindow(QMainWindow):
    closed = Signal()

    def __init__(self, **kwargs):
        parent = kwargs.get('parent', None)
        super(SPCWindow, self).__init__(parent=parent)
        logging.debug("Initialize SPCWindow...")
        self.menu_items = []
        self.picker_window = parent
        self.__initUI(**kwargs)

    def __initUI(self, **kwargs):
        kwargs['parent'] = self
        self.spc_widget = SPCWidget(**kwargs)
        self.parent().config_changed.connect(self.spc_widget.updateProfs)
        self.parent().config_changed.connect(self.updateConfig)
        self.setCentralWidget(self.spc_widget)
        self.createMenuBar()

        logging.debug("Determining system platform to resize the window.")
        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        self.setWindowTitle(title)

        bg_hex = self.spc_widget.config['preferences', 'bg_color']
        self.setStyleSheet("QMainWindow { background-color: " + bg_hex + "; }")
        
        ## handle the attribute of the main window
        if platform.system() == 'Windows':
            self.setGeometry(10,30,1180,800)
        else:
            self.setGeometry(0, 0, 1180, 800)

        self.show()
        self.raise_()

    def createMenuBar(self):
        logging.debug("Creating the SPCWindow Menu Bar.")
        bar = self.menuBar()
        filemenu = bar.addMenu("File")

        pref = QAction("Preferences", self)
        filemenu.addAction(pref)
        pref.triggered.connect(self.parent().preferencesbox)

        saveimage = QAction("Save Image", self, shortcut=QKeySequence("Ctrl+S"))
        saveimage.triggered.connect(self.spc_widget.saveimage)
        filemenu.addAction(saveimage)

        savetext = QAction("Save Text", self, shortcut=QKeySequence("Ctrl+Shift+S"))
        savetext.triggered.connect(self.spc_widget.savetext)
        filemenu.addAction(savetext)

        self.profilemenu = bar.addMenu("Profiles")

        self.allobserved = QAction("Collect Observed", self, checkable=True, shortcut=QKeySequence("C"))
        self.allobserved.triggered.connect(self.spc_widget.toggleCollectObserved)
        self.profilemenu.addAction(self.allobserved)

        self.interpolate = QAction("Interpolate Focused Profile", self, shortcut=QKeySequence("I"))
        self.interpolate.triggered.connect(self.interpProf)
        self.profilemenu.addAction(self.interpolate)

        self.resetinterp = QAction("Reset Interpolation", self, shortcut=QKeySequence("I"))
        self.resetinterp.triggered.connect(self.resetProf)
        self.resetinterp.setVisible(False)
        self.profilemenu.addAction(self.resetinterp)

        self.profilemenu.addSeparator()

        self.focus_mapper = QSignalMapper(self)
        self.remove_mapper = QSignalMapper(self)

        self.focus_mapper.mapped[str].connect(self.spc_widget.setProfileCollection)
        self.remove_mapper.mapped[str].connect(self.rmProfileCollection)

    def createProfileMenu(self, prof_col):
        logging.debug("Creating the SPCWindow Profile Menu.")
        menu_name = self.createMenuName(prof_col)
        prof_menu = self.profilemenu.addMenu(menu_name)

        focus = QAction("Focus", self)
        focus.triggered.connect(self.focus_mapper.map)
        self.focus_mapper.setMapping(focus, menu_name)
        prof_menu.addAction(focus)

        remove = QAction("Remove", self)
        remove.triggered.connect(self.remove_mapper.map)
        self.remove_mapper.setMapping(remove, menu_name)
        prof_menu.addAction(remove)

        if len(self.menu_items) == 0:
            remove.setVisible(False)

        self.menu_items.append(prof_menu)

    def removeProfileMenu(self, menu_name):
        menu_items = [ mitem for mitem in self.menu_items if mitem.title() == menu_name ]
        for mitem in menu_items:
            mitem.menuAction().setVisible(False)

    def addProfileCollection(self, prof_col, focus=True, check_integrity=True):
        logging.debug("Calling SPCWindow.addProfileCollection")

        if check_integrity is True:
            logging.debug("Testing data integrity")
            exit_code = self.testDataIntegrity(prof_col.getHighlightedProf())
            if exit_code == 0:
                if len(self.menu_items) == 0:
                    self.focusPicker()
                    self.close()
                else:
                    return

        menu_name = self.createMenuName(prof_col)
        if any( mitem.title() == menu_name and mitem.menuAction().isVisible() for mitem in self.menu_items ):
            self.spc_widget.setProfileCollection(menu_name)
            return
            
        if not prof_col.getMeta('observed'):
            self.allobserved.setDisabled(True)
            self.allobserved.setChecked(False)

        self.createProfileMenu(prof_col)

        visible_mitems = [ mitem for mitem in self.menu_items if mitem.menuAction().isVisible() ]
        if len(visible_mitems) > 1:
            actions = visible_mitems[0].actions()
            names = [ act.text() for act in actions ]
            actions[names.index("Remove")].setVisible(True)

        try:
            self.spc_widget.addProfileCollection(prof_col, menu_name, focus=focus)
        except Exception as exc:
            print("OOPS:", exc)
            ### TODO: This may be a good place to output a copy of the offending data (useful for debugging observed data).
            if len(self.menu_items) == 1:
                self.focusPicker()
                self.close()
            else:
                self.rmProfileCollection(menu_name)
            raise

    def testDataIntegrity(self, prof):
        try:
            prof.checkDataIntegrity()
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setText("SHARPpy has detected that the data you are attempting to load may have errors.")
            msgBox.setInformativeText("Do you want to still try and load the data?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            msgBox.setDetailedText(str(e).split(',')[1].replace(')', ''))
            ret = msgBox.exec_()
            if ret == QMessageBox.Yes:
                return 1
            else:
                return 0
        return 1


    @Slot(str)
    def rmProfileCollection(self, menu_name):
        logging.debug("Calling SPCWindow.rmProfileCollection")
        self.removeProfileMenu(menu_name)
        self.spc_widget.rmProfileCollection(menu_name)

        if self.spc_widget.isAllObserved():
            self.allobserved.setDisabled(False)

        visible_mitems = [ mitem for mitem in self.menu_items if mitem.menuAction().isVisible() ]
        if len(visible_mitems) == 1:
            actions = visible_mitems[0].actions()
            names = [ act.text() for act in actions ]
            actions[names.index("Remove")].setVisible(False)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left: # Step forward/backwards in time
            self.spc_widget.advanceTime(-1)
            self.setInterpolated(self.spc_widget.isInterpolated())
        elif e.key() == Qt.Key_Right:
            self.spc_widget.advanceTime(1)
            self.setInterpolated(self.spc_widget.isInterpolated())
        elif e.key() == Qt.Key_Up: # Change focus from member to member of the ensemble
            self.spc_widget.advanceHighlight(1)
        elif e.key() == Qt.Key_Down:
            self.spc_widget.advanceHighlight(-1)
        elif e.key() == Qt.Key_Space:
            # Swap the profile collections
            self.spc_widget.swapProfCollections()
            self.setInterpolated(self.spc_widget.isInterpolated())
        elif e.matches(QKeySequence.Save):
            # Save an image
            self.spc_widget.saveimage()
        elif e.key() == Qt.Key_W:
            # Return focus to the Sounding Picker
            self.focusPicker()

    def closeEvent(self, e):
        logging.debug("Calling SPCWindow.closeEvent")

        self.spc_widget.closeEvent(e)
        self.closed.emit()

    def closeIfEmpty(self):
        logging.debug("Calling SPCWindow.closeIfEmpty")
        visible_mitems = [ mitem for mitem in self.menu_items if mitem.menuAction().isVisible() ]
        if len(visible_mitems) < 1:
            self.close()

    def createMenuName(self, prof_col):
        pc_loc = prof_col.getMeta('loc')
        pc_date = prof_col.getMeta('run').strftime("%d/%H%MZ")
        pc_model = prof_col.getMeta('model')

        return "%s (%s %s)" % (pc_loc, pc_date, pc_model)

    def interpProf(self):
        self.setInterpolated(True)
        self.spc_widget.interpProf()

    def resetProf(self):
        self.setInterpolated(False)
        self.spc_widget.resetProfInterpolation()

    def setInterpolated(self, is_interpolated):
        self.resetinterp.setVisible(is_interpolated)
        self.interpolate.setVisible(not is_interpolated)

    @Slot()
    def updateConfig(self):
        bg_hex = self.spc_widget.config['preferences', 'bg_color']
        sheet = self.styleSheet()
        sheet = _modifySheet(sheet, 'background-color', bg_hex)
        self.setStyleSheet(sheet)
        self.update()

    def focusPicker(self):
        logging.debug("Calling SPCWindow.focusPicker")
        if self.picker_window is not None:
            self.picker_window.activateWindow()
            self.picker_window.setFocus()
            self.picker_window.raise_()

if __name__ == '__main__':
    app_frame = QApplication([])    
    tester = SPCWindow()
    tester.show()    
    app_frame.exec_()
