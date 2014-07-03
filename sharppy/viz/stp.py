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
        self.box_font = QtGui.QFont('Helvetica', 9)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.height()
        self.box_height = self.box_metrics.height()
        self.lpad = 0.; self.rpad = 0.
        self.tpad = 15.; self.bpad = 15.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.stpmax = 11.; self.stpmin = 0.
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
        rect1 = QtCore.QRectF(1.5,1.5, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Effective Layer STP (with CIN)')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        spacing = self.bry / 12.

        ytick_fontsize = 10
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        texts = ['11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0', ' ']
        y_ticks = np.arange(self.tpad, self.bry+spacing, spacing)
        for i in range(len(y_ticks)):
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            qp.drawLine(self.tlx, y_ticks[i], self.brx, y_ticks[i])
            color = QtGui.QColor('#000000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
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
            rect = QtCore.QRectF(center[i] - width/2., self.stp_to_pix(-.5), width, 4)
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
        self.mlcape = prof.mlpcl.bplus
        self.mllcl = prof.mlpcl.lclhght
        self.esrh = prof.right_esrh[0]
        self.ebwd = prof.ebwd[0]
        self.stpc = prof.stp_cin
        self.stpf = prof.stp_fixed
        ## get the probabilities
        self.cape_p, self.cape_c = self.cape_prob(self.mlcape)
        self.lcl_p, self.lcl_c = self.lcl_prob(self.mllcl)
        self.esrh_p, self.esrh_c = self.esrh_prob(self.esrh)
        self.ebwd_p, self.ebwd_c = self.ebwd_prob(self.ebwd)
        self.stpc_p, self.stpc_c = self.stpc_prob(self.stpc)
        self.stpf_p, self.stpf_c = self.stpf_prob(self.stpf)
    
    def cape_prob(self, cape):
        if cape == 0.:
            prob = 0.00
            color = QtGui.QColor(LBROWN)
        elif cape  > 0. and cape < 250.:
            prob = .12
            color = QtGui.QColor(LBROWN)
        elif cape >= 250. and cape < 500.:
            prob = .14
            color = QtGui.QColor(WHITE)
        elif cape >= 500. and cape < 1000.:
            prob = .16
            color = QtGui.QColor(WHITE)
        elif cape >= 1000. and cape < 1500.:
            prob = .15
            color = QtGui.QColor(WHITE)
        elif cape >= 1500. and cape < 2000.:
            prob = .13
            color = QtGui.QColor(WHITE)
        elif cape >= 2000. and cape < 2500.:
            prob = .14
            color = QtGui.QColor(WHITE)
        elif cape >= 2500. and cape < 3000.:
            prob = .18
            color = QtGui.QColor(YELLOW)
        elif cape >= 3000. and cape < 4000.:
            prob = .20
            color = QtGui.QColor(YELLOW)
        elif cape >= 4000.:
            prob = .16
            color = QtGui.QColor(YELLOW)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color
    
    def lcl_prob(self, lcl):
        if lcl < 750.:
            prob = .19
            color = QtGui.QColor(YELLOW)
        elif lcl >= 750. and lcl < 1000.:
            prob = .19
            color = QtGui.QColor(YELLOW)
        elif lcl >= 1000. and lcl < 1250.:
            prob = .15
            color = QtGui.QColor(WHITE)
        elif lcl >= 1250. and lcl < 1500.:
            prob = .10
            color = QtGui.QColor(LBROWN)
        elif lcl >= 1500. and lcl < 1750:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif lcl >= 1750. and lcl < 2000.:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif lcl >= 2000. and lcl < 2500.:
            prob = .02
            color = QtGui.QColor(DBROWN)
        elif lcl >= 2500:
            prob = 0.0
            color = QtGui.QColor(DBROWN)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color
    
    def esrh_prob(self, esrh):
        if esrh < 50.:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif esrh >= 50. and esrh < 100.:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif esrh >= 100. and esrh < 200.:
            prob = .08
            color = QtGui.QColor(DBROWN)
        elif esrh >= 200. and esrh < 300:
            prob = .14
            color = QtGui.QColor(WHITE)
        elif esrh >= 300. and esrh < 400.:
            prob = .20
            color = QtGui.QColor(YELLOW)
        elif esrh >= 400. and esrh < 500.:
            prob = .27
            color = QtGui.QColor(YELLOW)
        elif esrh >= 500. and esrh < 600:
            prob = .38
            color = QtGui.QColor(RED)
        elif esrh >= 600. and esrh < 700.:
            prob = .37
            color = QtGui.QColor(RED)
        elif esrh >= 700:
            prob = .42
            color = QtGui.QColor(RED)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color
    
    def ebwd_prob(self, ebwd):
        if ebwd == 0.:
            prob = 0.0
            color = QtGui.QColor(DBROWN)
        elif ebwd >= .01 and ebwd < 20.:
            prob = .03
            color = QtGui.QColor(DBROWN)
        elif ebwd >= 20. and ebwd < 30.:
            prob = .05
            color = QtGui.QColor(DBROWN)
        elif ebwd >= 30. and ebwd < 40.:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif ebwd >= 40. and ebwd < 50.:
            prob = .12
            color = QtGui.QColor(LBROWN)
        elif ebwd >= 50. and ebwd < 60.:
            prob = .19
            color = QtGui.QColor(YELLOW)
        elif ebwd >= 60. and ebwd < 70.:
            prob = .27
            color = QtGui.QColor(YELLOW)
        elif ebwd >= 70. and ebwd < 80.:
            prob = .36
            color = QtGui.QColor(RED)
        elif ebwd >= 80.:
            prob = .26
            color = QtGui.QColor(YELLOW)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color

    def stpc_prob(self, stpc):
        if stpc < .1:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif stpc >= .1 and stpc < .50:
            prob = .08
            color = QtGui.QColor(LBROWN)
        elif stpc >= .5 and stpc < 1.0:
            prob = .12
            color = QtGui.QColor(LBROWN)
        elif stpc >= 1. and stpc < 2.:
            prob = .17
            color = QtGui.QColor(WHITE)
        elif stpc >= 2. and stpc < 4.:
            prob = .25
            color = QtGui.QColor(YELLOW)
        elif stpc >= 4. and stpc < 6.:
            prob = .32
            color = QtGui.QColor(RED)
        elif stpc >= 6. and stpc < 8.:
            prob = .34
            color = QtGui.QColor(RED)
        elif stpc >= 8. and stpc < 10.:
            prob = .55
            color = QtGui.QColor(MAGENTA)
        elif stpc >= 10.:
            prob = .58
            color = QtGui.QColor(MAGENTA)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color

    def stpf_prob(self, stpf):
        if stpf < .1:
            prob = .05
            color = QtGui.QColor(DBROWN)
        elif stpf >= .1 and stpf < .5:
            prob = .06
            color = QtGui.QColor(DBROWN)
        elif stpf >= .5 and stpf < 1.:
            prob = .11
            color = QtGui.QColor(LBROWN)
        elif stpf >= 1. and stpf < 2.:
            prob = .17
            color = QtGui.QColor(WHITE)
        elif stpf >= 2. and stpf < 3.:
            prob = .25
            color = QtGui.QColor(YELLOW)
        elif stpf >= 3. and stpf < 5.:
            prob = .25
            color = QtGui.QColor(YELLOW)
        elif stpf >= 5. and stpf < 7.:
            prob = .39
            color = QtGui.QColor(RED)
        elif stpf >= 7. and stpf < 9.:
            prob = .55
            color = QtGui.QColor(MAGENTA)
        elif stpf >= 9.:
            prob = .59
            color = QtGui.QColor(MAGENTA)
        else:
            prob = np.ma.masked
            color = QtGui.QColor(DBROWN)
        return prob, color


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
        self.draw_stp(qp)
        self.draw_box(qp)

    def draw_stp(self, qp):
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        if self.stpc < 0:
            self.stpc = 0
        elif self.stpc > 11.:
            self.stpc = 11.
        if self.stpc < 3:
            color = QtGui.QColor('#996600')
        else:
            color = QtGui.QColor('#FF0000')
        ef = self.stp_to_pix(self.stpc)
        pen = QtGui.QPen(color, 1.5, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, ef, self.wid, ef)
        qp.end()

    def draw_box(self, qp):
        qp.begin(self.plotBitMap)
        width = self.brx / 14.
        left_x = width * 7
        right_x = self.brx - 5.
        top_y = self.stp_to_pix(11.)
        bot_y = top_y + (self.box_height + 1)*8
        ## fill the box with a black background
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(QtCore.Qt.black, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawRect(left_x, top_y, right_x - left_x, bot_y - top_y)
        ## draw the borders of the box
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawLine( left_x, top_y, right_x, top_y )
        qp.drawLine( left_x, bot_y, right_x, bot_y )
        qp.drawLine( left_x, top_y, left_x, bot_y )
        qp.drawLine( right_x, top_y, right_x, bot_y)
        ## set the font and line width for the rest of the plotting
        qp.setFont(self.box_font)
        ## plot the left column of text
        width = right_x - left_x - 3
        y1 = top_y + 2
        x1 = left_x+3
        x2 = x1 + (width * .75)
        ## start with the header/title
        texts = ['Prob EF2+ torn with supercell', 'Sample CLIMO = .15 sigtor']
        for text in texts:
            rect = QtCore.QRectF(x1, y1, width, self.box_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            y1 += self.box_height + 1
        qp.drawLine(left_x, y1-1, right_x, y1-1)
        ## draw the variable names
        texts = ['based on CAPE: ', 'based on LCL:', 'based on ESRH:', 'based on EBWD:',
                 'based on STPC:', 'based on STP_fixed:' ]
        probs = [self.cape_p, self.lcl_p, self.esrh_p, self.ebwd_p, self.stpc_p, self.stpf_p]
        colors = [self.cape_c, self.lcl_c, self.esrh_c, self.ebwd_c, self.stpc_c, self.stpf_c]
        for text, p, c in zip(texts, probs, colors):
            pen = QtGui.QPen(c, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRectF(x1, y1, width, self.box_height)
            rect2 = QtCore.QRectF(x2, y1, width, self.box_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.FLOAT2STR(p,2) )
            y1 += self.box_height
        qp.end()

