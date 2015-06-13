__author__ = 'keltonhalbert, wblumberg'

from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics, plotGeneric
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP, plotWinter
from sharppy.viz import plotSHIP, plotSTPEF, plotFire, plotVROT
from PySide.QtCore import *
from PySide.QtGui import *
import sharppy.sharptab.profile as profile
import sharppy.sharptab as tab
import sharppy.io as io
from datetime import datetime, timedelta
import numpy as np
import platform
from os.path import expanduser
import os
from sharppy.version import __version__, __version_name__

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

    def __init__(self, **kwargs):

        super(SPCWidget, self).__init__()
        """
        """
        ## these are the keyword arguments used to define what
        ## sort of profile is being viewed
        self.prof_collections = []
        self.pc_idx = 0
        self.config = kwargs.get("cfg")
        self.dgz = False
        self.plot_title = ""

        ## these are used to display profiles
        self.parcel_type = "MU"

        if not self.config.has_section('insets'):
            self.config.add_section('insets')
            self.config.set('insets', 'right_inset', 'STP STATS')
            self.config.set('insets', 'left_inset', 'SARS')
        if not self.config.has_section('parcel_types'):
            self.config.add_section('parcel_types')
            self.config.set('parcel_types', 'pcl1', 'SFC')
            self.config.set('parcel_types', 'pcl2', 'ML')
            self.config.set('parcel_types', 'pcl3', 'FCST')
            self.config.set('parcel_types', 'pcl4', 'MU')

        ## these are the boolean flags used throughout the program
        self.swap_inset = False

        ## initialize empty variables to hold objects that will be
        ## used later
        self.left_inset_ob = None
        self.right_inset_ob = None

        ## these are used for insets and inset swapping
        insets = sorted(SPCWidget.inset_names.items(), key=lambda i: i[1])
        inset_ids, inset_names = zip(*insets)
        self.available_insets = inset_ids
        self.left_inset = self.config.get('insets', 'left_inset')
        self.right_inset = self.config.get('insets', 'right_inset')
        self.insets = {}

        self.parcel_types = [self.config.get('parcel_types', 'pcl1'), self.config.get('parcel_types', 'pcl2'), \
                             self.config.get('parcel_types', 'pcl3'),self.config.get('parcel_types', 'pcl4')]

        ## initialize the rest of the window attributes, layout managers, etc

        self.setStyleSheet("QWidget {background-color: rgb(0, 0, 0);}")
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
        self.urparent.setLayout(self.urparent_grid)
        self.ur = QFrame()
        self.ur.setStyleSheet("QFrame {"
                         "  background-color: rgb(0, 0, 0);"
                         "  border-width: 0px;"
                         "  border-style: solid;"
                         "  border-color: rgb(255, 255, 255);"
                         "  margin: 0px;}")

        self.brand = QLabel("SHARPpy Beta v%s %s" % (__version__, __version_name__))
        self.brand.setAlignment(Qt.AlignRight)
        self.brand.setStyleSheet("QFrame {"
                             "  background-color: rgb(0, 0, 0);"
                             "  text-align: right;"
                             "  font-size: 11px;"
                             "  color: #FFFFFF;}")

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
                            "  background-color: rgb(0, 0, 0);"
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

    def getPlotTitle(self):
        modified = self.prof_collections[self.pc_idx].isModified()
        modified_str = "; Modified" if modified else ""

        prof_col = self.prof_collections[self.pc_idx]
        loc = prof_col.getMeta('loc')
        date = prof_col.getCurrentDate()
        run = prof_col.getMeta('run')
        model = prof_col.getMeta('model')
        observed = prof_col.getMeta('observed')

        plot_title = loc + '   ' + datetime.strftime(date, "%Y%m%d/%H%M")
        if model == "Archive":
            plot_title += "  (User Selected" + modified_str + ")"
        elif observed:
            plot_title += "  (Observed" + modified_str + ")"
        else:
            fhour = self.prof_collections[self.pc_idx].getMeta('fhour', index=True)
            plot_title += "  (" + run + "  " + model + "  " + fhour + modified_str + ")"
        return plot_title

    def saveimage(self):
        self.home_path = expanduser('~')
        files_types = "PNG (*.png)"
        fileName, result = QFileDialog.getSaveFileName(self, "Save Image", self.home_path, files_types)
        if result:
            pixmap = QPixmap.grabWidget(self)
            pixmap.save(fileName, 'PNG', 100)

    def initData(self):
        """
        Initializes all the widgets for the window.
        This gets initially called by __init__
        :return:
        """

        self.sound = plotSkewT(dgz=self.dgz)
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

        # intialize swappable insets
        for inset, inset_gen in SPCWidget.inset_generators.iteritems():
            self.insets[inset] = inset_gen()

        self.right_inset_ob = self.insets[self.right_inset]
        self.left_inset_ob = self.insets[self.left_inset]

        # Connect signals to slots
        self.convective.updatepcl.connect(self.updateParcel)

        self.sound.parcel.connect(self.defineUserParcel)
        self.sound.modified.connect(self.modifyProf)
        self.sound.reset.connect(self.resetProf)

        self.hodo.modified.connect(self.modifyProf)
        self.hodo.reset.connect(self.resetProf)

        self.insets["SARS"].updatematch.connect(self.updateSARS)

    def addProfileCollection(self, prof_col):
        self.prof_collections.append(prof_col)
        self.pc_idx = len(self.prof_collections) - 1

        cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        for prof_col in self.prof_collections:
            prof_col.setCurrentDate(cur_dt)

        self.updateProfs()

    def updateProfs(self):
        profs = self.prof_collections[self.pc_idx].getCurrentProfs().values()
        default_prof = self.prof_collections[self.pc_idx].getHighlightedProf()

        self.plot_title = self.getPlotTitle()

        # update the profiles
        self.sound.setProf(default_prof, title=self.plot_title, proflist=profs)
        self.hodo.setProf(default_prof, proflist=profs)

        self.storm_slinky.setProf(default_prof)
        self.inferred_temp_advection.setProf(default_prof)
        self.speed_vs_height.setProf(default_prof)
        self.srwinds_vs_height.setProf(default_prof)
        self.thetae_vs_pressure.setProf(default_prof)
        self.watch_type.setProf(default_prof)
        self.convective.setProf(default_prof)
        self.kinematic.setProf(default_prof)

        for inset in self.insets.keys():
            self.insets[inset].setProf(default_prof)

        # Update the parcels to match the new profiles
        parcel = self.getParcelObj(default_prof, self.parcel_type)
        self.sound.setParcel(parcel)
        self.storm_slinky.setParcel(parcel)

    @Slot(tab.params.Parcel)
    def updateParcel(self, pcl):

        default_prof = self.prof_collections[self.pc_idx].getHighlightedProf()
        self.parcel_type = self.getParcelName(default_prof, pcl)

        self.sound.setParcel(pcl)
        self.storm_slinky.setParcel(pcl)

        self.config.set('parcel_types', 'pcl1', self.convective.pcl_types[0])
        self.config.set('parcel_types', 'pcl2', self.convective.pcl_types[1])
        self.config.set('parcel_types', 'pcl3', self.convective.pcl_types[2])
        self.config.set('parcel_types', 'pcl4', self.convective.pcl_types[3])

    @Slot(str)
    def updateSARS(self, filematch):
        prof_col = self.prof_collections[self.pc_idx]
        if not prof_col.isEnsemble():

            profs = prof_col.getCurrentProfs().values()
            default_prof = prof_col.getHighlightedProf()

            if filematch != "":
                dec = io.spc_decoder.SPCDecoder(filematch)
                matchprof = dec.getProfiles().getHighlightedProf()

                profs.append(matchprof)

            self.sound.setProf(default_prof, title=self.plot_title, proflist=profs)
            self.hodo.setProf(default_prof, proflist=profs)

    @Slot(tab.params.Parcel)
    def defineUserParcel(self, parcel):
        self.prof_collections[self.pc_idx].defineUserParcel(parcel)
        self.updateProfs()
        self.setFocus()

    @Slot(int, dict)
    def modifyProf(self, idx, kwargs):
        self.prof_collections[self.pc_idx].modify(idx, **kwargs)
        self.updateProfs()
        self.setFocus()

    @Slot(list)
    def resetProf(self, args):
        self.prof_collections[self.pc_idx].reset(*args)

        self.updateProfs()
        self.setFocus()

    def loadWidgets(self):
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

        self.grid.addWidget(self.sound, 0, 0, 3, 1)
        self.grid.addWidget(self.text, 3, 0, 1, 2)

    def advanceTime(self, direction):
        if len(self.prof_collections) == 0:
            return

        cur_dt = self.prof_collections[self.pc_idx].advanceTime(direction)
        for prof_col in self.prof_collections:
            prof_col.setCurrentDate(cur_dt)

        self.parcel_types = self.convective.pcl_types
        self.updateProfs()
        self.updateSARS("")
        self.insets['SARS'].clearSelection()

    def swapProfCollections(self):
        n_coll = len(self.prof_collections)
        idx = (self.pc_idx + 1) % n_coll

        while not self.prof_collections[idx % n_coll].hasCurrentProf():
            idx = (idx + 1) % n_coll

        self.pc_idx = idx

        self.updateProfs()
        self.updateSARS("")
        self.insets['SARS'].clearSelection()

    def closeEvent(self, e):
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
        ## This will swap either the left or right inset depending on whether or not the
        ## self.inset_to_swap value is LEFT or RIGHT.
        a = self.menu_ag.checkedAction()

        if self.inset_to_swap == "LEFT":
            if self.left_inset == "WINTER" and self.dgz:
                self.sound.setDGZ(False)
                self.dgz = False

            # Delete and re-make the inset.  For some stupid reason, pyside/QT forces you to 
            #   delete something you want to remove from the layout.
            default_prof = self.prof_collections[self.pc_idx].getHighlightedProf()
            self.left_inset_ob.deleteLater()
            self.insets[self.left_inset] = SPCWidget.inset_generators[self.left_inset]()
            self.insets[self.left_inset].setProf(default_prof)

            self.left_inset = a.data()
            self.left_inset_ob = self.insets[self.left_inset]
            self.grid3.addWidget(self.left_inset_ob, 0, 2)
            self.config.set('insets', 'left_inset', self.left_inset)

        elif self.inset_to_swap == "RIGHT":
            if self.right_inset == "WINTER" and self.dgz:
                self.sound.setDGZ(False)
                self.dgz = False

            # Delete and re-make the inset.  For some stupid reason, pyside/QT forces you to 
            #   delete something you want to remove from the layout.
            default_prof = self.prof_collections[self.pc_idx].getHighlightedProf()
            self.right_inset_ob.deleteLater()
            self.insets[self.right_inset] = SPCWidget.inset_generators[self.right_inset]()
            self.insets[self.right_inset].setProf(default_prof)

            self.right_inset = a.data()
            self.right_inset_ob = self.insets[self.right_inset]
            self.grid3.addWidget(self.right_inset_ob, 0, 3)
            self.config.set('insets', 'right_inset', self.right_inset)

        if a.data() == "WINTER":
            self.sound.setDGZ(True)
            self.dgz = True

        self.setFocus()
        self.update()

class SPCWindow(QMainWindow):
    closed = Signal()

    def __init__(self, **kwargs):
        super(SPCWindow, self).__init__()

        self.__initUI(**kwargs)

    def __initUI(self, **kwargs):
        self.spc_widget = SPCWidget(**kwargs)
        self.setCentralWidget(self.spc_widget)

        self.createMenuBar()

        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        self.setWindowTitle(title)

        ## handle the attribute of the main window
        if platform.system() == 'Windows':
            self.setGeometry(10,30,1180,800)
        else:
            self.setGeometry(0, 0, 1180, 800)

        self.show()
        self.raise_()

    def createMenuBar(self):
        bar = self.menuBar()
        filemenu = bar.addMenu("File")

        saveimage = QAction("Save Image", self, shortcut=QKeySequence("Ctrl+S"))
        saveimage.triggered.connect(self.spc_widget.saveimage)
        filemenu.addAction(saveimage)

        savetext = QAction("Save Text", self)
        filemenu.addAction(savetext)

    def addProfileCollection(self, prof_col):
        self.spc_widget.addProfileCollection(prof_col)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.spc_widget.advanceTime(-1)
        elif e.key() == Qt.Key_Right:
            self.spc_widget.advanceTime(1)
        elif e.key() == Qt.Key_Space:
            self.spc_widget.swapProfCollections()
        elif e.matches(QKeySequence.Save):
            # Save an image
            self.spc_widget.saveimage()
            return

    def closeEvent(self, e):
        self.spc_widget.closeEvent(e)
        self.closed.emit()
