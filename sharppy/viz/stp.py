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
        self.plot_font = QtGui.QFont('Helvetica', 12)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.plot_height = self.plot_metrics.height()
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 0
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
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
        rect0 = QtCore.QRect(1, 1, self.brx-2, self.bry-2)
        rect1 = QtCore.QRect(2,2, self.brx, self.plot_height)
        image = os.path.join( os.path.dirname( __file__ ), 'bigsharp_stp_vs_ef.png')
        image = QtGui.QImage(image)
        qp.drawImage(rect0, image)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Effective Layer STP (with CIN)')
        ## draw the borders in white



class plotSTP(backgroundSTP):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        super(plotSTP, self).__init__()

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
        ## end the painter
        qp.end()
