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
import sharppy.databases.sars as sars
from datetime import datetime, timedelta
import copy
import numpy as np
import ConfigParser
import platform
from time import sleep
from os.path import expanduser
from sharppy.version import __version__, __version_name__

class SkewApp(QWidget):
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

    cfg_file_name = 'sharppy.ini'

    def __init__(self, profs, dates, model, **kwargs):

        super(SkewApp, self).__init__()
        """
        """
        ## these are the keyword arguments used to define what
        ## sort of profile is being viewed
        self.profs = profs
        self.proflist = []
        self.dates = dates
        self.model = model
        self.prof_idx = kwargs.get("idx")
        self.run = kwargs.get("run")
        self.loc = kwargs.get("location")
        self.fhour = kwargs.get("fhour", [ None ])
        self.dgz = False

        self.plot_title = ""

        ## these are used to display profiles
        self.current_idx = 0
        self.prof = profs[self.current_idx]
        self.original_profs = self.profs[:]
        self.modified_skew = [ False for p in self.original_profs ]
        self.modified_hodo = [ False for p in self.original_profs ]
        self.parcel_type = "MU"

        self.config = ConfigParser.RawConfigParser()
        self.config.read(SkewApp.cfg_file_name)
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
        insets = sorted(SkewApp.inset_names.items(), key=lambda i: i[1])
        inset_ids, inset_names = zip(*insets)
        self.available_insets = inset_ids
        self.left_inset = self.config.get('insets', 'left_inset')
        self.right_inset = self.config.get('insets', 'right_inset')
        self.insets = {}

        self.parcel_types = [self.config.get('parcel_types', 'pcl1'), self.config.get('parcel_types', 'pcl2'), \
                             self.config.get('parcel_types', 'pcl3'),self.config.get('parcel_types', 'pcl4')]

        ## initialize the rest of the window attributes, layout managers, etc

        ## handle the attribute of the main window
        if platform.system() == 'Windows':
            self.setGeometry(10,30,1180,800)
        else:
            self.setGeometry(0, 0, 1180, 800)
        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        self.setWindowTitle(title)
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
        modified = self.modified_skew[self.current_idx] or self.modified_hodo[self.current_idx]
        modified_str = "; Modified" if modified else ""

        plot_title = self.loc + '   ' + datetime.strftime(self.dates[self.current_idx], "%Y%m%d/%H%M")
        if self.model == "Archive":
            plot_title += "  (User Selected" + modified_str + ")"
        elif self.fhour == [ 'F000' ]:
            plot_title += "  (Observed" + modified_str + ")"
        else:
             plot_title += "  (" + self.run + "  " + self.model + "  " + self.fhour[self.current_idx] + modified_str + ")"
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

        ## set the plot title that will be displayed in the Skew frame.
        self.plot_title = self.getPlotTitle()
        default_pcl = self.prof.mupcl

        if self.model == "SREF":
            self.prof = self.profs[self.current_idx][0]
            self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_idx][:], dgz=self.dgz)
            self.hodo = plotHodo(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof,
                                 proflist=self.profs[self.current_idx][:], parent=self)
        else:
            self.prof = self.profs[self.current_idx]
            self.sound = plotSkewT(self.prof, pcl=default_pcl, title=self.plot_title, brand=self.brand,
                                   dgz=self.dgz, proflist=self.proflist)
            self.sound.updated.connect(self.updateProfs)
            self.sound.reset.connect(self.resetProf)
            self.hodo = plotHodo(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof, parent=self,
                                 proflist=self.proflist)

        ## initialize the non-swappable insets
        self.speed_vs_height = plotSpeed( self.prof )

        self.inferred_temp_advection = plotAdvection(self.prof)



        self.hodo.updated.connect(self.updateProfs)
        self.hodo.reset.connect(self.resetProf)

        self.storm_slinky = plotSlinky(self.prof, pcl=default_pcl)
        self.thetae_vs_pressure = plotGeneric(self.prof.thetae[self.prof.pres > 500.],
                                self.prof.pres[self.prof.pres > 500.], xticks=np.arange(220,360,10),
                                 yticks=np.arange(500, 1000, 100), title="ThetaE v.\nPres" )

        self.srwinds_vs_height = plotWinds(self.prof)
        self.watch_type = plotWatch(self.prof)
        self.convective = plotText(self.prof, self.parcel_types)
        self.kinematic = plotKinematics(self.prof)

        self.convective.updatepcl.connect(self.updateParcel)

        self.makeInsets()
        self.insets["SARS"].updatematch.connect(self.updateSARS)
        self.right_inset_ob = self.insets[self.right_inset]
        self.left_inset_ob = self.insets[self.left_inset]

    def makeInsets(self):
        """
        Create the swappable insets
        :return:
        """

        for inset, inset_gen in SkewApp.inset_generators.iteritems():
            self.insets[inset] = inset_gen(self.prof)


    @Slot(profile.Profile, str, bool) # Note to myself...could add an additional argument to allow emit to change pcl types to be shown.
    def updateProfs(self, prof, panel, modified):
        if panel == 'skew':
            self.modified_skew[self.current_idx] = modified
        elif panel == 'hodo':
            self.modified_hodo[self.current_idx] = modified

        self.plot_title = self.getPlotTitle()
        if self.model == "SREF":
            self.profs[self.current_idx][0] = prof[0]
            self.prof = self.profs[self.current_idx][0]
            self.sound.setProf(self.prof, pcl=self.getParcelObj(self.prof, self.parcel_type), title=self.plot_title,
                               brand=self.brand, proflist=self.profs[self.current_idx][:], dgz=self.dgz)
            self.hodo.setProf(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof,
                              proflist=self.profs[self.current_idx][:], parent=self)
        else:
            self.profs[self.current_idx] = prof
            self.prof = self.profs[self.current_idx]
            self.sound.setProf(self.prof, pcl=self.getParcelObj(self.prof, self.parcel_type), title=self.plot_title,
                               brand=self.brand, dgz=self.dgz, proflist=self.proflist)
            self.hodo.setProf(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof,
                              proflist=self.proflist, parent=self)

        self.storm_slinky.setProf(self.prof, self.getParcelObj(self.prof, self.parcel_type))

        self.inferred_temp_advection.setProf(self.prof)

        self.speed_vs_height.setProf(self.prof)

        self.srwinds_vs_height.setProf(self.prof)

        self.thetae_vs_pressure.setProf(self.prof.thetae[self.prof.pres > 500.],
                                self.prof.pres[self.prof.pres > 500.], xticks=np.arange(220,360,10),
                                 yticks=np.arange(500, 1000, 100), title="ThetaE v.\nPres" )

        self.watch_type.setProf(self.prof)

        self.convective.setProf(self.prof, self.convective.pcl_types)
        self.kinematic.setProf(self.prof)



        for inset in self.insets.keys():
            self.insets[inset].setProf(self.prof)

    @Slot(str)
    def resetProf(self, panel):
        current = self.profs[self.current_idx]
        orig = self.original_profs[self.current_idx]
        self.proflist = []

        if panel == 'hodo':
            kwargs = {'u':orig.u, 'v':orig.v}
        elif panel == 'skew':
            kwargs = {'tmpc':orig.tmpc, 'dwpc':orig.dwpc}

        self.profs[self.current_idx] = type(current).copy(current, **kwargs)

        self.updateProfs(self.profs[self.current_idx], panel, modified=False) #, pcl=self.getParcelObj(self.profs[self.current_idx], self.parcel_type))
        self.setFocus()

    @Slot(tab.params.Parcel)
    def updateParcel(self, pcl):
        modified_str = ""
        self.parcel_type = self.getParcelName(self.prof, pcl)

        self.plot_title = self.getPlotTitle()
        if self.model == "SREF":
            self.sound.setProf(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_idx][:], dgz=self.dgz)
        else:
            self.sound.setProf(self.prof, pcl=pcl, title=self.plot_title, brand=self.brand,
                               dgz=self.dgz, proflist=self.proflist)

        self.storm_slinky.setProf(self.prof, pcl=pcl)

        self.config.set('parcel_types', 'pcl1', self.convective.pcl_types[0])
        self.config.set('parcel_types', 'pcl2', self.convective.pcl_types[1])
        self.config.set('parcel_types', 'pcl3', self.convective.pcl_types[2])
        self.config.set('parcel_types', 'pcl4', self.convective.pcl_types[3])

    @Slot(str)
    def updateSARS(self, filematch):
        if self.model != "SREF":
            self.proflist = []
#           data = io.spc_decoder.SNDFile(filematch)
#           matchprof = tab.profile.create_profile(pres=data.pres, hght=data.hght,
#                                              tmpc=data.tmpc, dwpc=data.dwpc,
#                                              wspd=data.wspd, wdir=data.wdir,
#                                              profile="convective")

            if filematch != "":
                dec = io.spc_decoder.SPCDecoder(filematch)
                matchprof = dec.getProfiles()[0]

                self.proflist.append(matchprof)

            self.sound.setProf(self.prof, pcl=self.getParcelObj(self.prof, self.parcel_type), title=self.plot_title,
                           brand=self.brand, dgz=self.dgz, proflist=self.proflist)
            self.hodo.setProf(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof, parent=self,
                              proflist=self.proflist)

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

    def keyPressEvent(self, e):
        key = e.key()
        length = len(self.profs)
        if key == Qt.Key_Right:
            if self.current_idx != length - 1:
                self.current_idx += 1
            else:
                self.current_idx = 0
            self.parcel_types = self.convective.pcl_types
            self.updateProfs(self.profs[self.current_idx], 'none', False)
            self.updateSARS("")
            self.insets['SARS'].clearSelection()
            return

        if key == Qt.Key_Left:
            if self.current_idx != 0:
                self.current_idx -= 1
            elif self.current_idx == 0:
                self.current_idx = length -1
            self.parcel_types = self.convective.pcl_types
            self.updateProfs(self.profs[self.current_idx], 'none', False)
            self.updateSARS("")
            self.insets['SARS'].clearSelection()
            return

        if e.matches(QKeySequence.Save):
            # Save an image
            self.saveimage()
            return

    def closeEvent(self, e):
        self.config.write(open(SkewApp.cfg_file_name, 'w'))
        self.sound.closeEvent(e)

    def makeInsetMenu(self, *exclude):

        # This will make the menu of the available insets.
        self.popupmenu=QMenu("Inset Menu")
        self.menu_ag = QActionGroup(self, exclusive=True)

        for inset in self.available_insets:
            if inset not in exclude:
                inset_action = QAction(self)
                inset_action.setText(SkewApp.inset_names[inset])
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
            self.left_inset_ob.deleteLater()
            self.insets[self.left_inset] = SkewApp.inset_generators[self.left_inset](self.prof)

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
            self.right_inset_ob.deleteLater()
            self.insets[self.right_inset] = SkewApp.inset_generators[self.right_inset](self.prof)

            self.right_inset = a.data()
            self.right_inset_ob = self.insets[self.right_inset]
            self.grid3.addWidget(self.right_inset_ob, 0, 3)
            self.config.set('insets', 'right_inset', self.right_inset)

        if a.data() == "WINTER":
            self.sound.setDGZ(True)
            self.dgz = True

        self.setFocus()
        self.update()
