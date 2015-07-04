import numpy as np
import os
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
import sharppy.databases.inset_data as inset_data
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundSHIP', 'plotSHIP']

class backgroundSHIP(QtGui.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundSHIP, self).__init__()
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
        if self.physicalDpiX() > 75:
            fsize = 7
        else:
            fsize = 8
        self.plot_font = QtGui.QFont('Helvetica', fsize + 1)
        self.box_font = QtGui.QFont('Helvetica', fsize)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.xHeight() + 5
        self.box_height = self.box_metrics.xHeight() + 5
        self.lpad = 0.; self.rpad = 0.
        self.tpad = 15.; self.bpad = 15.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.shipmax = 5.; self.shipmin = 0.
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
            'Significant Hail Param (SHIP)')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        spacing = self.bry / 6.

        ytick_fontsize = 10
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        ship_inset_data = inset_data.shipData()
        texts = ship_inset_data['ship_ytexts']
        y_ticks = np.arange(self.tpad, self.bry+spacing, spacing)
        for i in xrange(len(y_ticks)):
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.tlx, self.ship_to_pix(int(texts[i])), self.brx, self.ship_to_pix(int(texts[i])))
            except:
                continue
            color = QtGui.QColor('#000000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            ypos = self.ship_to_pix(int(texts[i])) - ytick_fontsize/2
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        ef = ship_inset_data['ship_dist']
        width = self.brx / 3.7
        spacing = self.brx / 3
        center = np.arange(spacing, self.brx, spacing)
        texts = ship_inset_data['ship_xtexts']
        ef = self.ship_to_pix(ef)
        qp.setFont(QtGui.QFont('Helvetica', 10))
        for i in xrange(ef.shape[0]):
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
            #qp.drawLine(center[i] - width/2., ef[i,2], center[i] + width/2., ef[i,2])
            # Draw upper whisker
            qp.drawLine(center[i], ef[i,3], center[i], ef[i,4])
            # Set black transparent pen to draw a rectangle
            color = QtGui.QColor('#000000')
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRectF(center[i] - width/2., self.ship_to_pix(-.2), width, 4)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

    def ship_to_pix(self, ship):
        scl1 = self.shipmax - self.shipmin
        scl2 = self.shipmin + ship
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)


class plotSHIP(backgroundSHIP):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        super(plotSHIP, self).__init__()
        self.prof = None

    def setProf(self, prof):
        self.prof = prof
        self.ship = prof.ship

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()


    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotSHIP, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotSHIP, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
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
        Handles painting on the frame
        '''
        if self.prof is None:
            return

        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        self.draw_ship(qp)

    def draw_ship(self, qp):
        if not tab.utils.QC(self.ship):
            return

        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)

        if self.ship < self.shipmin:
            self.ship = self.shipmin
        elif self.ship > self.shipmax:
            self.ship = self.shipmax

        color = self.ship_color(self.ship) 
        ef = self.ship_to_pix(self.ship)
        pen = QtGui.QPen(color, 1.5, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, ef, self.wid, ef)
        qp.end()

    def ship_color(self, ship):
        color_list = [QtGui.QColor(CYAN), QtGui.QColor(DBROWN), QtGui.QColor(LBROWN), QtGui.QColor(WHITE), QtGui.QColor(YELLOW), QtGui.QColor(RED), QtGui.QColor(MAGENTA)]
        if float(ship) >= 5:
            color = color_list[6]
        elif float(ship) >= 2:
            color = color_list[5]
        elif float(ship) >= 1:
            color = color_list[4]
        elif float(ship) >= .5:
            color = color_list[3]
        else:
            color = color_list[1]

        return color

