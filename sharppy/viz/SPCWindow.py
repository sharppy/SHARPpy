__author__ = 'keltonhalbert, wblumberg'

from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics, plotGeneric
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP, plotWinter
from sharppy.viz import plotSHIP, plotSTPEF, plotFire, plotVROT
from PySide.QtCore import *
from PySide.QtGui import *
from sharppy.io.buf_decoder import BufkitFile
import sharppy.sharptab.profile as profile
from StringIO import StringIO
from datetime import datetime
import urllib
import numpy as np

class Thread(QThread):
    progress = Signal()
    def __init__(self, **kwargs):
        super(Thread, self).__init__()
        self.model = kwargs.get("model")
        self.runtime = kwargs.get("run")
        self.loc = kwargs.get("loc")
        self.prof_idx = kwargs.get("idx")
        self.profs = []
        self.d = None

    def returnData(self):
        return self.profs, self.d

    def make_profile(self, i):
        d = self.d
        prof = profile.create_profile(profile='convective', hght = d.hght[0][i],
                tmpc = d.tmpc[0][i], dwpc = d.dwpc[0][i], pres = d.pres[0][i],
                wspd=d.wspd[0][i], wdir=d.wdir[0][i])
        return prof

    def __modelProf(self):
        if self.model == "GFS":
            d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/' + self.model + '/' + self.runtime[:-1] + '/'
                + self.model.lower() + '3_' + self.loc.lower() + '.buf')
        else:
            d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/' + self.model + '/' + self.runtime[:-1] + '/'
                + self.model.lower() + '_' + self.loc.lower() + '.buf')
        self.d = d

        if self.model == "SREF":
            for i in self.prof_idx:
                profs = []
                for j in range(len(d.wdir)):
                    ##print "MAKING PROFILE OBJECT: " + datetime.strftime(d.dates[i], '%Y%m%d/%H%M')
                    if j == 0:
                        profs.append(profile.create_profile(profile='convective', omeg = d.omeg[j][i], hght = d.hght[j][i],
                        tmpc = d.tmpc[j][i], dwpc = d.dwpc[j][i], pres = d.pres[j][i], wspd=d.wspd[j][i], wdir=d.wdir[j][i]))
                        self.progress.emit()
                    else:
                        profs.append(profile.create_profile(profile='default', omeg = d.omeg[j][i], hght = d.hght[j][i],
                        tmpc = d.tmpc[j][i], dwpc = d.dwpc[j][i], pres = d.pres[j][i], wspd=d.wspd[j][i], wdir=d.wdir[j][i]))
                self.profs.append(profs)

        else:
            for i in self.prof_idx:
                ##print "MAKING PROFILE OBJECT: " + datetime.strftime(d.dates[i], '%Y%m%d/%H%M')
                self.profs.append(profile.create_profile(profile='convective', omeg = d.omeg[0][i], hght = d.hght[0][i],
                    tmpc = d.tmpc[0][i], dwpc = d.dwpc[0][i], pres = d.pres[0][i], wspd=d.wspd[0][i], wdir=d.wdir[0][i]))
                self.progress.emit()


    def run(self):
        self.__modelProf()


class SkewApp(QWidget):
    """
    This will create the full SPC window, handle the organization
    of the insets, and handle all click/key events and features.
    """

    def __init__(self, **kwargs):

        super(SkewApp, self).__init__()
        """
        """
        ## these are the keyword arguments used to define what
        ## sort of profile is being viewed
        self.model = kwargs.get("model")
        self.prof_time = kwargs.get("prof_time", None)
        self.prof_idx = kwargs.get("idx")
        self.run = kwargs.get("run")
        self.loc = kwargs.get("location")
        self.link = kwargs.get("path", None)
        self.dgz = False

        self.progressDialog = QProgressDialog()

        ## these are the boolean flags used throughout the program
        self.changeflag = True
        self.swap_inset = False

        ## initialize empty variables to hold objects that will be
        ## used later
        self.d = None
        self.left_inset_ob = None
        self.right_inset_ob = None

        ## these are used for insets and inset swapping
        self.avaliable_insets = ["SARS", "STP STATS", 'COND STP', 'WINTER', 'FIRE', 'SHIP', 'VROT']
        self.left_inset = "SARS"
        self.right_inset = "STP STATS"
        self.insets = {}
        self.makeInsetMenu()

        ## these are used to display profiles
        self.current_idx = 0
        self.profs = []

        ## determine what type of data is to be loaded
        ## if the profile is an observed sounding, load
        ## from the SPC website
        if self.model == "Observed":
            self.prof, self.plot_title = self.__observedProf()
            self.profs.append(self.prof)

        ## if the profile is an archived file, load the file from
        ## the hard disk
        elif self.model == "Archive":
            self.prof, self.plot_title = self.__archiveProf()
            self.profs.append(self.prof)

        ## if the profile is a model profile, load it from the model
        ## download thread
        else:
            self.progressDialog.setMinimum(0)
            self.progressDialog.setMaximum(len(self.prof_idx))
            self.progressDialog.setValue(0)
            self.progressDialog.setLabelText("Profile 0/" + str(len(self.prof_idx)))
            self.thread = Thread(model=self.model, loc=self.loc, run=self.run, idx=self.prof_idx)
            self.thread.progress.connect(self.progress_bar)
            self.thread.start()
            self.progressDialog.open()
            while not self.thread.isFinished():
                QCoreApplication.processEvents()
            ## return the data from the thread
            self.profs, self.d = self.thread.returnData()


        ## initialize the rest of the window attributes, layout managers, etc

        ## handle the attribute of the main window
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

        self.brand = QLabel('SHARPpy Beta')
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

    def __archiveProf(self):
        """
        Get the archive sounding based on the user's selections.
        """
        ## construct the URL
        arch_file = open(self.link, 'r')

        ## read in the file
        data = np.array(arch_file.read().split('\n'))
        ## take care of possible whitespace issues
        for i in range(len(data)):
            data[i] = data[i].strip()
        arch_file.close()

        ## necessary index points
        title_idx = np.where( data == '%TITLE%')[0][0]
        start_idx = np.where( data == '%RAW%' )[0] + 1
        finish_idx = np.where( data == '%END%')[0]

        ## create the plot title
        plot_title = data[title_idx + 1].upper() + ' (User Selected)'

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])
        sound_data = StringIO( full_data )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, delimiter=',', comments="%", unpack=True )

        ## construct the Profile object
        prof = profile.create_profile( profile='convective', pres=p, hght=h, tmpc=T, dwpc=Td,
                                wdir=wdir, wspd=wspd, location=self.loc)
        return prof, plot_title

    def __observedProf(self):
        """
        Get the observed sounding based on the user's selections
        """
        ## if the profile is the latest, pull the latest profile
        if self.prof_time == "Latest":
            timestr = self.prof_time.upper()
        ## otherwise, convert the menu string to the URL format
        else:
            timestr = self.prof_time[2:4] + self.prof_time[5:7] + self.prof_time[8:10] + self.prof_time[11:-1]
            timestr += "_OBS"
        ## construct the URL
        url = urllib.urlopen('http://www.spc.noaa.gov/exper/soundings/' + timestr + '/' + self.loc.upper() + '.txt')
        ## read in the file
        data = np.array(url.read().split('\n'))
        ## necessary index points
        title_idx = np.where( data == '%TITLE%')[0][0]
        start_idx = np.where( data == '%RAW%' )[0] + 1
        finish_idx = np.where( data == '%END%')[0]

        ## create the plot title
        plot_title = data[title_idx + 1] + ' (Observed)'

        ## put it all together for StringIO
        full_data = '\n'.join(data[start_idx : finish_idx][:])
        sound_data = StringIO( full_data )

        ## read the data into arrays
        p, h, T, Td, wdir, wspd = np.genfromtxt( sound_data, delimiter=',', comments="%", unpack=True )

        ## construct the Profile object
        prof = profile.create_profile( profile='convective', pres=p, hght=h, tmpc=T, dwpc=Td,
                                wdir=wdir, wspd=wspd, location=self.loc)
        return prof, plot_title

    @Slot()
    def progress_bar(self):
        value = self.progressDialog.value()
        self.progressDialog.setValue(value + 1)
        self.progressDialog.setLabelText("Profile " + str(value + 1) + "/" + str(self.progressDialog.maximum()))

    def saveimage(self):
        fileName, result = QFileDialog.getSaveFileName(self, "Save Image", '/home')
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
        if self.model != "Observed" and self.model != "Archive":
            self.plot_title = self.loc + ' ' + datetime.strftime(self.d.dates[self.prof_idx[self.current_idx]], "%Y%m%d/%H%M") \
                + "  (" + self.run + "  " + self.model + ")"

        if self.model == "SREF":
            self.prof = self.profs[self.current_idx][0]
            self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_idx][:], dgz=self.dgz)
        else:
            self.prof = self.profs[self.current_idx]
            self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                                   dgz=self.dgz)

        ## initialize the non-swappable insets
        self.speed_vs_height = plotSpeed( self.prof )
        self.inferred_temp_advection = plotAdvection(self.prof)
        self.hodo = plotHodo(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof, parent=self)

        self.storm_slinky = plotSlinky(self.prof)
        self.thetae_vs_pressure = plotGeneric(self.prof.thetae[self.prof.pres > 500.],
                                self.prof.pres[self.prof.pres > 500.], xticks=np.arange(220,360,10),
                                 yticks=np.arange(500, 1000, 100), title="ThetaE v.\nPres" )

        self.srwinds_vs_height = plotWinds(self.prof)
        self.watch_type = plotWatch(self.prof)

        self.convective = plotText(self.prof)
        self.kinematic = plotKinematics(self.prof)

        self.makeInsets()

    def makeInsets(self):
        """
        Create the swappable insets
        :return:
        """
        SARS = plotAnalogues(self.prof)
        stp = plotSTP(self.prof)
        winter = plotWinter(self.prof)
        fire = plotFire(self.prof)
        ship = plotSHIP(self.prof)
        stpef = plotSTPEF(self.prof)
        vrot = plotVROT(self.prof)

        self.insets["SARS"] = SARS
        self.insets["STP STATS"] = stp
        self.insets["WINTER"] = winter
        self.insets["FIRE"] = fire
        self.insets["SHIP"] = ship
        self.insets["COND STP"] = stpef
        self.insets["VROT"] = vrot

    def updateProfs(self):
        #self.sound.setProf(self.profs[self.current_idx])
        if self.model != "Observed" and self.model != "Archive":
            self.plot_title = self.loc + ' ' + datetime.strftime(self.d.dates[self.prof_idx[self.current_idx]], "%Y%m%d/%H%M") \
                + "  (" + self.run + "  " + self.model + ")"

        if self.model == "SREF":
            self.prof = self.profs[self.current_idx][0]
            self.sound.setProf(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_idx][:], dgz=self.gdz)
        else:
            self.prof = self.profs[self.current_idx]
            self.sound.setProf(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand, dgz=self.dgz)

        self.storm_slinky.setProf(self.prof)
        self.inferred_temp_advection.setProf(self.prof)
        self.speed_vs_height.setProf(self.prof)
        self.srwinds_vs_height.setProf(self.prof)
        self.thetae_vs_pressure.setProf(self.prof.thetae[self.prof.pres > 500.],
                                self.prof.pres[self.prof.pres > 500.], xticks=np.arange(220,360,10),
                                 yticks=np.arange(500, 1000, 100), title="ThetaE v.\nPres" )
        self.watch_type.setProf(self.prof)
        self.convective.setProf(self.prof)
        self.kinematic.setProf(self.prof)
        self.hodo.setProf(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof, parent=self)

        for inset in self.insets.keys():
            self.insets[inset].setProf(self.prof)


    def paintEvent(self, e):
        """
        The paint event will handle the placing of widgets in their
        appropriate layout managers and places.
        :param e:
        :return:
        """
        if self.changeflag:
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
            self.grid3.addWidget(self.insets[self.left_inset], 0, 2)
            self.left_inset_ob = self.insets[self.left_inset]

            # Set Right Inset
            self.grid3.addWidget(self.insets[self.right_inset], 0, 3)
            self.right_inset_ob = self.insets[self.right_inset]

            ## do a check for setting the dendretic growth zone
            if self.left_inset == "WINTER" or self.right_inset == "WINTER":
                self.dgz = True


            self.grid.addWidget(self.sound, 0, 0, 3, 1)
            self.grid.addWidget(self.text, 3, 0, 1, 2)
            self.changeflag = False

    def keyPressEvent(self, e):
        key = e.key()
        length = len(self.profs)
        if key == Qt.Key_Right:
            if self.current_idx != length - 1:
                self.current_idx += 1
            else:
                self.current_idx = 0
            self.changeflag = True
            self.updateProfs()
            return

        if key == Qt.Key_Left:
            if self.current_idx != 0:
                self.current_idx -= 1
            elif self.current_idx == 0:
                self.current_idx = length -1
            self.changeflag = True
            self.updateProfs()
            return

        if e.matches(QKeySequence.Save):
            # Save an image
            self.saveimage()
            return

    def makeInsetMenu(self):
        # This will make the menu of the available insets.
        self.popupmenu=QMenu("Inset Menu")
        self.menu_ag = QActionGroup(self, exclusive=True)

        for i in xrange(len(self.avaliable_insets)):
            inset_action = QAction(self)
            inset_action.setText(self.avaliable_insets[i])
            inset_action.setCheckable(True)
            inset_action.triggered.connect(self.swapInset)
            a = self.menu_ag.addAction(inset_action)
            self.popupmenu.addAction(a)

    def showCursorMenu(self, pos):

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

            self.left_inset = a.text()
            self.left_inset_ob.deleteLater()


        elif self.inset_to_swap == "RIGHT":
            if self.right_inset == "WINTER" and self.dgz:
                self.sound.setDGZ(False)
                self.dgz = False

            self.right_inset = a.text()
            self.right_inset_ob.deleteLater()

        self.makeInsets()
        self.setFocus()
        self.changeflag=True
        self.update()