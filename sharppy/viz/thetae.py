import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtOpenGL import *
import sharppy.sharptab as tab
import sharppy.sharptab.utils as utils
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert - OU School of Meteorology
## keltonhalbert@ou.edu

__all__ = ['backgroundThetae', 'plotThetae']


class backgroundThetae(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot.
    Draws the background on a QPixmap.
    
    Inherits a QtWidgets.QFrame Object
    '''
    def __init__(self):
        super(backgroundThetae, self).__init__()
        self.initUI()


    def initUI(self):
        '''
        Initializes window variables and the QPixmap
        that gets drawn on.
        '''
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
        ## do a DPI check for the font size
        if self.physicalDpiX() > 75:
            fsize = 6
        else:
            fsize = 7
        self.font_ratio = 0.0512
        self.label_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio))
        ## initialize the QPixmap
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.clear()
        ## and draw the background
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        Handles the drawing of the background onto
        the QPixmap.
        '''
        ## initialize a painter object and draw the frame
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.draw_frame(qp)
        ## draw the isobar ticks and the theta-e ticks
        for p in [1000, 900, 800, 700, 600, 500]:
            self.draw_isobar(p, qp)
        for t in np.arange( 200, 400, 10):
            self.draw_thetae(t, qp)
        qp.end()

    def clear(self):
        '''
        Clear the widget
        '''
        self.plotBitMap.fill(self.bg_color)

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
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
        Draw background isobar ticks.
        
        Parameters
        ----------
        p: pressure in hPa or mb
        qp: QtGui.QPainter object
        
        '''
        ## set a new pen with a white color and solid line of thickness 1
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
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
                utils.INT2STR(p))

    def draw_thetae(self, t, qp):
        '''
        Draw background Theta-E ticks.
        
        Parameters
        ----------
        t: Theta-E in degrees Kelvin
        qp: QtGui.QPainter object
        
        '''
        ## set a new pen with a white color, thickness one, solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
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
        qp.drawText(x1, self.bry-20, 15, 20,
            QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, utils.INT2STR(t))

    def pres_to_pix(self, p):
        '''
        Function to convert a pressure value (hPa) to a Y pixel.
        
        Parameters
        ----------
        p: pressure in hPa or mb
        
        '''
        scl1 = self.pmax - self.pmin
        scl2 = self.pmax - p
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def theta_to_pix(self, t):
        '''
        Function to convert a Theta-E value (K) to a X pixel.
        
        Parameters
        ----------
        t: temperature in Kelvin
        
        '''
        scl1 = self.tmax - self.tmin
        scl2 = self.tmax - t
        return self.bry - (scl2 / scl1) * (self.bry - self.rpad)

class plotThetae(backgroundThetae):
    '''
    Draws the theta-E window. Inherits from the backgroundThetae
    class that handles plotting of the frame. Draws the contours
    to the QPixmap inherited by the backgroundThetae class.
    '''
    def __init__(self):
        '''
        Initializes the data needed from the Profile object.
        
        Parameters
        ----------
        prof: a Profile object
        
        '''
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.thte_color = QtGui.QColor('#ff0000')

        super(plotThetae, self).__init__()
        ## set the varables for pressure and thetae
        self.prof = None

    def setProf(self, prof):
        self.prof = prof
        self.thetae = prof.thetae
        self.pres = prof.pres

        idx = np.where( self.pres > 400. )[0]
        self.tmin = self.thetae[idx].min() - 10.
        self.tmax = self.thetae[idx].max() + 10.

        self.clear()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])
        self.thte_color = QtGui.QColor(prefs['temp_color'])

        if update_gui:
            self.clear()
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
        super(plotThetae, self).resizeEvent(e)
        if self.prof is not None:
            idx = np.where( self.pres > 400. )[0]
            self.tmin = self.thetae[idx].min() - 10.
            self.tmax = self.thetae[idx].max() + 10.
        self.update()
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Draws the QPixmap onto the QWidget.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotThetae, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Plots the data onto the QPixmap.
        '''
        if self.prof is None:
            return

        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the theta-e profile
        self.draw_profile(qp)
        ## end the painter
        qp.end()

    def draw_profile(self, qp):
        '''
        Draw the Theta-E v. Pres profile.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        pen = QtGui.QPen(self.thte_color, 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        mask1 = self.thetae.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        pres = self.pres[~mask]
        thetae = self.thetae[~mask]
        for i in range( pres.shape[0] - 1 ):
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

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotThetae()
    tester.show()    
    app_frame.exec_()

