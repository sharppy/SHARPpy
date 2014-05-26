import numpy as np
import os
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from scipy.misc import bytescale
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundSTP', 'plotSTP']

class backgroundSTP(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundSTP, self).__init__()
        self.initUI()


    def initUI(self):
        ## window configuration settings,
        ## sich as padding, width, height, and
        ## min/max plot axes
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        self.plot_font = QtGui.QFont('Helvetica', 11)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.plot_height = self.plot_metrics.height()
        self.lpad = 0; self.rpad = 0
        self.tpad = 12; self.bpad = 12
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.stpmax = 11; self.stpmin = 0
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
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
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.draw_frame(qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRect(2,2, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Effective Layer STP (with CIN)')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        spacing = self.bry / 12.

        ytick_fontsize = 10
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        texts = ['11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0', '']
        y_ticks = np.arange(self.tpad, self.bry+spacing, spacing)
        for i in range(len(y_ticks)):
            pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            qp.drawLine(self.tlx, y_ticks[i], self.brx, y_ticks[i])
            color = QtGui.QColor('#000000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRect(self.tlx, spacing*(i+1)-spacing/2, 20, ytick_fontsize)
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        ef = [[1.2, 2.6, 5.3, 8.3, 11.0], #ef4
              [0.2, 1.0, 2.4, 4.5, 8.4], #ef3
              [0.0, 0.6, 1.7, 3.7, 5.6], #ef2
              [0.0, 0.3, 1.2, 2.6, 4.5], #ef1
              [0.0, 0.1, 0.8, 2.0, 3.7], # ef-0
              [0.0, 0.0, 0.2, 0.7, 1.7]] #nontor
        ef = np.array(ef)
        width = self.brx / 14
        spacing = self.brx / 7
        center = np.arange(spacing, self.brx, spacing)
        texts = ['EF4+', 'EF3', 'EF2', 'EF1', 'EF0', 'NONTOR']
        ef = self.stp_to_pix(ef)
        qp.setFont(QtGui.QFont('Helvetica', 8))
        for i in range(ef.shape[0]):
            # Set green pen to draw box and whisker plots 
            pen = QtGui.QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            # Draw lower whisker
            qp.drawLine(center[i], ef[i,0], center[i], ef[i,1])
            # Draw box
            qp.drawLine(center[i] - width/2., ef[i,3], center[i] + width/2., ef[i,3])
            qp.drawLine(center[i] - width/2., ef[i,1], center[i] + width/2., ef[i,1])
            qp.drawLine(center[i] - width/2., ef[i,1], center[i] - width/2., ef[i,3])
            qp.drawLine(center[i] + width/2., ef[i,1], center[i] + width/2., ef[i,3])
            # Draw median
            qp.drawLine(center[i] - width/2., ef[i,2], center[i] + width/2., ef[i,2])
            # Draw upper whisker
            qp.drawLine(center[i], ef[i,3], center[i], ef[i,4])
            # Set black transparent pen to draw a rectangle
            color = QtGui.QColor('#000000')
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRect(center[i] - width/2., self.stp_to_pix(-.25), width, 4)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

    def stp_to_pix(self, stp):
        scl1 = self.stpmax - self.stpmin
        scl2 = self.stpmin + stp
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)


class plotSTP(backgroundSTP):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self, prof):
        super(plotSTP, self).__init__()
        self.stp_cin = prof.stp_cin

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotSTP, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotSTP, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ef = self.stp_to_pix(self.stp_cin)
        color = QtGui.QColor('#996600')
        pen = QtGui.QPen(color, 1.5, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, ef, self.wid, ef)
       
        ## end the painter
        qp.end()
