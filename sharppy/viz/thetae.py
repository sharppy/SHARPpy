import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundThetae', 'plotThetae']

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

class backgroundThetae(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundThetae, self).__init__()
        self.initUI()


    def initUI(self):
        ## window configuration settings,
        ## sich as padding, width, height, and
        ## min/max plot axes
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## what are the minimum/maximum values expected
        ## for the data? This is used when converting
        ## to pixel coordinates.
        self.pmax = 1025.; self.pmin = 400.
        self.tmax = 360.; self.tmin = 300.
        self.label_font = QtGui.QFont('Helvetica', 7)
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        Handles painting the frame.
        '''
        ## initialize a painter object and draw the frame
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        self.draw_frame(qp)
        ## draw the isobar ticks and the theta-e ticks
        for p in [1000, 900, 800, 700, 600, 500]:
            self.draw_isobar(p, qp)
        for t in np.arange( 200, 400, 10):
            self.draw_thetae(t, qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the borders in white
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)
        qp.setFont(self.label_font)
        ## draw the plot name on the background
        qp.drawText(35, 15, 50, 50,
                    QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter,
                    'Theta-E\nv.\nPres')

    def draw_isobar(self, p, qp):
        '''
        Draw background isobars.
        
        ---------
        p: pressure in hPa or mb
        qp: QtGui.QPainter object
        
        '''
        ## set a new pen with a white color and solid line of thickness 1
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert the pressure to pixel coordinates
        y1 = self.pres_to_pix(p)
        ## length of line to draw
        offset = 5
        ## draw the isobar line and text
        qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
        qp.drawLine(self.brx+self.rpad-offset, y1,
                self.brx+self.rpad, y1)
        qp.drawText(0, y1-20, 20, 40,
                QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
                str(int(p)))

    def draw_thetae(self, t, qp):
        '''
        Draw background Theta-E.
        ---------
        t: Theta-E in degrees Kelvin
        qp: QtGui.QPainter object
        
        '''
        ## set a new pen with a white color, thickness one, solid line
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert theta-E to pixel values
        x1 = self.theta_to_pix(t)
        ## length of tick to draw
        offset = 5
        ## draw the tick and label it with a value
        qp.drawLine(x1, 0, x1, 0+offset)
        qp.drawLine(x1, self.bry+self.tpad-offset,
            x1, self.bry+self.rpad)
        qp.drawText(x1+10, self.bry-20, 20, 20,
            QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, str(int(t)))

    def pres_to_pix(self, p):
        '''
        Function to convert a pressure value (hPa) to a Y pixel.
        '''
        scl1 = self.pmax - self.pmin
        scl2 = self.pmax - p
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def theta_to_pix(self, t):
        '''
        Function to convert a Theta-E value (K) to a X pixel.
        '''
        scl1 = self.tmax - self.tmin
        scl2 = self.tmax - t
        return self.bry - (scl2 / scl1) * (self.bry - self.rpad)

class plotThetae(backgroundThetae):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self, prof):
        super(plotThetae, self).__init__()
        ## make variables inheritable
        self.prof = prof
        self.thetae = prof.thetae
        self.pres = prof.pres

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotThetae, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotThetae, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the theta-e profile
        self.draw_profile(qp)
        ## end the painter
        qp.end()

    def draw_profile(self, qp):
        '''
        Draw the Theta-E v. Pres profile.
        --------
        qp: QtGui.QPainter object
        '''
        pen = QtGui.QPen(QtGui.QColor("#FF0000"), 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        mask1 = self.thetae.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        pres = self.pres[~mask]
        thetae = self.thetae[~mask]
        for i in range( pres.shape[0] ):
            ## we really only want to plot the data in the lowest 500mb
            if pres[i] > 400:
                ## get two pressure, temperature, and dewpoint values
                p1 = pres[i]; p2 = pres[i+1]
                ## get two theta-e values from the above sounding profile data
                thte1 = thetae[i]; thte2 = thetae[i+1]
                ## convert the theta-e values to x pixel coordinates
                ## and the pressure values to y pixel coordinates
                x1 = self.theta_to_pix(thte1); x2 = self.theta_to_pix(thte2)
                y1 = self.pres_to_pix(p1); y2 = self.pres_to_pix(p2)
                ## set the pen and draw a line between the two points
                qp.setPen(pen)
                qp.drawLine(x1, y1, x2, y2)


