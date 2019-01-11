import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import platform

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundFire', 'plotFire']

class backgroundFire(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundFire, self).__init__()
        self.init_hght = self.size().height()
        #print(self.init_hght)
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
        font_ratio = fsize/self.hgt
        font_ratio = 0.0512
        self.label_font = QtGui.QFont('Helvetica', round(font_ratio * self.hgt))
        self.fosberg_font = QtGui.QFont('Helvetica', round(font_ratio * self.hgt) + 2)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.fosberg_metrics = QtGui.QFontMetrics( self.fosberg_font )
        self.label_height = self.label_metrics.xHeight() + self.tpad
        self.ylast = self.label_height
        if platform.system() == "Windows":
            self.os_mod = self.label_metrics.descent()

        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.fosberg_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(0, self.tpad, self.wid, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fire Weather Parameters')
        self.labels = 2 * self.label_height + self.tpad + self.os_mod # Beginning of next line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        sep = 2
        y1 = self.labels + 4

        qp.setFont(self.label_font)
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
            y1 += self.label_height + sep + self.os_mod

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
            y1 += self.label_height + sep + self.os_mod
        
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine( 0, y1 + 3, self.brx, y1 + 3 )
        
        self.start_data_y1 = y1+3
        y1 = y1 + 3
        color = QtGui.QColor('#FF6633') 
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        self.moswindsep = 7
        label = ['', '','','','','','Derived Indices']
        for i in label: 
            rect1 = QtCore.QRect(0, y1, self.brx, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, i)
            y1 += self.label_height + self.moswindsep + self.os_mod
        qp.drawLine( 0, y1, self.brx, y1 )
        
        self.fosberg_y1 = y1+self.moswindsep
        self.fosberg_x = 0
        self.fosberg_width = self.brx
        
        self.haines_y1 = self.fosberg_y1 + self.moswindsep + self.os_mod + self.label_height
        self.haines_x = 0
        self.haines_width = self.brx
        """
        label = ['','','','','','Derived Indices']
        for i in label: 
            rect1 = QtCore.QRect(0, y1, self.brx, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, i)
            y1 += self.label_height + self.moswindsep + self.os_mod
        qp.drawLine( 0, y1, self.brx, y1 )
        
        self.fosberg_y1 = y1+self.moswindsep
        self.fosberg_x = 0
        self.fosberg_width = self.brx
        """

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
    def __init__(self):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')

        super(plotFire, self).__init__()
        self.prof = None

    def setProf(self, prof):
        self.prof = prof;

        # Fire indices
        self.fosberg = prof.fosberg
        self.haines_hght = prof.haines_hght
        self.haines_index = [prof.haines_low, prof.haines_mid, prof.haines_high]
        self.sfc_rh = prof.sfc_rh
        self.rh01km = prof.rh01km
        self.pblrh = prof.pblrh
        self.pbl_h = prof.pbl_h
        self.meanwind01km = tab.utils.comp2vec(prof.meanwind01km[0], prof.meanwind01km[1])
        self.meanwindpbl = tab.utils.comp2vec(prof.meanwindpbl[0], prof.meanwindpbl[1])
        self.sfc_wind = (prof.wdir[prof.get_sfc()], prof.wspd[prof.get_sfc()])
        self.pwat = prof.pwat
        if not tab.utils.QC(prof.pblmaxwind[0]):
            self.maxwindpbl = [np.ma.masked, np.ma.masked]
        else:
            self.maxwindpbl = tab.utils.comp2vec(prof.pblmaxwind[0], prof.pblmaxwind[1])
        self.bplus_fire = prof.bplus_fire

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def mousePressEvent(self, e):
        '''
        Handles mouse click event to switch 
        Haines Index elevations
        '''
        pos = e.pos()
        if 0 <= pos.x() and pos.x() <= self.haines_width and self.haines_y1 <= pos.y() and pos.y() <= self.haines_y1 + self.label_height - self.os_mod:
            self.haines_hght += 1
            self.haines_hght %= 3
            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()
            self.parentWidget().setFocus()

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
        self.drawPBLchar(qp)
        self.drawFosberg(qp)
        self.drawHainesIndex(qp)
        qp.end()
    
    def drawFosberg(self, qp):
        color = self.getFosbergFormat()
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.fosberg_font)

        rect1 = QtCore.QRect(0, self.fosberg_y1, self.fosberg_width, self.label_height - self.os_mod)
        if self.fosberg == self.prof.missing:
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fosberg FWI = M')
        else:    
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Fosberg FWI = ' + tab.utils.INT2STR(self.fosberg))
 
    def drawHainesIndex(self, qp):
        haines_height_label = ['L', 'M', 'H']
        color = self.getHainesFormat()
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.fosberg_font)
        
        rect1 = QtCore.QRect(0, self.haines_y1, self.haines_width, self.label_height - self.os_mod)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Haines Index (' + haines_height_label[self.haines_hght] + ') = ' + tab.utils.INT2STR(self.haines_index[self.haines_hght]))
    
    def getHainesFormat(self):
        if self.haines_index[self.haines_hght] == 2:
            color = QtGui.QColor(DGREEN)
        elif self.haines_index[self.haines_hght] == 3:
            color = QtGui.QColor(GREEN)
        elif self.haines_index[self.haines_hght] == 4:
            color = QtGui.QColor(YELLOW)
        elif self.haines_index[self.haines_hght] == 5:
            color = QtGui.QColor(ORANGE)
        elif self.haines_index[self.haines_hght] == 6:
            color = QtGui.QColor(RED)
        else:
            color = QtGui.QColor(DGREEN)
        return color


    def getFosbergFormat(self):
        if (not tab.utils.QC(self.fosberg)) or self.fosberg < 30:
            color = QtGui.QColor(DBROWN)
        elif self.fosberg < 40:
            color = QtGui.QColor(LBROWN)
        elif self.fosberg < 50:
            color = QtGui.QColor(self.fg_color)
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
            color = QtGui.QColor(self.fg_color)
        elif int(self.maxwindpbl[1]) <= 40:
            color = QtGui.QColor(YELLOW)
        elif int(self.maxwindpbl[1]) <= 50:
            color = QtGui.QColor(RED)
        else:
             color = QtGui.QColor(MAGENTA)

        return color, fontsize            

    def drawPBLchar(self, qp):
        color = QtGui.QColor(self.fg_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)        
        label = ['SFC = ' + tab.utils.INT2STR(self.sfc_wind[0]) + '/' + tab.utils.INT2STR(self.sfc_wind[1]), \
                '0-1 km mean = ' + tab.utils.INT2STR(self.meanwind01km[0]) + '/' + tab.utils.INT2STR(self.meanwind01km[1]), \
                'BL mean = ' + tab.utils.INT2STR(self.meanwindpbl[0]) + '/' + tab.utils.INT2STR(self.meanwindpbl[1]), \
                'BL max = ' + tab.utils.INT2STR(self.maxwindpbl[0]) + '/' + tab.utils.INT2STR(self.maxwindpbl[1])]
        sep = self.moswindsep
        y1 = self.start_data_y1 + 6
        for i in range(len(label)):
            if i == 3:
                color, fontsize = self.getMaxWindFormat()
            else:
                color = QtGui.QColor(self.fg_color)
                fontsize = 10

            qp.setFont(self.label_font) 
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect1 = QtCore.QRect(self.llw_x, y1, self.llw_width, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, label[i])
            y1 += self.label_height + sep + self.os_mod

        label = ['SFC RH = ' + tab.utils.INT2STR(self.sfc_rh) + '%', \
                '0-1 km RH = ' + tab.utils.INT2STR(self.rh01km) + '%', \
                'BL mean RH = ' + tab.utils.INT2STR(self.pblrh) + '%', \
                'PW = ' + tab.utils.FLOAT2STR(self.pwat,2) + ' in']

        y1 = self.start_data_y1 + 6
        for i in range(len(label)): 
            if i == 0:
                color, fontsize = self.getSfcRHFormat()
            elif i == 1 or i == 2:
                color = QtGui.QColor(self.fg_color)
                fontsize = 10
            else:
                color, fontsize = self.getPWColor()

            qp.setFont(self.label_font) 
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect1 = QtCore.QRect(self.moist_x, y1, self.moist_width, self.label_height)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, label[i])
            y1 += self.label_height + sep + self.os_mod
 
        color = QtGui.QColor(self.fg_color)
        qp.setFont(self.label_font) 
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRect(0, y1, self.brx, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "PBL Height = " + tab.utils.FLOAT2STR(tab.utils.M2FT(self.pbl_h), 0) + 'ft / ' + tab.utils.FLOAT2STR(self.pbl_h, 0) + 'm')
        y1 += self.label_height + sep + self.os_mod


    def getPWColor(self):
        if self.pwat < 0.5 and self.bplus_fire > 50 and self.sfc_rh < 35:
            color = QtGui.QColor(RED)
            fontsize = 12
        else:
            color = QtGui.QColor(self.fg_color)
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
            color = QtGui.QColor(self.fg_color)
        elif self.sfc_rh <= 35:
            color = QtGui.QColor(LBROWN)
        else:
            color = QtGui.QColor(DBROWN)   
        return color, 12

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    tester = plotFire()
    tester.setGeometry(50,50,293,195)
    tester.show()        
    app_frame.exec_()
