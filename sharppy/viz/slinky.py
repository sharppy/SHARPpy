import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import platform

__all__ = ['backgroundSlinky', 'plotSlinky']

## Written by Greg Blumberg - CIMMS
## wblumberg@ou.edu

class backgroundSlinky(QtWidgets.QFrame):
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
        self.font_ratio = 0.0512
        self.title_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio)+2)
        self.plot_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio))
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
        self.plotBitMap.fill(self.bg_color)
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
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
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
    def __init__(self, **kwargs):
        '''
        Initializes data variables needed to draw 
        the slinky by taking in a Profile object.
        
        Parameters
        ----------
        prof: a Profile Object
        
        '''
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.use_left = False

        super(plotSlinky, self).__init__()
        self.prof = None
        self.pcl = None

        self.low_level_color = QtGui.QColor(RED)
        self.mid_level_color = QtGui.QColor("#00FF00")
        self.upper_level_color = QtGui.QColor(YELLOW)
        self.trop_level_color = QtGui.QColor("#00FFFF")

    def setProf(self, prof):
        self.prof = prof

        if self.use_left:
            self.smu = self.prof.srwind[2]
            self.smv = self.prof.srwind[3]
        else:
            self.smu = self.prof.srwind[0]
            self.smv = self.prof.srwind[1]

        self.pcl = None

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setParcel(self, pcl):
        self.pcl = pcl

        if self.prof is not None:
            self.slinky_traj, self.updraft_tilt = tab.params.parcelTraj(self.prof, pcl, self.smu, self.smv)

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        self.low_level_color = QtGui.QColor(prefs['0_3_color'])
        self.mid_level_color = QtGui.QColor(prefs['3_6_color'])
        self.upper_level_color = QtGui.QColor(prefs['6_9_color'])
        self.trop_level_color = QtGui.QColor(prefs['9_12_color'])

        if update_gui:

            if self.use_left:
                self.smu = self.prof.srwind[2]
                self.smv = self.prof.srwind[3]
            else:
                self.smu = self.prof.srwind[0]
                self.smv = self.prof.srwind[1]

            self.slinky_traj, self.updraft_tilt = tab.params.parcelTraj(self.prof, self.pcl, self.smu, self.smv)

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        if self.use_left:
            self.smu = self.prof.srwind[2]
            self.smv = self.prof.srwind[3]
        else:
            self.smu = self.prof.srwind[0]
            self.smv = self.prof.srwind[1]

        self.slinky_traj, self.updraft_tilt = tab.params.parcelTraj(self.prof, self.pcl, self.smu, self.smv)

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
        if self.prof is None or self.pcl is None:
            return

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
        self.plotBitMap.fill(self.bg_color)
   
    def plotSMV(self, qp):
        '''
        Draws the line representing the Storm Motion Vector.
        
        Parameters
        ----------
        qp: a QtGui.QPainter object
        
        '''
        ## set the pen
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
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
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        ## draw the text
        rect0 = QtCore.QRect(self.brx-30, self.tly+2, 30, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, tab.utils.INT2STR(self.updraft_tilt) + ' deg  ')

    def plotSlinky(self, qp):
        '''
        Plots the circles of the Storm Slinky.
        
        Parameters
        ----------
        qp: a QtGui.QPainter object
        
        '''
        ## set the pen
        pen = QtGui.QPen(self.trop_level_color, 1, QtCore.Qt.SolidLine)
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
                pen = QtGui.QPen(self.low_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 6000:
                pen = QtGui.QPen(self.mid_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 9000:
                pen = QtGui.QPen(self.upper_level_color, 1, QtCore.Qt.SolidLine)
            elif z < 12000:
                pen = QtGui.QPen(self.trop_level_color, 1, QtCore.Qt.SolidLine)
            else:
                continue
            ## draw the circle
            qp.setPen(pen)
            xx, yy = self.xy_to_pix(x,y)
            center = QtCore.QPointF(xx, yy)
            qp.drawEllipse(center, 5, 5)

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotSlinky()
    tester.setGeometry(100,100,121,138)
    tester.show()    
    app_frame.exec_()
