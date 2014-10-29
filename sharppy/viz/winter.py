import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.viz import drawBarb
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundWinter', 'plotWinter']

class backgroundWinter(QtGui.QFrame):
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
        if self.physicalDpiX() > 75:
            fsize = 8
        else:
            fsize = 10
        self.label_font = QtGui.QFont('Helvetica', fsize)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.label_height = self.label_metrics.xHeight() + self.tpad
        self.ylast = self.label_height
        self.barby = 0
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
        pen = QtGui.QPen(QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(0, self.tpad, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '*** DENDRITIC GROWTH ZONE (-12 TO -17 C) ***')
        self.oprh_y1 = 2*self.label_height+self.tpad
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        sep = 5
        y1 = 3*self.label_height+self.tpad+sep
        self.layers_y1 = y1
        
        label = ['', '', '']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep

        y1 = 3*self.label_height+self.tpad+sep + self.label_height+sep
        begin = 3*self.label_height+self.tpad+sep + self.label_height+sep
        label = ['', '']
        for i in label: 
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep
        
        qp.drawLine( 0, y1, self.brx, y1 )
        qp.drawLine( self.brx* .48, y1, self.brx*.48, begin )
        y1 = y1+3
        
        self.init_phase_y1 = y1
       
        label = ['']
        for i in label: 
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep
        qp.drawLine( 0, y1, self.brx, y1 )
        
        y1 = y1+3
        backup = y1
        label = ['','', '', '']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep

        y1 = backup
        label = ['','', '', '']
        for i in label: 
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep
        
        self.energy_y1 = backup
        qp.drawLine( 0, y1+6, self.brx, y1 +6)
        qp.drawLine( self.brx* .48, y1+6, self.brx*.48, backup )
        y1 = y1 +10
        rect1 = QtCore.QRect(0, y1, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '*** BEST GUESS PRECIP TYPE ***')
        self.precip_type_y1 = y1 + self.label_height + 3
    
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
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        super(plotWinter, self).__init__()
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

    def plotData(self):
        '''
        Handles the drawing of the text on the frame.
        '''
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
        self.drawOPRH(qp)
        self.drawInitial(qp) 
        self.drawDGZLayer(qp)
        self.drawWCLayer(qp)
        qp.end()
    
    def drawOPRH(self, qp):
        pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect1 = QtCore.QRect(0, self.oprh_y1, self.wid, self.label_height)
        if self.dgz_meanomeg == self.prof.missing:
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'OPRH (Omega*PW*RH): N/A')
        else:    
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'OPRH (Omega*PW*RH): ' + str(round(self.oprh,2)))

    def drawPrecipType(self, qp):
        big = QtGui.QFont('Helvetica', 15, bold=True)
        big_metrics = QtGui.QFontMetrics( big )
        height = big_metrics.xHeight() + self.tpad
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(big)
        rect1 = QtCore.QRect(0, self.precip_type_y1, self.wid, height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, self.precip_type)

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
            y1 += self.label_height+sep

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
            y1 += self.label_height+sep

    def drawDGZLayer(self, qp):
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        sep = 5
        y1 = self.layers_y1
        label = ['Layer Depth: ' + str(int(self.dgz_depth)) + " ft (" + str(int(self.dgz_zbot)) + '-' +\
                 str(int(self.dgz_ztop)) + ' ft msl)',\
                 'Mean Layer RH: ' + str(round(self.dgz_meanrh,0)) + '%',\
                 'Mean Layer PW: ' + str(round(self.dgz_pw,0)) + 'in']
        for i in label:
            rect1 = QtCore.QRect(self.lpad, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep

        y1 = self.layers_y1 + self.label_height+sep
        if self.dgz_meanomeg == self.prof.missing:
            omeg = 'N/A'
        else:
            omeg = str(round(self.dgz_meanomeg,0)) + ' ub/s'
        label = ['Mean Layer MixRat: ' + str(round(self.dgz_meanq,1)) + 'g/kg', \
                 'Mean Layer Omega: ' + omeg]
        for i in label: 
            rect1 = QtCore.QRect(self.brx/2 + 2, y1, self.wid/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep


    def drawInitial(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect1 = QtCore.QRect(self.lpad, self.init_phase_y1,  self.wid/10, self.label_height)
        if self.plevel > 100: 
            hght = tab.utils.M2FT(tab.interp.hght(self.prof, self.plevel))
            string = "Inital Phase: " + self.init_st + ' from: ' + str(int(self.plevel)) + ' mb (' + str(int(hght)) + ' ft msl; ' + str(round(self.init_tmp,1)) + ' C)'
        else:
            string = "Initial Phase:  No Precipitation layers found."
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, string)


