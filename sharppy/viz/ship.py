import numpy as np
import os
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
import sharppy.databases.inset_data as inset_data
from sharppy.sharptab.constants import *
import platform 

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundSHIP', 'plotSHIP']

class backgroundSHIP(QtWidgets.QFrame):
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
        self.textpad = 5
        self.font_ratio = 0.0512
        fsize1 = round(self.size().height() * self.font_ratio) + 2
        fsize2 = round(self.size().height() * self.font_ratio)
        self.plot_font = QtGui.QFont('Helvetica', fsize1 )
        self.box_font = QtGui.QFont('Helvetica', fsize2)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        if platform.system() == "Windows":
            fsize1 -= self.plot_metrics.descent()
            fsize2 -= self.box_metrics.descent()

            self.plot_font = QtGui.QFont('Helvetica', fsize1 )
            self.box_font = QtGui.QFont('Helvetica', fsize2)
            self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
            self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.xHeight()# + self.textpad
        self.box_height = self.box_metrics.xHeight() + self.textpad
        self.tpad = self.plot_height + 15; 
        self.bpad = self.plot_height + 2
        self.lpad = 0.; self.rpad = 0.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad;
        self.brx = self.wid; 
        self.bry = self.hgt - self.bpad#+ round(self.font_ratio * self.hgt)
        self.shipmax = 5.; self.shipmin = 0.
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
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
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRectF(1.5,6, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Significant Hail Param (SHIP)')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        spacing = self.bry / 6.

        ytick_fontsize = round(self.font_ratio * self.hgt)
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        ship_inset_data = inset_data.shipData()
        texts = ship_inset_data['ship_ytexts']
        for i in range(len(texts)):
            pen = QtGui.QPen(self.line_color, 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.tlx, self.ship_to_pix(int(texts[i])), self.brx, self.ship_to_pix(int(texts[i])))
            except:
                continue
            color = QtGui.QColor(self.bg_color)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            ypos = self.ship_to_pix(int(texts[i])) - ytick_fontsize/2
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        ef = ship_inset_data['ship_dist']
        width = self.brx / 3.7
        spacing = self.brx / 3
        center = np.arange(spacing, self.brx, spacing)
        texts = ship_inset_data['ship_xtexts']
        ef = self.ship_to_pix(ef)
        qp.setFont(QtGui.QFont('Helvetica', round(self.font_ratio * self.hgt)))
        for i in range(ef.shape[0]):
            # Set green pen to draw box and whisker plots 
            pen = QtGui.QPen(self.box_color, 2, QtCore.Qt.SolidLine)
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
            color = QtGui.QColor(self.bg_color)
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRectF(center[i] - width/2., self.bry + self.bpad/2, width, self.bpad)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
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
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.box_color = QtGui.QColor('#00ff00')
        self.line_color = QtGui.QColor('#0080ff')

        self.alert_colors = [
            QtGui.QColor('#775000'),
            QtGui.QColor('#996600'),
            QtGui.QColor('#ffffff'),
            QtGui.QColor('#ffff00'),
            QtGui.QColor('#ff0000'),
            QtGui.QColor('#e700df'),
        ]

        super(plotSHIP, self).__init__()
        self.prof = None

    def setProf(self, prof):
        self.prof = prof
        self.ship = prof.ship

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])
        self.box_color = QtGui.QColor(prefs['stp_box_color'])
        self.line_color = QtGui.QColor(prefs['stp_line_color'])

        self.alert_colors = [
            QtGui.QColor(prefs['alert_l1_color']),
            QtGui.QColor(prefs['alert_l2_color']),
            QtGui.QColor(prefs['alert_l3_color']),
            QtGui.QColor(prefs['alert_l4_color']),
            QtGui.QColor(prefs['alert_l5_color']),
            QtGui.QColor(prefs['alert_l6_color']),
        ]

        if update_gui:
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
        self.plotBitMap.fill(self.bg_color)
    
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
        color_list = self.alert_colors
        if float(ship) >= 5:
            color = color_list[5]
        elif float(ship) >= 2:
            color = color_list[4]
        elif float(ship) >= 1:
            color = color_list[3]
        elif float(ship) >= .5:
            color = color_list[2]
        else:
            color = color_list[0]

        return color

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotSHIP()
    tester.show()    
    app_frame.exec_()
