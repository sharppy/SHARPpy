import numpy as np
import os
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab.params as params
import sharppy.sharptab.winds as winds
import sharppy.sharptab.interp as interp
import sharppy.databases.inset_data as inset_data
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundENS', 'plotENS']

class backgroundENS(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundENS, self).__init__()
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
            fsize = 10
        else:
            fsize = 11
        fsize = np.floor(.055 * self.size().height())
        self.fsize = fsize
        self.plot_font = QtGui.QFont('Helvetica', fsize + 1)
        self.box_font = QtGui.QFont('Helvetica', fsize)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.xHeight() + 5
        self.box_height = self.box_metrics.xHeight() + 5
        self.lpad = 40; self.rpad = 40.
        self.tpad = fsize * 2 + 5; self.bpad = fsize
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.ymax = 3000.; self.ymin = 0.
        self.xmax = 3000.; self.xmin = 0.
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

    def setBlackPen(self, qp):
        color = QtGui.QColor('#000000')
        color.setAlphaF(.5)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        return qp

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        EF1_color = "#006600"
        EF2_color = "#FFCC33"
        EF3_color = "#FF0000"
        EF4_color = "#FF00FF"

        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRectF(1.5, 2, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Ensemble Indices')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        ytick_fontsize = self.fsize-1
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        efstp_inset_data = inset_data.condSTPData()
        #texts = efstp_inset_data['ytexts']
        spacing = self.bry / 10.
        texts = ['0','1000','2000','3000']
        y_ticks = [0,1000,2000,3000]#np.arange(self.tpad, self.bry+spacing, spacing)
        for i in range(len(y_ticks)):
            #print y_ticks[i]
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.tlx, self.y_to_ypix(int(texts[i])), self.brx, self.y_to_ypix(int(texts[i])))
            except:
                continue
            color = QtGui.QColor('#000000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            ypos = self.y_to_ypix(int(texts[i])) - ytick_fontsize/2
            xpos = self.tlx - 50/2.
            rect = QtCore.QRect(xpos, ypos, 50, ytick_fontsize)
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        width = self.brx / 12
        spacing = self.brx / 12

        # Draw the x tick marks
        qp.setFont(QtGui.QFont('Helvetica', self.fsize-1))
        for i in range(np.asarray(texts).shape[0]):
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.x_to_xpix(int(texts[i])), self.tly,  self.x_to_xpix(int(texts[i])),self.bry)
            except:
                continue
            color = QtGui.QColor('#000000')
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            ypos = self.y_to_ypix(0)
            xpos = self.x_to_xpix(float(texts[i])) - 50 / 2.
            rect = QtCore.QRect(xpos, ypos, 50, ytick_fontsize)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])


    def y_to_ypix(self, y):
        scl1 = self.ymax - self.ymin
        scl2 = self.ymin + y
        #print scl1, scl2, self.bry, self.tpad, self.tly
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def x_to_xpix(self, x):
        scl1 = self.xmax - self.xmin
        scl2 = self.xmax - x
        return self.brx - (scl2 / scl1) * (self.brx - self.rpad)


class plotENS(backgroundENS):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')

        self.use_left = False

        super(plotENS, self).__init__()
        self.prof = None
        self.pc_idx = 0
        self.prof_collections = []

    def addProfileCollection(self, prof_coll):
        # Add a profile collection to the scatter plot
        self.prof_collections.append(prof_coll)

    def rmProfileCollection(self, prof_coll):
        # Remove a profile collection from the scatter plot
        self.prof_collections.remove(prof_coll)

    def setActiveCollection(self, pc_idx, **kwargs):
        # Set the active profile collection that is being shown in SPCWindow.
        self.pc_idx = pc_idx
        prof = self.prof_collections[pc_idx].getHighlightedProf()

        self.prof = prof
        self.hght = prof.hght

        self.clearData()
        self.plotData()
        self.update()

    def setProf(self, prof):
        # Set the current profile being viewed in the SPC window.
        self.prof = prof

        # Some code to show whether or not the left or right mover is being used.
        #if self.use_left:
        #    self.stpc = prof.left_stp_cin
        #else:
        #    self.stpc = prof.right_stp_cin

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        # Set the preferences for the inset.
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            if self.use_left:
                self.stpc = self.prof.left_stp_cin
            else:
                self.stpc = self.prof.right_stp_cin

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        # Set the variable to indicate whether or not the right or left mover is being used.
        self.use_left = deviant == 'left'

        if self.use_left:
            self.stpc = self.prof.left_stp_cin
        else:
            self.stpc = self.prof.right_stp_cin

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotENS, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotENS, self).paintEvent(e)
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
        Handles drawing of data on the frame.
        '''
        if self.prof is None:
            return

        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)

        cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        bc_idx = 0
        for idx, prof_coll in enumerate(self.prof_collections):
            # Draw all unhighlighed ensemble members
            if prof_coll.getCurrentDate() == cur_dt:
                proflist = list(prof_coll.getCurrentProfs().values())

                if idx == self.pc_idx:
                    for prof in proflist:
                        self.draw_ensemble_point(qp, prof)
                else:
                    for prof in proflist:
                        self.draw_ensemble_point(qp, prof)
                    #%bc_idx = (bc_idx + 1) % len(self.background_colors)

        bc_idx = 0
        for idx, prof_coll in enumerate(self.prof_collections):
            # Draw all highlighted members that aren't the active one.
            if idx != self.pc_idx and (prof_coll.getCurrentDate() == cur_dt or self.all_observed):
                prof = prof_coll.getHighlightedProf()
                self.draw_ensemble_point(qp, prof)
                #bc_idx = (bc_idx + 1) % len(self.background_colors)

    def draw_ensemble_point(self, qp, prof):
        # Plot the profile index on the scatter plot
        if 'pbl_h' not in dir(prof): # Make sure a PBL top has been found in the profile object
            ppbl_top = params.pbl_top(prof)
            setattr(prof, 'pbl_h', interp.to_agl(prof, interp.hght(prof, ppbl_top)))
        if 'sfcpcl' not in dir(prof): # Make sure a surface parcel has been lifted in the profile object
            setattr(prof, 'sfcpcl', params.parcelx(prof, flag=1 ))
        #x = self.x_to_xpix()
        #y = self.y_to_ypix()
        color = QtCore.Qt.red
        qp.setPen(QtGui.QPen(color))
        qp.setBrush(QtGui.QBrush(color))
        x = self.x_to_xpix(prof.pbl_h) - 50 / 2.
        y = self.y_to_ypix(prof.sfcpcl.bplus) - (self.fsize-1) / 2
        qp.drawEllipse(x, y, 3, 3)

        return


class DrawTest(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(DrawTest, self).__init__(parent)
        # x = np.asarray([1,2,3,4])
        # y = np.asarray([2,2,3,4])
        length = 10
        x = np.random.rand(length) + np.random.randint(0, 10, length)
        y = np.random.rand(length) + np.random.randint(0, 10, length)
        x = np.asarray([0, 5, 10, 0], dtype=float)
        y = np.asarray([0, 5, 10, 20], dtype=float)
        self.frame = plotENS()
        self.frame.addProfileCollection(prof_coll)

        self.frame.setActiveCollection(0)
        self.setCentralWidget(self.frame)

if __name__ == "__main__":
    import sys
    import sharppy.io.buf_decoder as buf_decoder
    path = 'ftp://ftp.meteo.psu.edu/pub/bufkit/SREF/21/sref_oun.buf'
    dec  = buf_decoder.BufDecoder(path)
    prof_coll = dec._parse()
    app = QtGui.QApplication(sys.argv)
    mySW = DrawTest()
    mySW.show()
    sys.exit(app.exec_())
