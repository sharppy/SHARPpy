import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundFire', 'plotFire']

class backgroundFire(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundFire, self).__init__()
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
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(QtGui.QFont('Helvetica', 12))
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(0, self.tpad, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fire Weather Parameters')
        self.labels = 2*self.label_height+self.tpad # Beginning of next line
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        sep = 2
        y1 = self.labels + 4
       
        color = QtGui.QColor('#00CC33')
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        label = ['Moisture']
        begin = y1
        self.moist_x = self.brx/10
        self.moist_width = self.brx/2 - self.brx/10
        for i in label:
            rect1 = QtCore.QRect(self.brx/10, y1, self.brx/2 - self.brx/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, i)
            y1 += self.label_height+sep

        color = QtGui.QColor('#0066CC') 
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        label = ['Low-Level Wind']
        self.llw_x = self.brx/2
        self.llw_width = self.brx/2 - self.brx/10
        y1 = begin
        for i in label: 
            rect1 = QtCore.QRect(self.brx/2, y1, self.brx/2 - self.brx/10, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, i)
            y1 += self.label_height+sep
        
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine( 0, y1 + 3, self.brx, y1 + 3 )
        
        self.start_data_y1 = y1+3
        y1 = y1 + 3
        color = QtGui.QColor('#FF6633') 
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        self.moswindsep = 7
        label = ['','','','','','Derived Indices']
        for i in label: 
            rect1 = QtCore.QRect(0, y1, self.brx, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, i)
            y1 += self.label_height+self.moswindsep
        qp.drawLine( 0, y1, self.brx, y1 )
        
        self.fosberg_y1 = y1+self.moswindsep
        self.fosberg_x = 0
        self.fosberg_width = self.brx

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


class plotFire(backgroundFire):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        super(plotFire, self).__init__()
        self.prof = prof;
        
        # Fire indices
        self.fosberg = prof.fosberg
        self.sfc_rh = prof.sfc_rh
        self.rh01km = prof.rh01km
        self.pblrh = prof.pblrh
        self.meanwind01km = tab.utils.comp2vec(prof.meanwind01km[0], prof.meanwind01km[1])
        self.meanwindpbl = tab.utils.comp2vec(prof.meanwindpbl[0], prof.meanwindpbl[1])
        self.sfc_wind = (prof.wdir[prof.get_sfc()], prof.wspd[prof.get_sfc()])
        self.pwat = prof.pwat
        if not tab.utils.QC(prof.pblmaxwind[0]):
            self.maxwindpbl = [np.ma.masked, np.ma.masked]
        else:
            self.maxwindpbl = tab.utils.comp2vec(prof.pblmaxwind[0], prof.pblmaxwind[1])
        self.bplus_fire = prof.bplus_fire

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotFire, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotFire, self).paintEvent(e)
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
        self.drawPBLchar(qp)
        self.drawFosberg(qp)
        qp.end()
    
    def drawFosberg(self, qp):
        color = self.getFosbergFormat()
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(QtGui.QFont('Helvetica', 12))

        rect1 = QtCore.QRect(0, self.fosberg_y1, self.fosberg_width, self.label_height)
        if self.fosberg == self.prof.missing:
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fosberg FWI = M')
        else:    
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fosberg FWI = ' + tab.utils.INT2STR(self.fosberg))

    def getFosbergFormat(self):
        if tab.utils.QC(self.fosberg) or self.fosberg < 30:
            color = QtGui.QColor(DBROWN)
        elif self.fosberg < 40:
            color = QtGui.QColor(LBROWN)
        elif self.fosberg < 50:
            color = QtGui.QColor(WHITE)
        elif self.fosberg < 60:
            color = QtGui.QColor(YELLOW)
        elif self.fosberg < 70:
            color = QtGui.QColor(RED)
        else:
            color = QtGui.QColor(MAGENTA)        

        return color

    def getMaxWindFormat(self):
        fontsize = 12
        if (not tab.utils.QC(self.maxwindpbl[1])) or int(self.maxwindpbl[1]) <= 10:
            color = QtGui.QColor(DBROWN)
        elif int(self.maxwindpbl[1]) <= 20:
            color = QtGui.QColor(LBROWN)
        elif int(self.maxwindpbl[1]) <= 30:
            color = QtGui.QColor(WHITE)
        elif int(self.maxwindpbl[1]) <= 40:
            color = QtGui.QColor(YELLOW)
        elif int(self.maxwindpbl[1]) <= 50:
            color = QtGui.QColor(RED)
        else:
             color = QtGui.QColor(MAGENTA)

        return color, fontsize            

    def drawPBLchar(self, qp):
        color = QtGui.QColor(WHITE)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(QtGui.QFont('Helvetica', 10))        
        
        label = ['SFC = ' + tab.utils.INT2STR(self.sfc_wind[0]) + '/' + tab.utils.INT2STR(self.sfc_wind[1]), \
                '0-1 km mean = ' + tab.utils.INT2STR(self.meanwind01km[0]) + '/' + tab.utils.INT2STR(self.meanwind01km[1]), \
                'BL mean = ' + tab.utils.INT2STR(self.meanwindpbl[0]) + '/' + tab.utils.INT2STR(self.meanwindpbl[1]), \
                'BL max = ' + tab.utils.INT2STR(self.maxwindpbl[0]) + '/' + tab.utils.INT2STR(self.maxwindpbl[1])]
        sep = self.moswindsep
        y1 = self.start_data_y1 + 6
        for i in xrange(len(label)):
            if i == 3:
                color, fontsize = self.getMaxWindFormat()
            else:
                color = QtGui.QColor(WHITE)
                fontsize = 10

            qp.setFont(QtGui.QFont('Helvetica', fontsize)) 
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect1 = QtCore.QRect(self.llw_x, y1, self.llw_width, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, label[i])
            y1 = y1 + self.label_height + sep

        label = ['SFC RH = ' + tab.utils.INT2STR(self.sfc_rh) + '%', \
                '0-1 km RH = ' + tab.utils.INT2STR(self.rh01km) + '%', \
                'BL mean RH = ' + tab.utils.INT2STR(self.pblrh) + '%', \
                'PW = ' + tab.utils.FLOAT2STR(self.pwat,2) + ' in']

        y1 = self.start_data_y1 + 6
        for i in xrange(len(label)): 
            if i == 0:
                color, fontsize = self.getSfcRHFormat()
            elif i == 1 or i == 2:
                color = QtGui.QColor(WHITE)
                fontsize = 10
            else:
                color, fontsize = self.getPWColor()

            qp.setFont(QtGui.QFont('Helvetica', fontsize)) 
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect1 = QtCore.QRect(self.moist_x, y1, self.moist_width, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, label[i])
            y1 = y1 + self.label_height + sep


    def getPWColor(self):
        if self.pwat < 0.5 and self.bplus_fire > 50 and self.sfc_rh < 35:
            color = QtGui.QColor(RED)
            fontsize = 12
        else:
            color = QtGui.QColor(WHITE)
            fontsize = 10
        return color, fontsize


    def getSfcRHFormat(self):
        if self.sfc_rh <= 10:
            color = QtGui.QColor(MAGENTA)
        elif self.sfc_rh <= 15:
            color = QtGui.QColor(RED)
        elif self.sfc_rh <= 20:
            color = QtGui.QColor(YELLOW)
        elif self.sfc_rh <= 30:
            color = QtGui.QColor(WHITE)
        elif self.sfc_rh <= 35:
            color = QtGui.QColor(LBROWN)
        else:
            color = QtGui.QColor(DBROWN)   
        return color, 12




