__author__ = 'keltonhalbert'

from sharppy.viz import plotSkewT, plotHodo, plotText, plotAnalogues
from sharppy.viz import plotThetae, plotWinds, plotSpeed, plotKinematics
from sharppy.viz import plotSlinky, plotWatch, plotAdvection, plotSTP
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
import datetime as date
from subprocess import call
from StringIO import StringIO
import sharppy.sharptab.profile as profile
import urllib
import numpy as np

class SkewApp(QFrame):
    """
    Create a skewT window app
    """

    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.prof_time = kwargs.get("prof_time")
        self.run = kwargs.get("run", None)
        self.loc = kwargs.get("location")
        self.create_window()


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


    def create_window(self):
        prof, plot_title = self.__observedProf()

        ## create an empty widget window
        self.skewWindow = QWidget()
        self.skewWindow.setGeometry(0, 0, 1180, 800)

        ## window title
        title = 'SHARPpy: Sounding and Hodograph Analysis and Research Program '
        title += 'in Python'
        self.skewWindow.setWindowTitle(title)
        self.skewWindow.setStyleSheet("QWidget {background-color: rgb(0, 0, 0);}")

        ## set the layout as a grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(2)
        self.skewWindow.setLayout(grid)

        ## set the brand and place the sounding in the window
        sound = plotSkewT(prof, pcl=prof.mupcl, title=plot_title)
        sound.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(sound, 0, 0, 3, 1)

        # Handle the Upper Right
        urparent = QFrame()
        urparent_grid = QGridLayout()
        urparent_grid.setContentsMargins(0, 0, 0, 0)
        urparent.setLayout(urparent_grid)
        ur = QFrame()
        ur.setStyleSheet("QFrame {"
                         "  background-color: rgb(0, 0, 0);"
                         "  border-width: 0px;"
                         "  border-style: solid;"
                         "  border-color: rgb(255, 255, 255);"
                         "  margin: 0px;}")

        ## set the "brand" name
        brand = QLabel('HOOT - Oklahoma Weather Lab')
        brand.setAlignment(Qt.AlignRight)
        brand.setStyleSheet("QFrame {"
                            "  background-color: rgb(0, 0, 0);"
                            "  text-align: right;"
                            "  font-size: 11px;"
                            "  color: #FFFFFF;}")

        ## create a grid to put the stuff in
        grid2 = QGridLayout()
        grid2.setHorizontalSpacing(0)
        grid2.setVerticalSpacing(0)
        grid2.setContentsMargins(0, 0, 0, 0)
        ur.setLayout(grid2)

        ## construct the data plots
        speed_vs_height = plotSpeed( prof )
        speed_vs_height.setObjectName("svh")
        inferred_temp_advection = plotAdvection(prof)
        hodo = plotHodo(prof.hght, prof.u, prof.v, prof=prof, centered=prof.mean_lcl_el)
        storm_slinky = plotSlinky(prof)
        thetae_vs_pressure = plotThetae(prof)
        srwinds_vs_height = plotWinds(prof)
        watch_type = plotWatch(prof)

        ## add them to the grid
        grid2.addWidget(speed_vs_height, 0, 0, 11, 3)
        grid2.addWidget(inferred_temp_advection, 0, 3, 11, 2)
        grid2.addWidget(hodo, 0, 5, 8, 24)
        grid2.addWidget(storm_slinky, 8, 5, 3, 6)
        grid2.addWidget(thetae_vs_pressure, 8, 11, 3, 6)
        grid2.addWidget(srwinds_vs_height, 8, 17, 3, 6)
        grid2.addWidget(watch_type, 8, 23, 3, 6)
        ## add the brand and upper right window to the parent grid
        urparent_grid.addWidget(brand, 0, 0, 1, 0)
        urparent_grid.addWidget(ur, 1, 0, 50, 0)
        ## add the parent upper right to the main grid
        grid.addWidget(urparent, 0, 1, 3, 1)

        # Handle the Text Areas
        text = QFrame()
        text.setStyleSheet("QWidget {"
                           "  background-color: rgb(0, 0, 0);"
                           "  border-width: 2px;"
                           "  border-style: solid;"
                           "  border-color: #3399CC;}")

        ## create the layout
        grid3 = QGridLayout()
        grid3.setHorizontalSpacing(0)
        grid3.setContentsMargins(0, 0, 0, 0)
        text.setLayout(grid3)

        ## construct the plot objects
        convective = plotText(prof)
        kinematic = plotKinematics(prof)
        SARS = plotAnalogues(prof)
        stp = plotSTP(prof)

        ## add them to the text grid
        grid3.addWidget(convective, 0, 0)
        grid3.addWidget(kinematic, 0, 1)
        grid3.addWidget(SARS, 0, 2)
        grid3.addWidget(stp, 0, 3)

        ## add the text grid to the main grid
        grid.addWidget(text, 3, 0, 1, 2)

        return self.skewWindow