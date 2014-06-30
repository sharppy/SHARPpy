import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

__all__ = ['backgroundSlinky', 'plotSlinky']

## Written by Greg Blumberg - CIMMS
## wblumberg@ou.edu

class backgroundSlinky(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Storm Slinky plot frame
    '''
    def __init__(self):
        super(backgroundSlinky, self).__init__()
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
        self.center_hodo()
        self.title_font = QtGui.QFont('Helvetica', 9)
        self.plot_font = QtGui.QFont('Helvetica', 9)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.title_height = self.title_metrics.height()
        self.plot_height = self.plot_metrics.height()
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()  

    def center_hodo(self):
        '''
        Center the hodograph in the window. Can/Should be overwritten.

        '''
        self.centerx = self.wid / 2; self.centery = self.hgt / 2
        self.hodomag = 6000.*1.7
        self.scale = (self.brx - self.tlx) / self.hodomag

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized
        '''
        self.initUI()

    def draw_frame(self, qp):
        '''
        Draw the background frame.
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

        rect0 = QtCore.QRect(2, self.bry-11, 11, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Storm Slinky')
    
    def draw_axes(self, qp):
        '''
        Draw the X, Y Axes.
        --------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame axes
        pen = QtGui.QPen(QtGui.QColor('#003366'), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame axes
        qp.drawLine(self.centerx, self.tly, self.centerx, self.bry)
        qp.drawLine(self.tlx, self.centery, self.brx, self.centery)
    
    def plotBackground(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the frame
        self.draw_frame(qp)
        self.draw_axes(qp)
        qp.end()

    def xy_to_pix(self, x, y):
        '''
        Function to convert (x, y) to pixel (x, y) coordinates.
        --------
        x: the x distance component
        y: the y distance component

        '''
        xx = self.centerx + (x * self.scale)
        yy = self.centery - (y * self.scale)
        return xx, yy


class plotSlinky(backgroundSlinky):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self, prof):
        self.prof = prof
        super(plotSlinky, self).__init__()
        self.slinky_traj = self.prof.slinky_traj
        self.updraft_tilt = self.prof.updraft_tilt
        self.smu = self.prof.srwind[0]
        self.smv = self.prof.srwind[1]

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotSlinky, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        super(plotSlinky, self).paintEvent(e)
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self)
        ## end the painter
        qp.drawPixmap(0,0,self.plotBitMap)
        qp.end()

    def plotData(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.plotSlinky(qp)
        self.plotSMV(qp)
        self.plotTilt(qp)
        qp.end()
   
    def plotSMV(self, qp):
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        wdir, wspd = tab.utils.comp2vec(self.smu, self.smv)
        u, v = tab.utils.vec2comp(wdir, 3000)
        motion_x, motion_y = self.xy_to_pix(u,v)
        center_x, center_y = self.xy_to_pix(0,0)
        qp.drawLine(motion_x,motion_y, center_x,center_y)

    def plotTilt(self, qp):
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(self.brx-30, self.tly+2, 30, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, str(round(self.updraft_tilt,0)) + ' deg  ')

    def plotSlinky(self, qp):
        low_level_color = QtGui.QColor("#FF0000")
        mid_level_color = QtGui.QColor("#00FF00")
        upper_level_color = QtGui.QColor("#FFFF00")
        trop_level_color = QtGui.QColor("#00FFFF")
        pen = QtGui.QPen(trop_level_color, 1, QtCore.Qt.SolidLine)
        if self.slinky_traj is np.ma.masked:
            return
        for i in self.slinky_traj[::-1]:
            x = i[0]
            y = i[1]
            z = i[2]
            if z == self.slinky_traj[-1][2]:
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
            qp.setPen(pen)
            xx, yy = self.xy_to_pix(x,y)
            center = QtCore.QPointF(xx, yy)
            qp.drawEllipse(center, 6, 6)

