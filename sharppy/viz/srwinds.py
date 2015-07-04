import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundWinds', 'plotWinds']

class backgroundWinds(QtGui.QFrame):
    '''
    Handles the plotting of the frame boarders and ticks.
    Draws the frame onto a QPixmap.
    '''
    def __init__(self):
        super(backgroundWinds, self).__init__()
        self.initUI()


    def initUI(self):
        '''
        Initializes the frame attributes and QPixmap.
        '''
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
        self.smax = 80.; self.smin = 0.
        ## do a DPI check for font sizing
        if self.physicalDpiX() > 75:
            fsize = 6
        else:
            fsize = 7
        self.label_font = QtGui.QFont('Helvetica', fsize)
        ## initialize the QPixmap
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized.
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        This paints the frame background onto the QPixmap.
        '''
        ## initialize a QPainter object for drawing
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the background frame
        self.draw_frame(qp)
        ## draw the ticks for the plot.
        ## height is in km.
        for h in [2,4,6,8,10,12,14]:
            self.draw_height(h, qp)
        for s in xrange(0,100,10):
            self.draw_speed(s, qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draws the background frame.
        
        Parameters
        ----------
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
        zero = self.speed_to_pix(15.)
        qp.drawLine( zero, self.bry, zero, self.tly)
        lower = self.hgt_to_pix(8.)
        upper = self.hgt_to_pix(16.)
        classic1 = self.speed_to_pix(40.)
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
        
        Parameters
        ----------
        h: height in km
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with color white, thickness 1, solid line
        pen = QtGui.QPen(QtGui.QColor(WHITE), 1, QtCore.Qt.SolidLine)
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
            tab.utils.INT2STR(h))

    def draw_speed(self, s, qp):
        '''
        Draw background speed ticks.
        
        Parameters
        ----------
        s: windpeed
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with white color, thickness 1, solid line
        pen = QtGui.QPen(QtGui.QColor(WHITE), 1, QtCore.Qt.SolidLine)
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
        
        Parameters
        ----------
        h: height in km
        
        '''
        scl1 = self.hmax - self.hmin
        scl2 = self.hmin + h
        return (self.bry - 2) - (scl2 / scl1) * (self.bry - self.tpad)

    def speed_to_pix(self, s):
        '''
        Function to convert a wind speed value to a X pixel.
        
        Parameters
        ----------
        s: speed in kts
        '''
        scl1 = self.smax - self.smin
        scl2 = self.smax - s
        return self.bry - (scl2 / scl1) * (self.bry - self.rpad)

class plotWinds(backgroundWinds):
    '''
    Draws the storm relative winds vs. height.
    Inherits from the backgroundWinds class that 
    contains the QPixmap with the background frame
    drawn on it.
    '''
    def __init__(self):
        '''
        Initializes the data from the Profile object
        used to draw the profile.
        
        Parameters
        ----------
        prof: a Profile object
        
        '''
        super(plotWinds, self).__init__()
        ## make the data accessable to the functions
        self.prof = None

    def setProf(self, prof):
        self.prof = prof
        self.srw_0_2km = tab.utils.comp2vec(self.prof.srw_0_2km[0], self.prof.srw_0_2km[1])[1]
        self.srw_4_6km = tab.utils.comp2vec(self.prof.srw_4_6km[0], self.prof.srw_4_6km[1])[1]
        self.srw_9_11km = tab.utils.comp2vec(self.prof.srw_9_11km[0], self.prof.srw_9_11km[1])[1]
        self.u = prof.u; self.v = prof.v
        ## calculate the storm relative wind from the bunkers motion function
        self.srwind = prof.srwind
        ## get only the right mover u and v components
        self.sru = self.u - self.srwind[0]
        self.srv = self.v - self.srwind[1]

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotWinds, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles the painting of the QPixmap onto
        the QWidget.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotWinds, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
    
    def plotData(self):
        '''
        Handles painting the plot data onto the
        QPixmap.
        '''
        if self.prof is None:
            return

        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the wind profile
        self.draw_profile(qp)
        qp.end()

    def draw_profile(self, qp):
        '''
        Draws the storm relative wind profile.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with a red color, thickness of 2, solid line
        pen = QtGui.QPen(QtGui.QColor(RED), 2)
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
                hgt1 = (hgt[i] - self.prof.hght[self.prof.sfc]) / 1000; hgt2 = (hgt[i+1] - self.prof.hght[self.prof.sfc]) / 1000
                sru1 = sru[i]; sru2 = sru[i+1]
                srv1 = srv[i]; srv2 = srv[i+1]
                ## calculate the storm relative wind speed
                spd1 = np.sqrt( sru1**2 + srv1**2 )
                spd2 = np.sqrt( sru2**2 + srv2**2 )
                if tab.utils.QC(spd1) and tab.utils.QC(spd2):
                    ## convert the wind speeds to x pixels
                    x1 = self.speed_to_pix( spd1 ); x2 = self.speed_to_pix(spd2)
                    ## convert the height values to y pixels
                    y1 = self.hgt_to_pix(hgt1); y2 = self.hgt_to_pix(hgt2)
                    ## draw a line between the two points
                    qp.setPen(pen)
                    qp.drawLine(x1, y1, x2, y2)
        
        # Plot the 0-2 km mean SRW
        if tab.utils.QC(self.srw_0_2km):
            pen = QtGui.QPen(QtGui.QColor("#8B0000"), 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_0_2km); x2 = self.speed_to_pix(self.srw_0_2km)
            y1 = self.hgt_to_pix(0.0); y2 = self.hgt_to_pix(2.0)
            qp.drawLine(x1, y1, x2, y2)
                    
        # Plot the 4-6 km mean SRW
        if tab.utils.QC(self.srw_4_6km):
            pen = QtGui.QPen(QtGui.QColor("#6495ED"), 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_4_6km); x2 = self.speed_to_pix(self.srw_4_6km)
            y1 = self.hgt_to_pix(4.0); y2 = self.hgt_to_pix(6.0)
            qp.drawLine(x1, y1, x2, y2)
                    
        # Plot the 9-11 km mean SRW
        if tab.utils.QC(self.srw_9_11km):
            pen = QtGui.QPen(QtGui.QColor("#9400D3"), 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_9_11km); x2 = self.speed_to_pix(self.srw_9_11km)
            y1 = self.hgt_to_pix(9.0); y2 = self.hgt_to_pix(11.0)
            qp.drawLine(x1, y1, x2, y2)
