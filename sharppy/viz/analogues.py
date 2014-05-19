import numpy as np
import os
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.sars import sars_hail
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundAnalogues', 'plotAnalogues']

class backgroundAnalogues(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundAnalogues, self).__init__()
        self.initUI()

    def initUI(self):
        ## initialize fram variables such as size,
        ## padding, etc.
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        self.title_font = QtGui.QFont('Helvetica', 14)
        self.plot_font = QtGui.QFont('Helvetica', 12)
        self.match_font = QtGui.QFont('Helvetica', 10)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.match_metrics = QtGui.QFontMetrics( self.match_font )
        self.title_height = self.title_metrics.height()
        self.plot_height = self.plot_metrics.height()
        self.match_height = self.match_metrics.height()
        self.lpad = 5; self.rpad = 5
        self.tpad = 10; self.bpad = 5
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 6
        y1 = self.bry / 19
        ## create the rectangles for drawing text
        rect0 = QtCore.QRect(0, 5, self.brx, self.title_height)
        rect1 = QtCore.QRect(x1*1, y1*2 + self.bpad, x1, self.plot_height)
        rect2 = QtCore.QRect(x1*4, y1*2 + self.bpad, x1, self.plot_height)
        ## draw the title text
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SARS - Sounding Analogue System')
        qp.setFont(self.plot_font)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SUPERCELL')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SGFNT HAIL')
        ## draw some separating lines
        qp.drawLine(0, y1*2, self.brx, y1*2)
        qp.drawLine(self.brx/2, y1*2, self.brx/2, self.bry)
    

    
    def resizeEvent(self, e):
        '''
        Handles when the window gets resized.
        '''
        self.initUI()

    def plotBackground(self):
        '''
        Handles drawing the text background.
        '''
        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the frame
        self.draw_frame(qp)
        qp.end()


class plotAnalogues(backgroundAnalogues):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.prof = prof
        self.matches = prof.matches
        super(plotAnalogues, self).__init__()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotAnalogues, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotAnalogues, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()

    def plotData(self):
        '''
        Handles the drawing of the text on the frame.
        '''
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the indices
        self.drawSARS_hail(qp)
        self.drawSARS_tor(qp)
        qp.end()
    
    def drawSARS_hail(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen to draw with.
        if self.matches is np.ma.masked:
            return
        else:
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setFont(self.plot_font)
            x1 = self.brx / 6
            y1 = self.bry / 19
            sig_hail_prob = str( int( self.matches[-1]*100 ))
            sig_hail_str = 'SARS: ' + sig_hail_prob + '% SIG'
            num_matches = str( int( self.matches[-3]))
            match_str = '(' + num_matches + ' loose matches)'
            ## draw the matches statistics
            rect0 = QtCore.QRect(x1*4, y1*18, x1, self.plot_height)
            rect1 = QtCore.QRect(x1*4, y1*17-self.bpad, x1, self.match_height)
            rect2 = QtCore.QRect(x1*4, y1*8, x1, self.match_height)
            if self.matches[-3] > 0:
                qp.setFont(self.match_font)
                qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    sig_hail_str)
                qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    match_str)
            else:
                pass
            if len(self.matches[0]) == 0:
                qp.setFont(self.match_font)
                qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    'No Quality Matches')

    def drawSARS_tor(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen to draw with.
        if self.matches is np.ma.masked:
            return
        else:
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setFont(self.match_font)
            x1 = self.brx / 6
            y1 = self.bry / 19
            ## draw the matches statistics
            rect0 = QtCore.QRect(x1*2, y1*18, x1, self.plot_height)
            rect1 = QtCore.QRect(x1*2, y1*17-self.bpad, x1, self.match_height)
            rect2 = QtCore.QRect(x1*1, y1*8, x1, self.match_height)
            qp.setFont(self.match_font)
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                'No Quality Matches')






