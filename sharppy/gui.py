import sys
import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP
from sharppy.viz import plotGeneric
from sharppy.sharptab.constants import *
from sharppy.sounding import prof, plot_title


# Setup Application
app = QtGui.QApplication(sys.argv)
mainWindow = QtGui.QMainWindow()
x = 1180; y = 800
mainWindow.setGeometry(0, 0, x, y)
title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
title += 'in Python'
mainWindow.setWindowTitle(title)
mainWindow.setStyleSheet("QMainWindow {background-color: rgb(0, 0, 0);}")
centralWidget = QtWidgets.QFrame()
mainWindow.setCentralWidget(centralWidget)
grid = QtGui.QGridLayout()
grid.setHorizontalSpacing(0)
grid.setVerticalSpacing(2)
centralWidget.setLayout(grid)


# Handle the Upper Left
## plot the main sounding
#print prof.right_scp, prof.left_scp
brand = 'SHARPpy Beta'
sound = plotSkewT(prof, pcl=prof.mupcl, title=plot_title, brand=brand)
sound.setContentsMargins(0, 0, 0, 0)
grid.addWidget(sound, 0, 0, 3, 1)

# Handle the Upper Right
urparent = QtWidgets.QFrame()
urparent_grid = QtGui.QGridLayout()
urparent_grid.setContentsMargins(0, 0, 0, 0)
urparent.setLayout(urparent_grid)
ur = QtWidgets.QFrame()
ur.setStyleSheet("QFrame {"
                 "  background-color: rgb(0, 0, 0);"
                 "  border-width: 0px;"
                 "  border-style: solid;"
                 "  border-color: rgb(255, 255, 255);"
                 "  margin: 0px;}")
brand = QtGui.QLabel('SHARPpy Beta')
brand.setAlignment(QtCore.Qt.AlignRight)
brand.setStyleSheet("QFrame {"
                    "  background-color: rgb(0, 0, 0);"
                    "  text-align: right;"
                    "  font-size: 11px;"
                    "  color: #FFFFFF;}")
grid2 = QtGui.QGridLayout()
grid2.setHorizontalSpacing(0)
grid2.setVerticalSpacing(0)
grid2.setContentsMargins(0, 0, 0, 0)
ur.setLayout(grid2)

speed_vs_height = plotSpeed( prof )
speed_vs_height.setObjectName("svh")
inferred_temp_advection = plotAdvection(prof)
hodo = plotHodo(prof.hght, prof.u, prof.v, prof=prof, centered=prof.mean_lcl_el)
storm_slinky = plotSlinky(prof)
#thetae_vs_pressure = plotThetae(prof)
thetae_vs_pressure = plotGeneric(prof.thetae[prof.pres > 500.], prof.pres[prof.pres > 500.],
                                 xticks=np.arange(320,360,10), yticks=np.arange(500, 1000, 100) )
srwinds_vs_height = plotWinds(prof)
#srwinds_vs_height = plotGeneric(prof.srwind, prof.hght)
watch_type = plotWatch(prof)

grid2.addWidget(speed_vs_height, 0, 0, 11, 3)
grid2.addWidget(inferred_temp_advection, 0, 3, 11, 2)
grid2.addWidget(hodo, 0, 5, 8, 24)
grid2.addWidget(storm_slinky, 8, 5, 3, 6)
grid2.addWidget(thetae_vs_pressure, 8, 11, 3, 6)
grid2.addWidget(srwinds_vs_height, 8, 17, 3, 6)
grid2.addWidget(watch_type, 8, 23, 3, 6)
urparent_grid.addWidget(brand, 0, 0, 1, 0)
urparent_grid.addWidget(ur, 1, 0, 50, 0)
grid.addWidget(urparent, 0, 1, 3, 1)

# Handle the Text Areas
text = QtWidgets.QFrame()
text.setStyleSheet("QWidget {"
                   "  background-color: rgb(0, 0, 0);"
                   "  border-width: 2px;"
                   "  border-style: solid;"
                   "  border-color: #3399CC;}")
grid3 = QtGui.QGridLayout()
grid3.setHorizontalSpacing(0)
grid3.setContentsMargins(0, 0, 0, 0)
text.setLayout(grid3)
convective = plotText(prof)
#convective = QtWidgets.QFrame()
#kinematic = QtWidgets.QFrame()
kinematic = plotKinematics(prof)
SARS = plotAnalogues(prof)
stp = plotSTP(prof)
grid3.addWidget(convective, 0, 0)
grid3.addWidget(kinematic, 0, 1)
grid3.addWidget(SARS, 0, 2)
grid3.addWidget(stp, 0, 3)
grid.addWidget(text, 3, 0, 1, 2)
pixmap = QtGui.QPixmap.grabWidget(mainWindow)
pixmap.save('skewt.png', 'PNG', 100)
mainWindow.show()

app.exec_()
