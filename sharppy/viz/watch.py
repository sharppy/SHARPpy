import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *

## Written by Kelton Halbert - OU School of Meteorology
## and Greg Blumberg - CIMMS


__all__ = ['backgroundWatch', 'plotWatch']

class backgroundWatch(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the watch plot frame
    '''
    def __init__(self):
        super(backgroundWatch, self).__init__()
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
        if self.physicalDpiX() > 75:
            fsize = 10
        else:
            fsize = 12
        #fsize = 10
        self.font_ratio = 0.0512
        self.title_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio) + 5)
        self.plot_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio) + 4)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.title_height = self.title_metrics.height()
        self.plot_height = self.plot_metrics.height()
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()  

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
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        
        ## draw the borders in white
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

        y1 = self.bry / 13.
        pad = self.bry / 100.
        rect0 = QtCore.QRect(0, pad*4, self.brx, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Psbl Haz. Type')
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, pad*4 + (self.title_height + 3), self.brx, pad*4 + (self.title_height + 3))
    
    def plotBackground(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        #qp.setRenderHint(qp.Antialiasing)
        #qp.setRenderHint(qp.TextAntialiasing)
        ## draw the frame
        self.draw_frame(qp)
        qp.end()

class plotWatch(backgroundWatch):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')

        self.pdstor_color   = QtGui.QColor('#ff00ff')
        self.tor_color      = QtGui.QColor('#ff0000')
        self.svr_color      = QtGui.QColor('#ffff00')
        self.mrglsvr_color  = QtGui.QColor('#0099cc')
        self.flood_color    = QtGui.QColor('#5ffb17')
        self.blizzard_color = QtGui.QColor('#3366ff')
        self.fire_color     = QtGui.QColor('#ff9900')
        self.heat_color     = QtGui.QColor('#c85a17')
        self.none_color     = QtGui.QColor('#ffcc33')

        self.color_map = {
            'PDS TOR':        'pdstor_color',
            'TOR':            'tor_color',
            'MRGL TOR':       'tor_color',
            'SVR':            'svr_color',
            'MRGL SVR':       'mrglsvr_color',
            'FLASH FLOOD':    'flood_color',
            'BLIZZARD':       'blizzard_color',
            'WIND CHILL':     'blizzard_color',
            'FREEZE':         'blizzard_color',
            'FIRE WEATHER':   'fire_color',
            'EXCESSIVE HEAT': 'heat_color',
            'NONE':           'none_color',
        }

        self.use_left = False

        super(plotWatch, self).__init__()
        self.prof = None 

    def setProf(self, prof):
        self.prof = prof
        if self.use_left:
            self.watch_type = self.prof.left_watch_type
        else:
            self.watch_type = self.prof.right_watch_type

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        self.pdstor_color   = QtGui.QColor(prefs['watch_pdstor_color'])
        self.tor_color      = QtGui.QColor(prefs['watch_tor_color'])
        self.svr_color      = QtGui.QColor(prefs['watch_svr_color'])
        self.mrglsvr_color  = QtGui.QColor(prefs['watch_mrglsvr_color'])
        self.flood_color    = QtGui.QColor(prefs['watch_flood_color'])
        self.blizzard_color = QtGui.QColor(prefs['watch_blizzard_color'])
        self.fire_color     = QtGui.QColor(prefs['watch_fire_color'])
        self.heat_color     = QtGui.QColor(prefs['watch_heat_color'])
        self.none_color     = QtGui.QColor(prefs['watch_none_color'])

        if update_gui:
            if self.use_left:
                self.watch_type = self.prof.left_watch_type
            else:
                self.watch_type = self.prof.right_watch_type

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'
        if self.use_left:
            self.watch_type = self.prof.left_watch_type
        else:
            self.watch_type = self.prof.right_watch_type

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotWatch, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        super(plotWatch, self).paintEvent(e)
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self)
        ## end the painter
        qp.drawPixmap(0,0,self.plotBitMap)
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)

    def plotData(self):
        if self.prof is None:
            return

        watch_type_color = getattr(self, self.color_map[self.watch_type])

        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        pen = QtGui.QPen(QtGui.QColor(watch_type_color), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)        
        qp.setFont(self.plot_font)
        centery = self.bry / 2.
        rect0 = QtCore.QRect(0, centery, self.brx, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, self.watch_type)
        qp.end()

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotWatch()
    tester.show()    
    app_frame.exec_()
