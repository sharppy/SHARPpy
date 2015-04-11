import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.viz import drawBarb
from sharppy.sharptab.constants import *
import platform

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundKinematics', 'plotKinematics']

class backgroundKinematics(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundKinematics, self).__init__()
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
        self.tpad = 5; self.bpad = 5

        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt

        fsize = np.floor(.06 * self.hgt)
        self.tpad = np.floor(.03 * self.hgt)

        self.label_font = QtGui.QFont('Helvetica')
        self.label_font.setPixelSize(fsize)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.label_height = self.label_metrics.xHeight() + self.tpad
        self.ylast = self.label_height
        self.barby = 0
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
        qp.setFont(self.label_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(x1*2.5, 3, x1, self.label_height)
        rect2 = QtCore.QRect(x1*5, 3, x1, self.label_height)
        rect3 = QtCore.QRect(x1*7, 3, x1, self.label_height)
        rect4 = QtCore.QRect(x1*9-self.rpad, 3, x1, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SRH (m2/s2)')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Shear (kt)')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'MnWind')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SRW')
        ## left column
        ## first block
        texts = ['SFC-1km', 'SFC-3km', 'Eff Inflow Layer',]
        for text in texts:
            rect = QtCore.QRect(self.lpad, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.ylast = y1
        ## second block
        texts = ['SFC-6km', 'SFC-8km','LCL-EL (Cloud Layer)', 'Eff Shear (EBWD)']
        y1 = self.ylast + self.tpad
        for text in texts:
            rect = QtCore.QRect(self.lpad, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.ylast = y1
        ## third block
        texts = ['BRN Shear = ', '4-6km SR Wind = ']
        y1 = self.ylast + self.tpad
        for text in texts:
            rect = QtCore.QRect(self.lpad, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.ylast = y1
        ## fourth block
        texts = ['...Storm Motion Vectors...', 'Bunkers Right = ', 'Bunkers Left = ', 'Corfidi Downshear = ', 'Corfidi Upshear = ']
        y1 = self.ylast + self.tpad
        self.barby = y1 + self.tpad
        for text in texts:
            rect = QtCore.QRect(self.lpad, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.ylast = vspace

        ## draw lines seperating the indices
        qp.drawLine( 0, self.ylast+3, self.brx, self.ylast+3 )
    
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


class plotKinematics(backgroundKinematics):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        super(plotKinematics, self).__init__()
        self.prof = prof;
        self.srh1km = prof.srh1km
        self.srh3km = prof.srh3km
        self.esrh = prof.right_esrh
        
        self.mean_1km = prof.mean_1km
        self.mean_3km = prof.mean_3km
        self.mean_6km = prof.mean_6km
        self.mean_8km = prof.mean_8km
        self.mean_lcl_el = prof.mean_lcl_el
        mean_eff = prof.mean_eff
        mean_ebw = prof.mean_ebw
        
        self.srw_1km = prof.srw_1km
        self.srw_3km = prof.srw_3km
        self.srw_6km = prof.srw_6km
        self.srw_8km = prof.srw_8km
        self.srw_lcl_el = prof.srw_lcl_el
        self.srw_4_5km = prof.srw_4_5km
        srw_eff = prof.srw_eff
        srw_ebw = prof.srw_ebw
        
        self.sfc_1km_shear = prof.sfc_1km_shear
        self.sfc_3km_shear = prof.sfc_3km_shear
        self.sfc_6km_shear = prof.sfc_6km_shear
        self.sfc_8km_shear = prof.sfc_8km_shear
        self.lcl_el_shear = prof.lcl_el_shear
        self.eff_shear = prof.eff_shear
        self.ebwd = prof.ebwd
        
        if prof.etop is np.ma.masked or prof.ebottom is np.ma.masked:
            self.mean_eff = [np.ma.masked, np.ma.masked]
            self.mean_ebw = [np.ma.masked, np.ma.masked]
            self.srw_eff = [np.ma.masked, np.ma.masked]
            self.srw_ebw = [np.ma.masked, np.ma.masked]
        else:
            self.mean_eff = tab.utils.comp2vec(mean_eff[0], mean_eff[1])
            self.mean_ebw = tab.utils.comp2vec(mean_ebw[0], mean_ebw[1])
            self.srw_eff = tab.utils.comp2vec(srw_eff[0], srw_eff[1])
            self.srw_ebw = tab.utils.comp2vec(srw_ebw[0], srw_ebw[1])
        
        self.brn_shear = prof.mupcl.brnshear
        self.bunkers_right_vec = tab.utils.comp2vec(prof.srwind[0], prof.srwind[1])
        self.bunkers_left_vec = tab.utils.comp2vec(prof.srwind[2], prof.srwind[3])
        self.upshear = tab.utils.comp2vec(prof.upshear_downshear[0],prof.upshear_downshear[1])
        self.downshear = tab.utils.comp2vec(prof.upshear_downshear[2],prof.upshear_downshear[3])

    def setProf(self, prof):
        self.ylast = self.label_height

        self.prof = prof;
        self.srh1km = prof.srh1km
        self.srh3km = prof.srh3km
        self.esrh = prof.right_esrh

        self.mean_1km = prof.mean_1km
        self.mean_3km = prof.mean_3km
        self.mean_6km = prof.mean_6km
        self.mean_8km = prof.mean_8km
        self.mean_lcl_el = prof.mean_lcl_el
        mean_eff = prof.mean_eff
        mean_ebw = prof.mean_ebw

        self.srw_1km = prof.srw_1km
        self.srw_3km = prof.srw_3km
        self.srw_6km = prof.srw_6km
        self.srw_8km = prof.srw_8km
        self.srw_lcl_el = prof.srw_lcl_el
        self.srw_4_5km = prof.srw_4_5km
        srw_eff = prof.srw_eff
        srw_ebw = prof.srw_ebw

        self.sfc_1km_shear = prof.sfc_1km_shear
        self.sfc_3km_shear = prof.sfc_3km_shear
        self.sfc_6km_shear = prof.sfc_6km_shear
        self.sfc_8km_shear = prof.sfc_8km_shear
        self.lcl_el_shear = prof.lcl_el_shear
        self.eff_shear = prof.eff_shear
        self.ebwd = prof.ebwd

        if prof.etop is np.ma.masked or prof.ebottom is np.ma.masked:
            self.mean_eff = [np.ma.masked, np.ma.masked]
            self.mean_ebw = [np.ma.masked, np.ma.masked]
            self.srw_eff = [np.ma.masked, np.ma.masked]
            self.srw_ebw = [np.ma.masked, np.ma.masked]
        else:
            self.mean_eff = tab.utils.comp2vec(mean_eff[0], mean_eff[1])
            self.mean_ebw = tab.utils.comp2vec(mean_ebw[0], mean_ebw[1])
            self.srw_eff = tab.utils.comp2vec(srw_eff[0], srw_eff[1])
            self.srw_ebw = tab.utils.comp2vec(srw_ebw[0], srw_ebw[1])

        self.brn_shear = prof.mupcl.brnshear
        self.bunkers_right_vec = tab.utils.comp2vec(prof.srwind[0], prof.srwind[1])
        self.bunkers_left_vec = tab.utils.comp2vec(prof.srwind[2], prof.srwind[3])
        self.upshear = tab.utils.comp2vec(prof.upshear_downshear[0],prof.upshear_downshear[1])
        self.downshear = tab.utils.comp2vec(prof.upshear_downshear[2],prof.upshear_downshear[3])

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotKinematics, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotKinematics, self).paintEvent(e)
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
        self.drawKinematics(qp)
        self.drawBarbs(qp)
        qp.end()
    
    def drawBarbs(self, qp):
        x1 = self.brx / 10
        y1 = self.bry / 19
        origin_x = x1*8.
        pen = QtGui.QPen(QtGui.QColor('#0A74C6'), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect0 = QtCore.QRect(x1*7, self.ylast + self.tpad, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '1km & 6km AGL\nWind Barbs' )
        drawBarb(qp, origin_x, self.barby, self.prof.wind1km[0], self.prof.wind1km[1], color='#AA0000')
        drawBarb(qp, origin_x, self.barby, self.prof.wind6km[0], self.prof.wind6km[1], color='#0A74C6')
    
    
    def drawKinematics(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen to draw with.
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad
        ## format the text
        srh1km = str(np.int(self.srh1km[0]))
        srh3km = str(np.int(self.srh3km[0]))
        
        sfc1km = tab.utils.INT2STR(tab.utils.mag(self.sfc_1km_shear[0], self.sfc_1km_shear[1]))
        sfc3km = tab.utils.INT2STR(tab.utils.mag(self.sfc_3km_shear[0], self.sfc_3km_shear[1]))
        sfc6km = tab.utils.INT2STR(tab.utils.mag(self.sfc_6km_shear[0], self.sfc_6km_shear[1]))
        sfc8km = tab.utils.INT2STR(tab.utils.mag(self.sfc_8km_shear[0], self.sfc_8km_shear[1]))
        lcl_el = tab.utils.INT2STR(tab.utils.mag(self.lcl_el_shear[0], self.lcl_el_shear[1]))
        
        mean_1km = tab.utils.INT2STR(self.mean_1km[0]) + '/' + tab.utils.INT2STR(self.mean_1km[1])
        mean_3km = tab.utils.INT2STR(self.mean_3km[0]) + '/' + tab.utils.INT2STR(self.mean_3km[1])
        mean_6km = tab.utils.INT2STR(self.mean_6km[0]) + '/' + tab.utils.INT2STR(self.mean_6km[1])
        mean_8km = tab.utils.INT2STR(self.mean_8km[0]) + '/' + tab.utils.INT2STR(self.mean_8km[1])
        mean_lcl_el = tab.utils.INT2STR(self.mean_lcl_el[0]) + '/' + tab.utils.INT2STR(self.mean_lcl_el[1])
        
        srw_1km = tab.utils.INT2STR(self.srw_1km[0]) + '/' + tab.utils.INT2STR(self.srw_1km[1])
        srw_3km = tab.utils.INT2STR(self.srw_3km[0]) + '/' + tab.utils.INT2STR(self.srw_3km[1])
        srw_6km = tab.utils.INT2STR(self.srw_6km[0]) + '/' + tab.utils.INT2STR(self.srw_6km[1])
        srw_8km = tab.utils.INT2STR(self.srw_8km[0]) + '/' + tab.utils.INT2STR(self.srw_8km[1])
        srw_lcl_el = tab.utils.INT2STR(self.srw_lcl_el[0]) + '/' + tab.utils.INT2STR(self.srw_lcl_el[1])
        srw_4_5km = tab.utils.INT2STR(self.srw_4_5km[0]) + '/' + tab.utils.INT2STR(self.srw_4_5km[1]) + ' kt'
        
        esrh = tab.utils.INT2STR(self.esrh[0])
        eff_lr = tab.utils.INT2STR(tab.utils.mag(self.eff_shear[0], self.eff_shear[1]))
        efbwd = tab.utils.INT2STR(tab.utils.mag(self.ebwd[0], self.ebwd[1]))
        mean_eff = tab.utils.INT2STR(self.mean_eff[0]) + '/' + tab.utils.INT2STR(self.mean_eff[1])
        mean_ebw = tab.utils.INT2STR(self.mean_ebw[0]) + '/' + tab.utils.INT2STR(self.mean_ebw[1])
        srw_eff = tab.utils.INT2STR(self.srw_eff[0]) + '/' + tab.utils.INT2STR(self.srw_eff[1])
        srw_ebw = tab.utils.INT2STR(self.srw_ebw[0]) + '/' + tab.utils.INT2STR(self.srw_ebw[1])
        
        brn_shear = tab.utils.INT2STR(self.brn_shear) + ' m2/s2'
        bunkers_left = tab.utils.INT2STR(self.bunkers_left_vec[0]) + '/' + tab.utils.INT2STR(self.bunkers_left_vec[1]) + ' kt'
        bunkers_right = tab.utils.INT2STR(self.bunkers_right_vec[0]) + '/' + tab.utils.INT2STR(self.bunkers_right_vec[1]) + ' kt'
        upshear = tab.utils.INT2STR(self.upshear[0]) + '/' + tab.utils.INT2STR(self.upshear[1]) + ' kt'
        downshear = tab.utils.INT2STR(self.downshear[0]) + '/' + tab.utils.INT2STR(self.downshear[1]) + ' kt'
        
        ## sfc-1km
        texts = [srh1km, sfc1km, mean_1km, srw_1km]
        count = 3
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## sfc-3km
        texts = [srh3km, sfc3km, mean_3km, srw_3km]
        count = 3
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## Effective Inflow Layer
        texts = [esrh, eff_lr, mean_eff, srw_eff]
        count = 3
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height + self.tpad
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## sfc-6km
        texts = [sfc6km, mean_6km, srw_6km]
        count = 5
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## sfc-8km
        texts = [sfc8km, mean_8km, srw_8km]
        count = 5
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## LCL-EL
        texts = [lcl_el, mean_lcl_el, srw_lcl_el]
        count = 5
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## Effective Shear
        texts = [efbwd, mean_ebw, srw_ebw]
        count = 5
        for text in texts:
            rect = QtCore.QRect(x1*count, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            count += 2
        vspace = self.label_height + self.tpad
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        self.ylast = y1
        ## BRN Shear and 4-6km SR Wind
        texts = [brn_shear, srw_4_5km]
        for text in texts:
            rect = QtCore.QRect(x1*5, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            vspace = self.label_height + self.tpad
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        self.ylast = y1
        vspace = self.label_height + self.tpad
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        y1 += vspace
        ## bunkers motion
        texts = [bunkers_right, bunkers_left]
        colors =[QtGui.QColor('#0099CC'), QtGui.QColor('#FF6666')]
        for text, color in zip(texts, colors):
            rect = QtCore.QRect(x1*5, y1, x1, self.label_height)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.ylast = y1
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## upshear and downshear vectors
        texts = [downshear, upshear]
        for text in texts:
            rect = QtCore.QRect(x1*5, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

