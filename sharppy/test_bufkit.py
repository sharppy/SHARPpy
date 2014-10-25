import sys
import numpy as np
import time as stime
from PySide import QtGui, QtCore
from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP
from sharppy.viz import plotWinter
#from sharppy.sounding import prof, plot_title
from sharppy.io.buf_decoder import BufkitFile
#from sharppy.sharptab.profile import Profile
import sharppy.sharptab.profile as profile
from datetime import datetime
from multiprocessing.pool import Pool

class MainProgram(QtGui.QMainWindow):

    def __init__(self, **kwargs):
        super(MainProgram, self).__init__()
        self.profs = kwargs.get('profs')
        self.station = kwargs.get('station')
        self.time = kwargs.get('time')
        self.model = kwargs.get('model')
        self.d = kwargs.get('d')
        self.current_index = 0
        self.changeflag = True
        self.swap_inset = False 
        self.inset = "S"

        self.setGeometry(0, 0, 1180, 800)
        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        brand = 'Oklahoma Weather Lab'
        self.setWindowTitle(title)
        self.setStyleSheet("QMainWindow {background-color: rgb(0, 0, 0);}")
        centralWidget = QtGui.QFrame()
        self.grid = QtGui.QGridLayout()
        self.grid.setHorizontalSpacing(0)
        self.grid.setVerticalSpacing(2)
        centralWidget.setLayout(self.grid)
        self.setCentralWidget(centralWidget)
        
        self.urparent = QtGui.QFrame()
        self.urparent_grid = QtGui.QGridLayout()
        self.urparent_grid.setContentsMargins(0, 0, 0, 0)
        self.urparent.setLayout(self.urparent_grid)
        self.ur = QtGui.QFrame()
        self.ur.setStyleSheet("QFrame {"
                         "  background-color: rgb(0, 0, 0);"
                         "  border-width: 0px;"
                         "  border-style: solid;"
                         "  border-color: rgb(255, 255, 255);"
                         "  margin: 0px;}")
        self.brand = QtGui.QLabel('HOOT - Oklahoma Weather Lab')
        self.brand.setAlignment(QtCore.Qt.AlignRight)
        self.brand.setStyleSheet("QFrame {"
                             "  background-color: rgb(0, 0, 0);"
                             "  text-align: right;"
                             "  font-size: 11px;"
                             "  color: #FFFFFF;}")
        self.grid2 = QtGui.QGridLayout()
        self.grid2.setHorizontalSpacing(0)
        self.grid2.setVerticalSpacing(0)
        self.grid2.setContentsMargins(0, 0, 0, 0)
        self.ur.setLayout(self.grid2)
        self.urparent_grid.addWidget(self.brand, 0, 0, 1, 0)
        self.urparent_grid.addWidget(self.ur, 1, 0, 50, 0)
        self.grid.addWidget(self.urparent, 0, 1, 3, 1)
         
         # Handle the Text Areas
        self.text = QtGui.QFrame()
        self.text.setStyleSheet("QWidget {"
                            "  background-color: rgb(0, 0, 0);"
                            "  border-width: 2px;"
                            "  border-style: solid;"
                            "  border-color: #3399CC;}")
        self.grid3 = QtGui.QGridLayout()
        self.grid3.setHorizontalSpacing(0)
        self.grid3.setContentsMargins(0, 0, 0, 0)
        self.text.setLayout(self.grid3)
        self.setUpdatesEnabled(True)

        self.initData()


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
        self.SARS.deleteLater()
        self.stp.deleteLater()
        self.winter.deleteLater()

    def initData(self):
        self.prof = self.profs[self.current_index]
        
        plot_title = self.station + ' ' + datetime.strftime(self.d.dates[self.current_index], '%Y%m%d/%H%M') + "  (" + self.time + "Z  " + self.model + ")"
        name = datetime.strftime(self.d.dates[self.current_index], '%Y%m%d.%H%M.') + self.time + self.model + '.' + self.station
        
        self.sound = plotSkewT(self.prof, pcl=self.prof.mupcl, title=plot_title, brand=self.brand)
        
        self.speed_vs_height = plotSpeed( self.prof )
        self.speed_vs_height.setObjectName("svh")
        self.inferred_temp_advection = plotAdvection(self.prof)
        self.hodo = plotHodo(self.prof.hght, self.prof.u, self.prof.v, prof=self.prof)
        
        self.storm_slinky = plotSlinky(self.prof)
        self.thetae_vs_pressure = plotThetae(self.prof)
        self.srwinds_vs_height = plotWinds(self.prof)
        self.watch_type = plotWatch(self.prof)
        
        self.convective = plotText(self.prof)
        self.kinematic = plotKinematics(self.prof)
        self.SARS = plotAnalogues(self.prof)
        self.stp = plotSTP(self.prof)
        self.winter = plotWinter(self.prof)

    def paintEvent(self, e):

        if self.changeflag:
            self.grid.addWidget(self.sound, 0, 0, 3, 1)
        
            self.grid2.addWidget(self.speed_vs_height, 0, 0, 11, 3)
            self.grid2.addWidget(self.inferred_temp_advection, 0, 3, 11, 2)
            self.grid2.addWidget(self.hodo, 0, 5, 8, 24)
            self.grid2.addWidget(self.storm_slinky, 8, 5, 3, 6)
            self.grid2.addWidget(self.thetae_vs_pressure, 8, 11, 3, 6)
            self.grid2.addWidget(self.srwinds_vs_height, 8, 17, 3, 6)
            self.grid2.addWidget(self.watch_type, 8, 23, 3, 6)
            
            
            self.grid3.addWidget(self.convective, 0, 0)
            self.grid3.addWidget(self.kinematic, 0, 1)
            self.grid3.addWidget(self.stp, 0, 3)
            self.grid.addWidget(self.text, 3, 0, 1, 2)
            self.changeflag = False
        else:

            self.grid.addWidget(self.sound, 0, 0, 3, 1)
        
            self.grid2.addWidget(self.speed_vs_height, 0, 0, 11, 3)
            self.grid2.addWidget(self.inferred_temp_advection, 0, 3, 11, 2)
            self.grid2.addWidget(self.hodo, 0, 5, 8, 24)
            self.grid2.addWidget(self.storm_slinky, 8, 5, 3, 6)
            self.grid2.addWidget(self.thetae_vs_pressure, 8, 11, 3, 6)
            self.grid2.addWidget(self.srwinds_vs_height, 8, 17, 3, 6)
            self.grid2.addWidget(self.watch_type, 8, 23, 3, 6)
            
            
            self.grid3.addWidget(self.convective, 0, 0)
            self.grid3.addWidget(self.kinematic, 0, 1)
            self.grid3.addWidget(self.stp, 0, 3)
            self.grid.addWidget(self.text, 3, 0, 1, 2)
            
        print self.swap_inset, self.inset
        if not self.swap_inset  and self.inset == "S":
            self.grid3.addWidget(self.SARS, 0, 2)
        elif not self.swap_inset and self.inset == "W":
            self.grid3.addWidget(self.winter, 0, 2)
        elif self.swap_inset and self.inset == "W":
            self.grid3.addWidget(self.SARS, 0, 2)
            self.inset = "S"
            self.swap_inset = False
        elif self.swap_inset and self.inset == "S":
            self.grid3.addWidget(self.winter, 0, 2)
            self.inset = "W"
            self.swap_inset = False

    def keyPressEvent(self, e):
        key = e.key()
        length = len(self.profs)
        if key == QtCore.Qt.Key_Right:
            if self.current_index != length - 1:
                self.current_index += 1
            else:
                self.current_index = 0
            self.changeflag = True
        #    self.clearWidgets()
        #    self.initData()
        #    self.update()

        if key == QtCore.Qt.Key_Left:
            if self.current_index != 0:
                self.current_index -= 1
            elif self.current_index == 0:
                self.current_index = length -1
            
            self.changeflag = True
        
        if key == QtCore.Qt.Key_S:
            self.swap_inset = True
            self.changeflag = False

        self.clearWidgets()
        self.initData()
        self.update()
        



station = sys.argv[3]
time = sys.argv[1]
model = sys.argv[2]
profs = []


if model == "GFS":
    d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/' + model + '/' + time + '/' + model.lower() + '3_' + station.lower() + '.buf')
#elif model == "NAM"
#    d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/' + model + '/' + time + '/' + model.lower() + '3_' + station.lower() + '.buf')
else:
    d = BufkitFile('ftp://ftp.meteo.psu.edu/pub/bufkit/' + model + '/' + time + '/' + model.lower() + '_' + station.lower() + '.buf')

for i in range(len(d.wdir[0]))[:]:
    print "MAKING PROFILE OBJECT: " + datetime.strftime(d.dates[i], '%Y%m%d/%H%M')
#    d.omeg[0][i] = d.omeg[0][i]*5
    profs.append(profile.create_profile(profile='convective', hght = d.hght[0][i], tmpc = d.tmpc[0][i], dwpc = d.dwpc[0][i], pres = d.pres[0][i], wspd=d.wspd[0][i], wdir=d.wdir[0][i], omeg=d.omeg[0][i]))
#    print d.omeg[0][i]
app = QtGui.QApplication(sys.argv)
mainWindow = MainProgram(profs=profs, station=station, time=time, model=model, d=d )
mainWindow.show()
app.exec_()
