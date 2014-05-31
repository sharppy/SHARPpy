import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundSpeed', 'plotSpeed']

class backgroundSpeed(QtGui.QFrame):
    '''
    Handles drawing the plot background.
    '''
    def __init__(self):
        super(backgroundSpeed, self).__init__()
        self.initUI()


    def initUI(self):
        ## initialize frame variables, such as length, width, and
        ## expected max/min values of data
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## set the max and min pressure expected, and convert it to log space
        self.pmax = 1050.; self.pmin = 100.
        self.log_pmax = np.log(self.pmax); self.log_pmin = np.log(self.pmin)
        ## set the max/min wind speed expected
        self.smax = 140.; self.smin = 0.
        self.label_font = QtGui.QFont('Helvetica', 7)
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        Handles painting the frame.
        '''
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the background frame
        self.draw_frame(qp)
        ## draw the vertical ticks for wind speed
        for s in range(0,140,20):
            self.draw_speed(s, qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draws the frame boarders.
        '''
        ## initialize a pen with white color, thickness 2, solid line
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)


    def draw_speed(self, s, qp):
        '''
        Draw background speed ticks.
        --------
        s: wind speed
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with an orange/brown color, thickness 1, dashed line
        pen = QtGui.QPen(QtGui.QColor("#9D5736"), 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert the speed value to pixel coordinates
        x1 = self.speed_to_pix(s)
        ## draw a dashed line of constant wind speed value
        qp.drawLine(x1, self.bry, x1, self.tly)
        if s > 0:
            pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            qp.drawText(x1-2, self.bry+10, 15, 10,
                QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft, tab.utils.INT2STR(s))

    def pres_to_pix(self, p):
        '''
        Function to convert a pressure value to a Y pixel.
        
        '''
        scl1 = self.log_pmax - self.log_pmin
        scl2 = self.log_pmax - np.log(p)
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def speed_to_pix(self, s):
        '''
        Function to convert a wind speed value to a X pixel.
        '''
        scl1 = self.smax - self.smin
        scl2 = self.smax - s
        return self.brx - (scl2 / scl1) * (self.brx - self.rpad)

class plotSpeed(backgroundSpeed):
    '''
    Handles plotting the data in the frame.
    '''
    def __init__(self, prof):
        super(plotSpeed, self).__init__()
        ## initialize values to be accessable to functions
        self.prof = prof
        self.u = prof.u; self.v = prof.v
        self.hght = prof.hght; self.pres = prof.pres

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotSpeed, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotSpeed, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Handles drawing the data on the frame.
        '''
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the wind speed profile
        self.draw_profile(qp)
        qp.end()

    def draw_profile(self, qp):
        '''
        Draw the Speed vs. Height profile.
        --------
        qp: QtGui.QPainter object
        '''
        ## give different colors for different height values.
        ## these are consistent with the hodograph colors.
        low_level_color = QtGui.QColor("#FF0000")
        mid_level_color = QtGui.QColor("#00FF00")
        upper_level_color = QtGui.QColor("#FFFF00")
        trop_level_color = QtGui.QColor("#00FFFF")
        ## initialize a pen starting with the low level color,
        ## thickness of 2, solid line.
        pen = QtGui.QPen(low_level_color, 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        ## if there are missing values, get the data mask
        try:
            mask = np.maximum(self.u.mask, self.v.mask)
            hgt = tab.interp.to_agl(self.prof, self.hght[~mask])
            pres = self.pres[~mask]
            u = self.u[~mask]
            v = self.v[~mask]
            ## calculate teh wind speed
            spd = np.sqrt( u**2 + v**2 )
        ## otherwise, the data is fine.
        except:
            hgt = tab.interp.to_agl(self.prof, self.hght)
            pres = self.pres
            u = self.u; v = self.v
            ## calculate the windspeed
            spd = np.sqrt( u**2 + v**2 )
        ## loop through the profile
        for i in range( pres.shape[0] ):
            ## get the important values from the profile
            hgt1 = hgt[i]
            p1 = pres[i]
            spd1 = spd[i]
            ## convert the speed to x pixel coordinates
            ## and convert the pressure in log space to a
            ## y pixel coordinate
            x1 = self.speed_to_pix(spd1)
            y1 = self.pres_to_pix(p1)
            ## now color code the different heights
            if hgt1 < 3000:
                pen = QtGui.QPen(low_level_color, 2)
            elif hgt1 < 6000:
                pen = QtGui.QPen(mid_level_color, 2)
            elif hgt1 < 9000:
                pen = QtGui.QPen(upper_level_color, 2)
            elif hgt1 < 12000:
                pen = QtGui.QPen(trop_level_color, 2)
            ## Draw a horizontal line with the length of the wind speed
            qp.setPen(pen)
            qp.drawLine(0, y1, x1, y1)



