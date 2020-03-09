import numpy as np
from qtpy import QtGui, QtCore, QtWidgets, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import platform

__all__ = ['backgroundAdvection', 'plotAdvection']
class backgroundAdvection(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundAdvection, self).__init__()
        self.initUI()

    def initUI(self):
        ## window configuration settings,
        ## such as padding, width, height, and
        ## min/max plot axes
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## set the max and min pressure expected, and convert it to log space
        self.pmax = 1050.; self.pmin = 100.
        self.log_pmax = np.log(self.pmax); self.log_pmin = np.log(self.pmin)
        self.adv_max = 13.; self.adv_min = -13.
        self.adv_min = 0

        self.font_ratio = 0.12
        fsize = round(self.size().width() * self.font_ratio) + 3
        self.label_font = QtGui.QFont('Helvetica', fsize)
        self.label_metrics = QtGui.QFontMetrics(self.label_font)
        self.os_mod = 0
        if platform.system() == "Windows":
            self.os_mod = self.label_metrics.descent()
            self.label_font = QtGui.QFont('Helvetica', fsize - self.os_mod)
            self.label_metrics = QtGui.QFontMetrics(self.label_font)

        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
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
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the background frame
        self.draw_frame(qp)
        ## draw the vertical ticks for wind speed
        self.draw_centerline(qp)
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setFont(self.label_font)
        qp.setPen(pen)
        qp.drawText(2,2,self.brx - 2,8*5, QtCore.Qt.AlignLeft | QtCore.Qt.TextWordWrap, 'Inf. Temp. Adv. (C/hr)')
        qp.end()

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the borders in white
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

    def draw_centerline(self, qp):
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        qp.drawLine(self.adv_to_pix(0), self.pres_to_pix(self.pmax), self.adv_to_pix(0), self.pres_to_pix(self.pmin))


    def pres_to_pix(self, p):
        '''
        Function to convert a pressure value to a Y pixel.
        '''
        scl1 = self.log_pmax - self.log_pmin
        scl2 = self.log_pmax - np.log(p)
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def adv_to_pix(self, a):
        '''
        Function to convert an advection value to a X pixel.
        '''
        half_line = (self.brx - self.rpad) / 2.
        scl1 = self.adv_max - self.adv_min
        scl2 = self.adv_max - a
        offset = self.brx - ((scl2 / scl1) * (self.brx - self.rpad))
        if a == 0:
            section = half_line
        else:
            section = offset/2 + half_line
        return section


class plotAdvection(backgroundAdvection):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')

        super(plotAdvection, self).__init__()
        self.prof = None

    def setProf(self, prof):

        self.prof = prof
        self.inf_temp_adv = prof.inf_temp_adv[0]
        self.pressure_bounds = prof.inf_temp_adv[1]

        self.clearData()
        self.plotBackground()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            self.clearData()
            self.plotBackground()
            self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotAdvection, self).resizeEvent(e)


    def paintEvent(self, e):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        super(plotAdvection, self).paintEvent(e)
        ## create a new painter obkect
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0,0, self.plotBitMap)
        self.plotData(qp)
        ## end the painter
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)

    def plotData(self, qp):
        if self.prof is None:
            return
        if self.prof.wdir.count() == 0:
            return
        for i in range(len(self.inf_temp_adv)):
            ptop = self.pressure_bounds[i][0]
            pbot = self.pressure_bounds[i][1]
            inf_temp_adv = self.inf_temp_adv[i]
            pix_ptop = self.pres_to_pix(ptop)
            pix_pbot = self.pres_to_pix(pbot)
            pix_adv = self.adv_to_pix(inf_temp_adv)
            qp.setFont(self.label_font)
            label_width = 5
            box_height = 8
            if tab.utils.QC(self.inf_temp_adv[i]) and not np.isnan(self.inf_temp_adv[i]):
                if self.inf_temp_adv[i] > 0:
                    pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
                    qp.setPen(pen)
                    label_loc = self.adv_to_pix(8) - label_width
                elif self.inf_temp_adv[i] < 0:
                    color = QtGui.QColor("#3399CC")
                    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
                    qp.setPen(pen)
                    label_loc = self.adv_to_pix(-8)
                else:
                    color = self.fg_color
                    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
                    qp.setPen(pen)
                    label_loc = self.adv_to_pix(8) - label_width
                rect = QtCore.QRect(label_loc, (pix_ptop + pix_pbot)/2, label_width, box_height)
                qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, str(round(inf_temp_adv,1)))
                qp.drawLine(pix_adv, pix_ptop, self.adv_to_pix(inf_temp_adv), pix_pbot)
                qp.drawLine(self.adv_to_pix(0), pix_pbot, pix_adv, pix_pbot)
                qp.drawLine(pix_adv, pix_ptop, self.adv_to_pix(0), pix_ptop)
                qp.drawLine(self.adv_to_pix(0), pix_ptop, self.adv_to_pix(0), pix_pbot)
        return


if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotAdvection()
    tester.show()    
    app_frame.exec_()
