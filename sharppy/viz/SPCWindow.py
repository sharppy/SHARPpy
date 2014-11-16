__author__ = 'keltonhalbert, wblumberg'

from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics, plotGeneric
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP, plotWinter
from sharppy.viz import plotSHIP
from PySide.QtCore import *
from PySide.QtGui import *
from sharppy.io.buf_decoder import BufkitFile
from StringIO import StringIO
import sharppy.sharptab.profile as profile
from datetime import datetime
import urllib
import numpy as np
from multiprocessing import Pool

class Thread(QThread):
    def __init__(self, **kwargs):
        super(Thread, self).__init__()
        self.model = kwargs.get("model")
        self.runtime = kwargs.get("run")
        self.loc = kwargs.get("loc")
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
            for i in range(len(d.wdir[0]))[:]:
                profs = []
                for j in range(len(d.wdir)):
                    print "MAKING PROFILE OBJECT: " + datetime.strftime(d.dates[i], '%Y%m%d/%H%M')
                    if j == 0:
                        profs.append(profile.create_profile(profile='convective', omeg = d.omeg[j][i], hght = d.hght[j][i],
                        tmpc = d.tmpc[j][i], dwpc = d.dwpc[j][i], pres = d.pres[j][i], wspd=d.wspd[j][i], wdir=d.wdir[j][i]))
                    else:
                        profs.append(profile.create_profile(profile='default', omeg = d.omeg[j][i], hght = d.hght[j][i],
                        tmpc = d.tmpc[j][i], dwpc = d.dwpc[j][i], pres = d.pres[j][i], wspd=d.wspd[j][i], wdir=d.wdir[j][i]))
                self.profs.append(profs)
        else:
            for i in range(len(d.wdir[0]))[:]:
                print "MAKING PROFILE OBJECT: " + datetime.strftime(d.dates[i], '%Y%m%d/%H%M')
                self.profs.append(profile.create_profile(profile='convective', omeg = d.omeg[0][i], hght = d.hght[0][i],
                    tmpc = d.tmpc[0][i], dwpc = d.dwpc[0][i], pres = d.pres[0][i], wspd=d.wspd[0][i], wdir=d.wdir[0][i]))


    def run(self):
        self.__modelProf()


class SkewApp(QWidget):
    """
    Create a skewT window app
    """

    def __init__(self, **kwargs):
        super(SkewApp, self).__init__()
        self.model = kwargs.get("model")
        self.prof_time = kwargs.get("prof_time", None)
        self.run = kwargs.get("run")
        self.loc = kwargs.get("location")
        self.link = kwargs.get("path", None)
        self.changeflag = True
        self.swap_inset = False
        self.d = None
        self.current_index = 0
        self.inset = "S"
        self.profs = []
        if self.model == "Observed":
            self.prof, self.plot_title = self.__observedProf()
            self.profs.append(self.prof)
        elif self.model == "Archive":
            self.prof, self.plot_title = self.__archiveProf()
            self.profs.append(self.prof)            
        else:
            self.thread = Thread(model=self.model, loc=self.loc, run=self.run)
            self.thread.start()
            while not self.thread.isFinished():
                QCoreApplication.processEvents()
            self.profs, self.d = self.thread.returnData()
        self.setGeometry(0, 0, 1180, 800)
        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        brand = 'SHARPpy Beta'
        self.setWindowTitle(title)
        self.setStyleSheet("QWidget {background-color: rgb(0, 0, 0);}")
        self.grid = QGridLayout()
        self.grid.setContentsMargins(1,1,1,1)
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(2)
        self.setLayout(self.grid)

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
        self.grid2 = QGridLayout()
        self.grid2.setHorizontalSpacing(0)
        self.grid2.setVerticalSpacing(0)
        self.grid2.setContentsMargins(0, 0, 0, 0)
        self.ur.setLayout(self.grid2)
        self.urparent_grid.addWidget(self.brand, 0, 0, 1, 0)
        self.urparent_grid.addWidget(self.ur, 1, 0, 50, 0)
        self.grid.addWidget(self.urparent, 0, 1, 3, 1)

         # Handle the Text Areas
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
        self.setUpdatesEnabled(True)

        self.menuBar()
        self.initData()


    def menuBar(self):

        self.bar = QMenuBar()
        self.filemenu = self.bar.addMenu("File")
        selectdata = QAction("Select Data...", self)
        saveimg = QAction("Save as image...", self)
        exit = QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"))
        self.filemenu.addAction(exit)
        exit.triggered.connect(self.exitApp)  
        pref = QAction("Preferences", self)
        self.filemenu.addAction(selectdata)
        self.filemenu.addAction(saveimg)
        saveimg.triggered.connect(self.saveimage)
        self.filemenu.addAction(pref)
        self.filemenu.addSeparator()
        self.insetsmenu = self.bar.addMenu("Insets")
        sars = QAction("SARS", self)
        stpstats = QAction("STP Stats", self)
        winter = QAction("Winter", self)
        fire = QAction("Fire", self)
        vrot = QAction("VROT", self)
        self.insetsmenu.addAction(sars)
        self.insetsmenu.addAction(stpstats)
        self.insetsmenu.addAction(winter)
        self.insetsmenu.addAction(fire)
        self.insetsmenu.addAction(vrot)
        self.insetsmenu.addSeparator()
        self.insetsmenu.addAction(sars)
        self.insetsmenu.addAction(stpstats)
        self.insetsmenu.addAction(winter)
        self.insetsmenu.addAction(fire)
        self.insetsmenu.addAction(vrot)
        self.cursormenu = self.bar.addMenu("Cursor")

        storm_motion = QAction("Storm Motion", self)
        boundary = QAction("Boundary Motion", self)
        strm_mot = self.cursormenu.addAction(storm_motion)
        bndy_mot = self.cursormenu.addAction(boundary)
        self.helpmenu = self.bar.addMenu("Help")
        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)
        self.helpmenu.addAction(about)

    def saveimage(self):
        fileName = QFileDialog.getSaveFileName(self, "Save Image", '/home')
        pixmap = QPixmap.grabWidget(self)
        pixmap.save(fileName[0], 'PNG', 100)

    def aboutbox(self):

        msgBox = QMessageBox()
        msgBox.setText("SHARPpy\nSounding and Hodograph Research and Analysis Program for " +
                       "Python\n\n(C) 2014 by Kelton Halbert and Greg Blumberg")
        msgBox.exec_()

    def __archiveProf(self):
        """
        Get the archive sounding based on the user's selections
        """
        ## construct the URL
        print self.link
        arch_file = open(self.link, 'r')
        ## read in the file
        data = np.array(arch_file.read().split('\n'))
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



    def clearWidgets(self):
        self.sound.deleteLater()

        self.speed_vs_height.deleteLater()
        self.inferred_temp_advection.deleteLater()
        self.hodo.deleteLater()
        self.storm_slinky.deleteLater()
        self.thetae_vs_pressure.deleteLater()
        self.srwinds_vs_height.deleteLater()
        self.watch_type.deleteLater()
        self.convective.deleteLater()
        self.kinematic.deleteLater()

        if self.inset == "S":
            self.SARS.deleteLater()
        self.stp.deleteLater()
        if self.inset == "W":
            self.winter.deleteLater()
        if self.inset == "F":
            self.fire.deleteLater()
        if self.inset == "H":
            self.ship.deleteLater()

    def exitApp(self):
        self.close()

    def initData(self):

        if self.model != "Observed" and self.model != "Archive":
            self.plot_title = self.loc + ' ' + datetime.strftime(self.d.dates[self.current_index], '%Y%m%d/%H%M') \
                + "  (" + self.run + "  " + self.model + ")"

        if self.model == "SREF":
            self.prof = self.profs[self.current_index][0]
            self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_index][:])
        else:
            self.prof = self.profs[self.current_index]
            self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand)

        self.speed_vs_height = plotSpeed( self.prof )
        self.speed_vs_height.setObjectName("svh")
        self.inferred_temp_advection = plotAdvection(self.prof)
        self.hodo = plotHodo(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof)

        self.storm_slinky = plotSlinky(self.prof)
        self.thetae_vs_pressure = plotGeneric(self.prof.thetae[self.prof.pres > 500.],
                                self.prof.pres[self.prof.pres > 500.], xticks=np.arange(220,360,10),
                                 yticks=np.arange(500, 1000, 100), title="ThetaE v.\nPres" )

        self.srwinds_vs_height = plotWinds(self.prof)
        self.watch_type = plotWatch(self.prof)

        self.convective = plotText(self.prof)
        self.kinematic = plotKinematics(self.prof)
        self.SARS = plotAnalogues(self.prof)
        self.stp = plotSTP(self.prof)
        self.winter = plotWinter(self.prof)
        self.ship = plotSHIP(self.prof)

    def paintEvent(self, e):
        if self.changeflag:
            self.grid2.addWidget(self.speed_vs_height, 0, 0, 11, 3)
            self.grid2.addWidget(self.inferred_temp_advection, 0, 3, 11, 2)
            self.grid2.addWidget(self.hodo, 0, 5, 8, 24)
            self.grid2.addWidget(self.storm_slinky, 8, 5, 3, 6)
            self.grid2.addWidget(self.thetae_vs_pressure, 8, 11, 3, 6)
            self.grid2.addWidget(self.srwinds_vs_height, 8, 17, 3, 6)
            self.grid2.addWidget(self.watch_type, 8, 23, 3, 6)


            self.grid3.addWidget(self.convective, 0, 0)
            self.grid3.addWidget(self.kinematic, 0, 1)
            if self.inset == "S":
                self.grid3.addWidget(self.SARS, 0, 2)
            elif self.inset == "W":
                self.grid3.addWidget(self.winter, 0, 2)
                if self.model == "SREF":
                    self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_index][:], dgz=True)
                else:
                    self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand, dgz=True)
            elif self.inset == "H":
                self.grid3.addWidget(self.ship, 0, 2)

            self.grid3.addWidget(self.stp, 0, 3)
            self.grid.addWidget(self.sound, 0, 0, 3, 1)
            self.grid.addWidget(self.text, 3, 0, 1, 2)
            self.changeflag = False

        if self.swap_inset and self.inset == "S":
            self.inset = "W"
            self.SARS.deleteLater()
            self.winter = plotWinter(self.prof)
            self.grid3.addWidget(self.winter, 0, 2)
            self.sound.deleteLater()
            if self.model == "SREF":
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_index][:], dgz=True)
            else:
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand, dgz=True)
            self.grid.addWidget(self.sound, 0, 0, 3, 1)            
            self.swap_inset = False

        elif self.swap_inset and self.inset == "W":
            self.inset = "H"
            self.winter.deleteLater()
            self.ship = plotSHIP(self.prof)
            self.grid3.addWidget(self.ship, 0, 2)
            self.sound.deleteLater()
            if self.model == "SREF":
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_index][:], dgz=False)
            else:
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand, dgz=False)
            self.grid.addWidget(self.sound, 0, 0, 3, 1)
            self.swap_inset = False

        elif self.swap_inset and self.inset == "H":
            self.inset = "S"
            self.ship.deleteLater()
            self.SARS = plotAnalogues(self.prof)
            self.grid3.addWidget(self.SARS, 0, 2)
            self.sound.deleteLater()
            if self.model == "SREF":
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand,
                               proflist=self.profs[self.current_index][:], dgz=False)
            else:
                self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=self.plot_title, brand=self.brand, dgz=False)
            self.grid.addWidget(self.sound, 0, 0, 3, 1)               
            self.swap_inset = False        

    def keyPressEvent(self, e):
        key = e.key()
        length = len(self.profs)
        if key == Qt.Key_Right:
            if self.current_index != length - 1:
                self.current_index += 1
            else:
                self.current_index = 0
            self.changeflag = True
            self.clearWidgets()
            self.initData()
            self.update()

        if key == Qt.Key_Left:
            if self.current_index != 0:
                self.current_index -= 1
            elif self.current_index == 0:
                self.current_index = length -1
            self.changeflag = True
            self.clearWidgets()
            self.initData()
            self.update()

        if key == Qt.Key_S:
            self.swap_inset = True
            self.update()
