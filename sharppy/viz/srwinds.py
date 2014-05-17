import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundWinds', 'plotWinds']

class backgroundWinds(QtGui.QFrame):
    '''
    Handles the plotting of the frame boarders and ticks.
    '''
    def __init__(self):
        super(backgroundWinds, self).__init__()
        self.initUI()


    def initUI(self):
        ## initialize plot window variables,
        ## such as width, height, padding, and
        ## min/max axes variables
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## minimum/maximum height (km) and wind values.
        ## used in converting to pixel units
        self.hmax = 16.; self.hmin = 0.
        self.smax = 70.; self.smin = 0.
        self.label_font = QtGui.QFont('Helvetica', 7)

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized.
        '''
        self.initUI()
    
    def paintEvent(self, e):
        '''
        Handles the paint event. This paints the frame background.
        '''
        ## initialize a QPainter object for drawing
        qp = QtGui.QPainter()
        qp.begin(self)
        ## draw the background frame
        self.draw_frame(qp)
        ## draw the ticks for the plot.
        ## height is in km.
        for h in [2,4,6,8,10,12,14]:
            self.draw_height(h, qp)
        for s in range(0,100,10):
            self.draw_speed(s, qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draws the background frame.
        ------
        qp: QtGui.QPainter object
        '''
        ## initialize a new pen with white color, thickness of 2, solid line.
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        qp.drawText(15, 5, 45, 35,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter,
            'SR Wind\nv.\nHeight')
        ## draw the frame borders
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        zero = self.speed_to_pix(20.)
        qp.drawLine( zero, self.bry, zero, self.tly)
        lower = self.hgt_to_pix(8.)
        upper = self.hgt_to_pix(16.)
        classic1 = self.speed_to_pix(45.)
        classic2 = self.speed_to_pix(70.)
        pen = QtGui.QPen(QtGui.QColor("#B1019A"), 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        qp.drawLine( classic1, lower, classic1, upper )
        qp.drawLine( classic2, lower, classic2, upper )
        qp.drawText(classic1-5, 2, 50, 50,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter,
            'Classic\nSupercell')
        ## draw the plot description text

    def draw_height(self, h, qp):
        '''
        Draw background height ticks in km.
        ---------
        h: height in km
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with color white, thickness 1, solid line
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert the height value to pixel coordinates
        y1 = self.hgt_to_pix(h)
        ## length of tick to be drawn
        offset = 5
        ## draw the tick and then label the tick with the value
        qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
        qp.drawLine(self.brx+self.rpad-offset, y1,
            self.brx+self.rpad, y1)
        qp.drawText(0, y1-20, 20, 40,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
            str(int(h)))

    def draw_speed(self, s, qp):
        '''
        Draw background speed ticks.
        --------
        s: windpeed
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with white color, thickness 1, solid line
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert wind speed values to pixel values
        x1 = self.speed_to_pix(s)
        ## length of tick to be drawn
        offset = 5
        qp.drawLine(x1, 0, x1, 0+offset)
        qp.drawLine(x1, self.bry+self.tpad-offset,
            x1, self.bry+self.rpad)

    def hgt_to_pix(self, h):
        '''
        Function to convert a height value (km) to a Y pixel.
        '''
        scl1 = self.hmax - self.hmin
        scl2 = self.hmin + h
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def speed_to_pix(self, s):
        '''
        Function to convert a wind speed value to a X pixel.
        '''
        scl1 = self.smax - self.smin
        scl2 = self.smax - s
        return self.bry - (scl2 / scl1) * (self.bry - self.rpad)

class plotWinds(backgroundWinds):
    def __init__(self, prof):
        super(plotWinds, self).__init__()
        ## make the data accessable to the functions
        self.prof = prof
        self.u = prof.u; self.v = prof.v
        ## calculate the storm relative wind from the bunkers motion function
        self.srwind = prof.srwind
        ## get only the right mover u and v components
        self.sru = self.u - self.srwind[0]
        self.srv = self.v - self.srwind[1]

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotWinds, self).resizeEvent(e)
    
    def paintEvent(self, e):
        '''
        Handles painting the plot data.
        '''
        super(plotWinds, self).paintEvent(e)
        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self)
        ## draw the wind profile
        self.draw_profile(qp)
        qp.end()

    def draw_profile(self, qp):
        '''
        Draws the storm relative wind profile.
        --------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen with a red color, thickness of 2, solid line
        pen = QtGui.QPen(QtGui.QColor("#FF0000"), 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        ## if there are missing values, get the mask
        try:
            mask = np.maximum(self.sru.mask, self.srv.mask)
            sru = self.sru[~mask]
            srv = self.srv[~mask]
            hgt = self.prof.hght[~mask]
        ## otherwise the data is fine
        except:
            sru = self.sru
            srv = self.srv
            hgt = self.prof.hgtht
        ## loop through the vertical profile.
        ## we go through length - 1 because we index i and i+1
        for i in range( hgt.shape[0] - 1 ):
                ## get the height and winds at two consecutive heights
                ## don't forget to convert the height from meters to
                ## kilometers; divide by 1000
                hgt1 = hgt[i] / 1000; hgt2 = hgt[i+1] / 1000
                sru1 = sru[i]; sru2 = sru[i+1]
                srv1 = srv[i]; srv2 = srv[i+1]
                ## calculate the storm relative wind speed
                spd1 = np.sqrt( sru1**2 + srv1**2 )
                spd2 = np.sqrt( sru2**2 + srv2**2 )
                ## convert the wind speeds to x pixels
                x1 = self.speed_to_pix( spd1 ); x2 = self.speed_to_pix(spd2)
                ## convert the height values to y pixels
                y1 = self.hgt_to_pix(hgt1); y2 = self.hgt_to_pix(hgt2)
                ## draw a line between the two points
                qp.setPen(pen)
                qp.drawLine(x1, y1, x2, y2)


