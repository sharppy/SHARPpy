import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import platform

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundWinter', 'plotWinter']

class backgroundWinter(QtWidgets.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundWinter, self).__init__()
        self.initUI()

    def initUI(self):
        ## initialize fram variables such as size,
        ## padding, etc.
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        self.lpad = 5; self.rpad = 5
        self.tpad = 3; self.bpad = 3
        self.os_mod = 0
        self.barby = 0
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt

        if self.physicalDpiX() > 75:
            fsize = 8
        else:
            fsize = 10
        self.font_ratio = 0.0512
        self.label_font = QtGui.QFont('Helvetica', round(self.hgt * self.font_ratio))
        self.label_metrics = QtGui.QFontMetrics( self.label_font )

        if platform.system() == "Windows":
            self.os_mod = self.label_metrics.descent()

        self.label_height = self.label_metrics.xHeight() + self.tpad
        self.ylast = self.label_height

        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()

    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(self.dgz_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(0, self.tpad, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '*** DENDRITIC GROWTH ZONE (-12 TO -17 C) ***')
        self.oprh_y1 = 2*self.label_height+self.tpad
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        sep = 5
        y1 = 3 * self.label_height + self.tpad + sep + self.os_mod
        self.layers_y1 = y1

        label = ['', '', '']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        y1 = 3 * (self.label_height + self.os_mod) + self.tpad + sep + self.label_height + sep + self.os_mod
        begin = y1
        label = ['', '']
        for i in label:
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        qp.drawLine( 0, y1, self.brx, y1 )
        qp.drawLine( self.brx* .48, y1, self.brx*.48, begin )
        y1 = y1+3

        self.init_phase_y1 = y1

        label = ['']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod
        qp.drawLine( 0, y1, self.brx, y1 )

        y1 = y1+3
        backup = y1
        label = ['','', '', '']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        y1 = backup
        label = ['','', '', '']
        for i in label:
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        self.energy_y1 = backup
        qp.drawLine( 0, y1 + 0, self.brx, y1 + 0)
        qp.drawLine( self.brx* .48, y1 + 0, self.brx*.48, backup )
        y1 += 4
        rect1 = QtCore.QRect(0, y1, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '*** BEST GUESS PRECIP TYPE ***')
        self.precip_type_y1 = y1 + self.label_height + 3 + 2 * self.os_mod
        self.ptype_tmpf_y1 = self.precip_type_y1 + self.label_height + 8 + 2 * self.os_mod

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


class plotWinter(backgroundWinter):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.dgz_color = QtGui.QColor('#ffff00')

        super(plotWinter, self).__init__()
        self.prof = None

    def setProf(self, prof):
        self.prof = prof;

        # DGZ data
        self.dgz_pbot = prof.dgz_pbot
        self.dgz_ptop = prof.dgz_ptop
        self.dgz_zbot = tab.utils.M2FT(tab.interp.hght(prof, self.dgz_pbot))
        self.dgz_ztop = tab.utils.M2FT(tab.interp.hght(prof, self.dgz_ptop))
        self.dgz_depth = self.dgz_ztop - self.dgz_zbot
        self.oprh = prof.oprh
        self.dgz_meanrh = prof.dgz_meanrh
        self.dgz_pw = prof.dgz_pw
        self.dgz_meanq = prof.dgz_meanq
        self.dgz_meanomeg = prof.dgz_meanomeg

        # Inital Phase Types
        self.plevel = prof.plevel
        self.init_phase = prof.phase
        self.init_tmp = prof.tmp
        self.init_st = prof.st

        # TEMP Energy
        self.tpos = prof.tpos
        self.tneg = prof.tneg
        self.ttop = prof.ttop
        self.tbot = prof.tbot

        # WETBULB Energy
        self.wpos = prof.wpos
        self.wneg = prof.wneg
        self.wtop = prof.wtop
        self.wbot = prof.wbot

        # PRECIP TYPE
        self.precip_type = prof.precip_type

        # PRECIP TYPE SFC TEMPERATURE
        self.ptype_tmpf = tab.thermo.ctof(prof.tmpc[prof.get_sfc()])
        self.ptype_tmpf_string = "Based on SFC Temperature of %.2f F" % self.ptype_tmpf

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])
        self.dgz_color = QtGui.QColor(prefs['winter_dgz_color'])

        if update_gui:
            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotWinter, self).resizeEvent(e)
        self.plotData()

    def paintEvent(self, e):
        super(plotWinter, self).paintEvent(e)
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
        Handles the drawing of the text on the frame.
        '''
        if self.prof is None:
            return

        x1 = self.brx / 10
        y1 = self.bry / 19
        origin_x = x1*8.5
        origin_y = y1*15

        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the indices
        self.drawPrecipType(qp)
        self.drawPrecipTypeTemp(qp)
        self.drawOPRH(qp)
        self.drawInitial(qp)
        self.drawDGZLayer(qp)
        self.drawWCLayer(qp)
        qp.end()

    def drawOPRH(self, qp):
        if self.oprh < -.1 and tab.utils.QC(self.oprh) and self.dgz_meanomeg != -99990.0:
            pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect1 = QtCore.QRect(0, self.oprh_y1, self.wid, self.label_height)
        if self.dgz_meanomeg == -99990.0:
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'OPRH (Omega*PW*RH): N/A')
        else:
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'OPRH (Omega*PW*RH): ' + tab.utils.FLOAT2STR(self.oprh,2))

    def drawPrecipType(self, qp):
        big = QtGui.QFont('Helvetica', round(self.hgt * self.font_ratio) + 5)
        big_metrics = QtGui.QFontMetrics( big )
        height = big_metrics.xHeight() + self.tpad
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(big)
        rect1 = QtCore.QRect(0, self.precip_type_y1, self.wid, height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, self.precip_type)

    def drawPrecipTypeTemp(self, qp):
        small = QtGui.QFont('Helvetica', round(self.hgt * self.font_ratio) -1)
        small_metrics = QtGui.QFontMetrics( small )
        height = small_metrics.xHeight() + self.tpad
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(small)
        rect1 = QtCore.QRect(0, self.ptype_tmpf_y1, self.wid, height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, self.ptype_tmpf_string)

    def drawWCLayer(self, qp):
        sep = 5
        # Temperature Profile Stuff
        y1 = self.energy_y1
        x = self.lpad
        if self.tpos > 0 and self.tneg < 0:
            string = 'P/N: ' + str(round(self.tpos,0)) + ' / ' + str(round(self.tneg,0)) + ' J/kg'
            label = ['TEMPERATURE PROFILE', \
                     string, \
                     'Melt Lyr: ' + str(int(self.ttop)) + '-' + str(int(self.tbot)) + ' mb', \
                     'Frz Lyr: ' + str(int(self.tbot)) + '-' + str(int(self.prof.pres[self.prof.sfc])) + ' mb']
        else:
            label = ['TEMPERATURE PROFILE', '', 'Warm/Cold layers not found.', '']

        for i in label:
            rect1 = QtCore.QRect(x, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        # Wetbulb Profile stuff
        y1 = self.energy_y1
        x = self.brx/2 + 2
        if self.wpos > 0 and self.wneg < 0:
            string = 'P/N: ' + str(round(self.wpos,0)) + ' / ' + str(round(self.wneg,0)) + ' J/kg'
            label = ['WETBULB PROFILE', \
                     string, \
                     'Melt Lyr: ' + str(int(self.wtop)) + '-' + str(int(self.wbot)) + ' mb', \
                     'Frz Lyr: ' + str(int(self.wbot)) + '-' + str(int(self.prof.pres[self.prof.sfc])) + ' mb']
        else:
            label = ['WETBULB PROFILE', '', 'Warm/Cold layers not found.', '']

        for i in label:
            rect1 = QtCore.QRect(x, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

    def drawDGZLayer(self, qp):
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        sep = 5
        y1 = self.layers_y1
        label = ['Layer Depth: ' + tab.utils.INT2STR(self.dgz_depth) + " ft (" + tab.utils.INT2STR(self.dgz_zbot) + '-' +\
                 tab.utils.INT2STR(self.dgz_ztop) + ' ft msl)',\
                 'Mean Layer RH: ' + tab.utils.FLOAT2STR(self.dgz_meanrh,0) + ' %',\
                 'Mean Layer PW: ' + tab.utils.FLOAT2STR(self.dgz_pw,1) + ' in']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod

        y1 = self.layers_y1 + self.label_height + sep + self.os_mod
        if self.dgz_meanomeg == 10*self.prof.missing:
            omeg = 'N/A'
        else:
            omeg = tab.utils.FLOAT2STR(self.dgz_meanomeg,1) + ' ub/s'
        label = ['Mean Layer MixRat: ' + tab.utils.FLOAT2STR(self.dgz_meanq,1) + ' g/kg', \
                 'Mean Layer Omega: ' + omeg]
        for i in label:
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height + sep + self.os_mod


    def drawInitial(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect1 = QtCore.QRect(self.lpad, self.init_phase_y1,  self.wid/10, self.label_height)
        if self.plevel > 100:
            hght = tab.utils.M2FT(tab.interp.hght(self.prof, self.plevel))
            string = "Inital Phase: " + self.init_st + ' from: ' + tab.utils.INT2STR(self.plevel) + ' mb (' + tab.utils.INT2STR(hght) + ' ft msl; ' + tab.utils.FLOAT2STR(self.init_tmp,1) + ' C)'
        else:
            string = "Initial Phase:  No Precipitation layers found."
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, string)

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])
    tester = plotWinter()
    tester.show()
    app_frame.exec_()
