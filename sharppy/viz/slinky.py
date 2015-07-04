import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import platform

__all__ = ['backgroundSlinky', 'plotSlinky']

## Written by Greg Blumberg - CIMMS
## wblumberg@ou.edu

class backgroundSlinky(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Storm Slinky.
    Draws onto a QPixmap.
    '''
    def __init__(self):
        super(backgroundSlinky, self).__init__()
        self.initUI()


    def initUI(self):
        ## window configuration settings,
        ## sich as padding, width, height, and
        ## min/max plot axes
        self.lpad = 5; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.fpad = 5
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## center the frame on the slinky
        self.center_frame()
        if self.physicalDpiX() > 75:
            fsize = 7
        else:
            fsize = 9
        self.title_font = QtGui.QFont('Helvetica', fsize)
        self.plot_font = QtGui.QFont('Helvetica', fsize)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.os_mod = 0
        if platform.system() == "Windows":
            self.os_mod = self.plot_metrics.descent()

        ## get the pixel height of the font
        self.title_height = self.title_metrics.xHeight() + self.fpad
        self.plot_height = self.plot_metrics.xHeight() + self.fpad
        ## initialize the QPixmap that the frame and data will be drawn on
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        ## plot the background
        self.plotBackground()  

    def center_frame(self):
        '''
        Center the slinky in the window.

        '''
        self.centerx = self.wid / 2; self.centery = self.hgt / 2
        self.mag = 7000.*1.7
        self.scale = (self.brx - self.tlx) / self.mag

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized.
        '''
        self.initUI()

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        
        ## draw the borders in white
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

        yval = self.bry - self.title_height - self.os_mod - 2
        rect0 = QtCore.QRect(self.lpad, yval, 20, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Storm Slinky')
    
    def draw_axes(self, qp):
        '''
        Draw the X, Y Axes.
        
        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame axes
        pen = QtGui.QPen(QtGui.QColor('#003366'), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame axes
        qp.drawLine(self.centerx, self.tly, self.centerx, self.bry)
        qp.drawLine(self.tlx, self.centery, self.brx, self.centery)
    
    def plotBackground(self):
        '''
        Draws the background frame onto the QPixmap.
        '''
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the frame
        self.draw_axes(qp)
        self.draw_frame(qp)
        qp.end()

    def xy_to_pix(self, x, y):
        '''
        Function to convert (x, y) to pixel (xx, yy) coordinates.
        --------
        x: the x distance component
        y: the y distance component

        '''
        xx = self.centerx + (x * self.scale)
        yy = self.centery - (y * self.scale)
        return xx, yy


class plotSlinky(backgroundSlinky):
    '''
    Plots the data on the frame. Inherits from the
    backgroundSlinky class and draws on the QPixmap
    that is initialized there.
    '''
    def __init__(self, prof, **kwargs):
        '''
        Initializes data variables needed to draw 
        the slinky by taking in a Profile object.
        
        Parameters
        ----------
        prof: a Profile Object
        
        '''
        self.prof = prof
        self.pcl = kwargs.get('pcl', self.prof.mupcl)
        super(plotSlinky, self).__init__()
        self.slinky_traj = self.prof.slinky_traj
        self.updraft_tilt = self.prof.updraft_tilt
        self.smu = self.prof.srwind[0]
        self.smv = self.prof.srwind[1]

    def setProf(self, prof, pcl):
        self.prof = prof
        self.pcl = pcl
        #self.slinky_traj = self.prof.slinky_traj
        #self.updraft_tilt = self.prof.updraft_tilt
        self.smu = self.prof.srwind[0]
        self.smv = self.prof.srwind[1]
        self.slinky_traj, self.updraft_tilt = tab.params.parcelTraj(prof, pcl, self.smu, self.smv)
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
        super(plotSlinky, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles painting the QPixmap onto the frame.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        ## this function handles painting the plot
        super(plotSlinky, self).paintEvent(e)
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0,0,self.plotBitMap)
        qp.end()

    def plotData(self):
        '''
        Draws the data onto the QPixmap.
        '''
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.plotSlinky(qp)
        self.plotSMV(qp)
        self.plotTilt(qp)
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
   
    def plotSMV(self, qp):
        '''
        Draws the line representing the Storm Motion Vector.
        
        Parameters
        ----------
        qp: a QtGui.QPainter object
        
        '''
        ## set the pen
        pen = QtGui.QPen(QtGui.QColor(WHITE), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## scale the vector to be visible in the window
        if tab.utils.QC(self.smu) and tab.utils.QC(self.smv):
            wdir, wspd = tab.utils.comp2vec(self.smu, self.smv)
            u, v = tab.utils.vec2comp(wdir, 3000)
            ## convert the unit space to pixel space
            motion_x, motion_y = self.xy_to_pix(u,v)
            center_x, center_y = self.xy_to_pix(0,0)
            qp.drawLine(motion_x,motion_y, center_x,center_y)

    def plotTilt(self, qp):
        '''
        Plots the data for the updraft tilt.
        
        Parameters
        ----------
        qp: a QtGui.QPainter object
        
        '''
        ## initialize a pen
        pen = QtGui.QPen(QtGui.QColor(WHITE), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        ## draw the text
        rect0 = QtCore.QRect(self.brx-30, self.tly+2, 30, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, str(round(self.updraft_tilt,0)) + ' deg  ')

    def plotSlinky(self, qp):
        '''
        Plots the circles of the Storm Slinky.
        
        Parameters
        ----------
        qp: a QtGui.QPainter object
        
        '''
        ## set the various colors
        low_level_color = QtGui.QColor(RED)
        mid_level_color = QtGui.QColor("#00FF00")
        upper_level_color = QtGui.QColor(YELLOW)
        trop_level_color = QtGui.QColor("#00FFFF")
        ## set the pen
        pen = QtGui.QPen(trop_level_color, 1, QtCore.Qt.SolidLine)
        ## if there is no storm slinky, don't plot it!
        if self.slinky_traj is np.ma.masked:
            return

        has_el = self.pcl.bplus > 1e-3 and tab.utils.QC(self.pcl.elhght)

        ## loop through the parcel tradjectory in reverse
        for tradj in self.slinky_traj[:]:
            ## get the x, y, and z location of the updraft at each height
            x = tradj[0]
            y = tradj[1]
            z = tradj[2]

            if not tab.utils.QC(x) or not tab.utils.QC(y):
                continue

            ## set the various colors
            if has_el and z == self.slinky_traj[-1][2]:
                pen = QtGui.QPen(QtGui.QColor("#FF00FF"), 1, QtCore.Qt.SolidLine)
            elif z < 3000:
                pen = QtGui.QPen(low_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 6000:
                pen = QtGui.QPen(mid_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 9000:
                pen = QtGui.QPen(upper_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 12000:
                pen = QtGui.QPen(trop_level_color, 1, QtCore.Qt.SolidLine)
            else:
                continue
            ## draw the circle
            qp.setPen(pen)
            xx, yy = self.xy_to_pix(x,y)
            center = QtCore.QPointF(xx, yy)
            qp.drawEllipse(center, 5, 5)

