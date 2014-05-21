import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.viz import drawBarb
from sharppy.sharptab.constants import *

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
        self.label_font = QtGui.QFont('Helvetica', 10)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.label_height = self.label_metrics.height()
        self.severe_font = QtGui.QFont('Helvetica', 12)
        self.severe_metrics = QtGui.QFontMetrics( self.severe_font )
        self.severe_height = self.severe_metrics.height()
        self.lpad = 5; self.rpad = 5
        self.tpad = 10; self.bpad = 5
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
        qp.setFont(self.label_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.bry / 19
        ## draw the header for the indices
        rect0 = QtCore.QRect(x1*1, 5, x1, self.label_height)
        rect1 = QtCore.QRect(x1*3, 5, x1, self.label_height)
        rect2 = QtCore.QRect(x1*5, 5, x1, self.label_height)
        rect3 = QtCore.QRect(x1*7, 5, x1, self.label_height)
        rect4 = QtCore.QRect(x1*9-self.rpad, 5, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SRH (m2/s2)')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'Shear (kt)')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'MnWind')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SRW')
        ## draw the column static text
        rect0 = QtCore.QRect(self.lpad, y1*1+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(self.lpad, y1*2+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(self.lpad, y1*3+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(self.lpad, y1*5+self.tpad, x1, self.label_height)
        rect4 = QtCore.QRect(self.lpad, y1*6+self.tpad, x1, self.label_height)
        rect5 = QtCore.QRect(self.lpad, y1*7+self.tpad, x1, self.label_height)
        rect6 = QtCore.QRect(self.lpad, y1*8+self.tpad, x1, self.label_height)
        rect7 = QtCore.QRect(self.lpad, y1*10+self.tpad, x1, self.label_height)
        rect8 = QtCore.QRect(self.lpad, y1*11+self.tpad, x1, self.label_height)
        rect9 = QtCore.QRect(self.lpad, y1*13+self.tpad, x1, self.label_height)
        rect10 = QtCore.QRect(self.lpad, y1*14+self.tpad, x1, self.label_height)
        rect11 = QtCore.QRect(self.lpad, y1*15+self.tpad, x1, self.label_height)
        rect12 = QtCore.QRect(self.lpad, y1*17+self.bpad, x1, self.label_height)
        rect13 = QtCore.QRect(self.lpad, y1*18+self.bpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'SFC-1km')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'SFC-3km')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Eff Inflow Layer')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'SFC-6km')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'SFC-8km')
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'LCL-EL (Cloud Layer)')
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Eff Shear (EBWD)')
        qp.drawText(rect7, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'BRN Shear = ')
        qp.drawText(rect8, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, '4-6km SR Wind = ')
        qp.drawText(rect9, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, '...Storm Motion Vectors...')
        qp.drawText(rect10, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Bunkers Right = ')
        qp.drawText(rect11, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Bunkers Left = ')
        qp.drawText(rect12, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Corfidi Downshear = ')
        qp.drawText(rect13, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Corfidi Upshear = ')
        
        ## draw lines seperating the indices
        qp.drawLine( 0, (self.bry/17)+4, self.brx, (self.bry/17)+4 )
    
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
        
        mean_1km = prof.mean_1km
        mean_3km = prof.mean_3km
        mean_6km = prof.mean_6km
        mean_8km = prof.mean_8km
        mean_lcl_el = prof.mean_lcl_el
        mean_eff = prof.mean_eff
        mean_ebw = prof.mean_ebw
        self.mean_1km = tab.utils.comp2vec(mean_1km[0], mean_1km[1])
        self.mean_3km = tab.utils.comp2vec(mean_3km[0], mean_3km[1])
        self.mean_6km = tab.utils.comp2vec(mean_6km[0], mean_6km[1])
        self.mean_8km = tab.utils.comp2vec(mean_8km[0], mean_8km[1])
        self.mean_lcl_el = tab.utils.comp2vec(mean_lcl_el[0], mean_lcl_el[1])
        
        srw_1km = prof.srw_1km
        srw_3km = prof.srw_3km
        srw_6km = prof.srw_6km
        srw_8km = prof.srw_8km
        srw_lcl_el = prof.srw_lcl_el
        srw_4_5km = prof.srw_4_5km
        srw_eff = prof.srw_eff
        srw_ebw = prof.srw_ebw
        self.srw_1km = tab.utils.comp2vec(srw_1km[0], srw_1km[1])
        self.srw_3km = tab.utils.comp2vec(srw_3km[0], srw_3km[1])
        self.srw_6km = tab.utils.comp2vec(srw_6km[0], srw_6km[1])
        self.srw_8km = tab.utils.comp2vec(srw_8km[0], srw_8km[1])
        self.srw_lcl_el = tab.utils.comp2vec(srw_lcl_el[0], mean_lcl_el[1])
        self.srw_4_5km = tab.utils.comp2vec(srw_4_5km[0], srw_4_5km[1])

        
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
        ## draw the indices
        self.drawKinematics(qp)
        self.drawBarbs(qp)
        qp.end()
    
    def drawBarbs(self, qp):
        x1 = self.brx / 10
        y1 = self.bry / 19
        origin_x = x1*8.5
        origin_y = y1*14
        drawBarb(qp, origin_x, origin_y, self.prof.wind1km[0], self.prof.wind1km[1], color='#AA0000')
        drawBarb(qp, origin_x, origin_y, self.prof.wind6km[0], self.prof.wind6km[1], color='#0A74C6')
        pen = QtGui.QPen(QtGui.QColor('#0A74C6'), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rect0 = QtCore.QRect(x1*7, y1*18, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, '1km & 6km AGL\nWind Barbs' )
    
    
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
        y1 = self.bry / 19
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
        rect0 = QtCore.QRect(x1*3, y1*1+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*1+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*1+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*1+self.tpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srh1km)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, sfc1km)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_1km)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_1km)
        ## sfc-3km
        rect0 = QtCore.QRect(x1*3, y1*2+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*2+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*2+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*2+self.tpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srh3km)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, sfc3km)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_3km)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_3km)
        ## Effective Inflow Layer
        rect0 = QtCore.QRect(x1*3, y1*3+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*3+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*3+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*3+self.tpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, esrh)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, eff_lr)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_eff)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_eff)
        ## sfc-6km
        rect1 = QtCore.QRect(x1*5, y1*5+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*5+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*5+self.tpad, x1, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, sfc6km)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_6km)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_6km)
        ## sfc-8km
        rect1 = QtCore.QRect(x1*5, y1*6+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*6+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*6+self.tpad, x1, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, sfc8km)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_8km)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_8km)
        ## LCL-EL
        rect1 = QtCore.QRect(x1*5, y1*7+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*7+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*7+self.tpad, x1, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, lcl_el)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_lcl_el)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_lcl_el)
        ## Effective Shear
        rect1 = QtCore.QRect(x1*5, y1*8+self.tpad, x1, self.label_height)
        rect2 = QtCore.QRect(x1*7, y1*8+self.tpad, x1, self.label_height)
        rect3 = QtCore.QRect(x1*9, y1*8+self.tpad, x1, self.label_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, efbwd)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, mean_ebw)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_ebw)
        ## BRN Shear and 4-6km SR Wind
        rect0 = QtCore.QRect(x1*5, y1*10+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*11+self.tpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, brn_shear)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, srw_4_5km)
        ## bunkers motion
        rect0 = QtCore.QRect(x1*5, y1*14+self.tpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*15+self.tpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, bunkers_right)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, bunkers_left)
        ## upshear and downshear vectors
        rect0 = QtCore.QRect(x1*5, y1*17+self.bpad, x1, self.label_height)
        rect1 = QtCore.QRect(x1*5, y1*18+self.bpad, x1, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, downshear)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, upshear)

