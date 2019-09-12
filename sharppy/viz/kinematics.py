import logging
import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.viz.barbs import drawBarb
from sharppy.sharptab.constants import *
import platform

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundKinematics', 'plotKinematics']

class backgroundKinematics(QtWidgets.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self, **kwargs):
        super(backgroundKinematics, self).__init__()
        self.wind_units = kwargs.get('wind_units', 'knots')
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
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 10
        y1 = self.label_height + self.tpad
        ## draw the header
        rect1 = QtCore.QRect(x1*2.5, 3, x1, self.label_height)
        rect2 = QtCore.QRect(x1*5, 3, x1, self.label_height)
        rect3 = QtCore.QRect(x1*7, 3, x1, self.label_height)
        rect4 = QtCore.QRect(x1*9-self.rpad, 3, x1, self.label_height)

        if self.wind_units == 'm/s':
            disp_unit = 'm/s'
        else:
            disp_unit = 'kt'

        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SRH (m2/s2)')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "Shear (%s)" % disp_unit)
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
    def __init__(self, **kwargs):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.

        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.use_left = False

        super(plotKinematics, self).__init__(**kwargs)
        self.prof = None

    def setProf(self, prof):
        self.ylast = self.label_height

        self.prof = prof

        if self.use_left:
            self.srh1km = prof.left_srh1km
            self.srh3km = prof.left_srh3km
            self.esrh = prof.left_esrh

            self.srw_1km = prof.left_srw_1km
            self.srw_3km = prof.left_srw_3km
            self.srw_6km = prof.left_srw_6km
            self.srw_8km = prof.left_srw_8km
            self.srw_lcl_el = prof.left_srw_lcl_el
            self.srw_4_5km = prof.left_srw_4_5km
            srw_eff = prof.left_srw_eff
            srw_ebw = prof.left_srw_ebw
        else:
            self.srh1km = prof.right_srh1km
            self.srh3km = prof.right_srh3km
            self.esrh = prof.right_esrh

            self.srw_1km = prof.right_srw_1km
            self.srw_3km = prof.right_srw_3km
            self.srw_6km = prof.right_srw_6km
            self.srw_8km = prof.right_srw_8km
            self.srw_lcl_el = prof.right_srw_lcl_el
            self.srw_4_5km = prof.right_srw_4_5km
            srw_eff = prof.right_srw_eff
            srw_ebw = prof.right_srw_ebw

        self.mean_1km = prof.mean_1km
        self.mean_3km = prof.mean_3km
        self.mean_6km = prof.mean_6km
        self.mean_8km = prof.mean_8km
        self.mean_lcl_el = prof.mean_lcl_el
        mean_eff = prof.mean_eff
        mean_ebw = prof.mean_ebw

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
        self.bunkers_right_vec = tab.utils.comp2vec(prof.bunkers[0], prof.bunkers[1])
        self.bunkers_left_vec = tab.utils.comp2vec(prof.bunkers[2], prof.bunkers[3])
        self.upshear = tab.utils.comp2vec(prof.upshear_downshear[0],prof.upshear_downshear[1])
        self.downshear = tab.utils.comp2vec(prof.upshear_downshear[2],prof.upshear_downshear[3])

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.wind_units = prefs['wind_units']

        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            if self.use_left:
                self.srh1km = self.prof.left_srh1km
                self.srh3km = self.prof.left_srh3km
                self.esrh = self.prof.left_esrh

                self.srw_1km = self.prof.left_srw_1km
                self.srw_3km = self.prof.left_srw_3km
                self.srw_6km = self.prof.left_srw_6km
                self.srw_8km = self.prof.left_srw_8km
                self.srw_lcl_el = self.prof.left_srw_lcl_el
                self.srw_4_5km = self.prof.left_srw_4_5km
                srw_eff = self.prof.left_srw_eff
                srw_ebw = self.prof.left_srw_ebw
            else:
                self.srh1km = self.prof.right_srh1km
                self.srh3km = self.prof.right_srh3km
                self.esrh = self.prof.right_esrh

                self.srw_1km = self.prof.right_srw_1km
                self.srw_3km = self.prof.right_srw_3km
                self.srw_6km = self.prof.right_srw_6km
                self.srw_8km = self.prof.right_srw_8km
                self.srw_lcl_el = self.prof.right_srw_lcl_el
                self.srw_4_5km = self.prof.right_srw_4_5km
                srw_eff = self.prof.right_srw_eff
                srw_ebw = self.prof.right_srw_ebw

            if self.prof.etop is np.ma.masked or self.prof.ebottom is np.ma.masked:
                self.srw_eff = [np.ma.masked, np.ma.masked]
                self.srw_ebw = [np.ma.masked, np.ma.masked]
            else:
                self.srw_eff = tab.utils.comp2vec(srw_eff[0], srw_eff[1])
                self.srw_ebw = tab.utils.comp2vec(srw_ebw[0], srw_ebw[1])

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        if self.use_left:
            self.srh1km = self.prof.left_srh1km
            self.srh3km = self.prof.left_srh3km
            self.esrh = self.prof.left_esrh

            self.srw_1km = self.prof.left_srw_1km
            self.srw_3km = self.prof.left_srw_3km
            self.srw_6km = self.prof.left_srw_6km
            self.srw_8km = self.prof.left_srw_8km
            self.srw_lcl_el = self.prof.left_srw_lcl_el
            self.srw_4_5km = self.prof.left_srw_4_5km
            srw_eff = self.prof.left_srw_eff
            srw_ebw = self.prof.left_srw_ebw
        else:
            self.srh1km = self.prof.right_srh1km
            self.srh3km = self.prof.right_srh3km
            self.esrh = self.prof.right_esrh

            self.srw_1km = self.prof.right_srw_1km
            self.srw_3km = self.prof.right_srw_3km
            self.srw_6km = self.prof.right_srw_6km
            self.srw_8km = self.prof.right_srw_8km
            self.srw_lcl_el = self.prof.right_srw_lcl_el
            self.srw_4_5km = self.prof.right_srw_4_5km
            srw_eff = self.prof.right_srw_eff
            srw_ebw = self.prof.right_srw_ebw

        if self.prof.etop is np.ma.masked or self.prof.ebottom is np.ma.masked:
            self.srw_eff = [np.ma.masked, np.ma.masked]
            self.srw_ebw = [np.ma.masked, np.ma.masked]
        else:
            self.srw_eff = tab.utils.comp2vec(srw_eff[0], srw_eff[1])
            self.srw_ebw = tab.utils.comp2vec(srw_ebw[0], srw_ebw[1])

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

        if self.wind_units == "m/s":
            conv = tab.utils.KTS2MS
        else:
            conv = lambda s: s
        try:
            drawBarb(qp, origin_x, self.barby, self.prof.wind1km[0], conv(self.prof.wind1km[1]), color='#AA0000', shemis=(self.prof.latitude < 0))
            drawBarb(qp, origin_x, self.barby, self.prof.wind6km[0], conv(self.prof.wind6km[1]), color='#0A74C6', shemis=(self.prof.latitude < 0))
        except:
            logging.debug("Couldn't draw the 1 or 6 km wind barbs on kinematics.py")
 
    def drawKinematics(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen to draw with.
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad

        if self.wind_units == 'm/s':
            disp_unit = ' m/s'
            conv = tab.utils.KTS2MS
        else:
            disp_unit = ' kt'
            conv = lambda s: s

        ## format the text
        srh1km = tab.utils.INT2STR(self.srh1km[0])
        srh3km = tab.utils.INT2STR(self.srh3km[0])
        
        sfc1km = tab.utils.INT2STR(conv(tab.utils.mag(self.sfc_1km_shear[0], self.sfc_1km_shear[1])))
        sfc3km = tab.utils.INT2STR(conv(tab.utils.mag(self.sfc_3km_shear[0], self.sfc_3km_shear[1])))
        sfc6km = tab.utils.INT2STR(conv(tab.utils.mag(self.sfc_6km_shear[0], self.sfc_6km_shear[1])))
        sfc8km = tab.utils.INT2STR(conv(tab.utils.mag(self.sfc_8km_shear[0], self.sfc_8km_shear[1])))
        lcl_el = tab.utils.INT2STR(conv(tab.utils.mag(self.lcl_el_shear[0], self.lcl_el_shear[1])))
        
        mean_1km = tab.utils.INT2STR(np.float64(self.mean_1km[0])) + '/' + tab.utils.INT2STR(conv(self.mean_1km[1]))
        mean_3km = tab.utils.INT2STR(np.float64(self.mean_3km[0])) + '/' + tab.utils.INT2STR(conv(self.mean_3km[1]))
        mean_6km = tab.utils.INT2STR(np.float64(self.mean_6km[0])) + '/' + tab.utils.INT2STR(conv(self.mean_6km[1]))
        mean_8km = tab.utils.INT2STR(np.float64(self.mean_8km[0])) + '/' + tab.utils.INT2STR(conv(self.mean_8km[1]))
        mean_lcl_el = tab.utils.INT2STR(np.float64(self.mean_lcl_el[0])) + '/' + tab.utils.INT2STR(conv(self.mean_lcl_el[1]))
        
        srw_1km = tab.utils.INT2STR(np.float64(self.srw_1km[0])) + '/' + tab.utils.INT2STR(conv(self.srw_1km[1]))
        srw_3km = tab.utils.INT2STR(np.float64(self.srw_3km[0])) + '/' + tab.utils.INT2STR(conv(self.srw_3km[1]))
        srw_6km = tab.utils.INT2STR(np.float64(self.srw_6km[0])) + '/' + tab.utils.INT2STR(conv(self.srw_6km[1]))
        srw_8km = tab.utils.INT2STR(np.float64(self.srw_8km[0])) + '/' + tab.utils.INT2STR(conv(self.srw_8km[1]))
        srw_lcl_el = tab.utils.INT2STR(np.float64(self.srw_lcl_el[0])) + '/' + tab.utils.INT2STR(conv(self.srw_lcl_el[1]))
        srw_4_5km = tab.utils.INT2STR(np.float64(self.srw_4_5km[0])) + '/' + tab.utils.INT2STR(conv(self.srw_4_5km[1])) + disp_unit
        
        esrh = tab.utils.INT2STR(self.esrh[0])
        eff_lr = tab.utils.INT2STR(conv(tab.utils.mag(self.eff_shear[0], self.eff_shear[1])))
        efbwd = tab.utils.INT2STR(conv(tab.utils.mag(self.ebwd[0], self.ebwd[1])))
        mean_eff = tab.utils.INT2STR(np.float64(self.mean_eff[0])) + '/' + tab.utils.INT2STR(conv(self.mean_eff[1]))
        mean_ebw = tab.utils.INT2STR(np.float64(self.mean_ebw[0])) + '/' + tab.utils.INT2STR(conv(self.mean_ebw[1]))
        srw_eff = tab.utils.INT2STR(np.float64(self.srw_eff[0])) + '/' + tab.utils.INT2STR(conv(self.srw_eff[1]))
        srw_ebw = tab.utils.INT2STR(np.float64(self.srw_ebw[0])) + '/' + tab.utils.INT2STR(conv(self.srw_ebw[1]))
        
        brn_shear = tab.utils.INT2STR(self.brn_shear) + ' m2/s2'
        bunkers_left = tab.utils.INT2STR(np.float64(self.bunkers_left_vec[0])) + '/' + tab.utils.INT2STR(conv(self.bunkers_left_vec[1])) + disp_unit
        bunkers_right = tab.utils.INT2STR(np.float64(self.bunkers_right_vec[0])) + '/' + tab.utils.INT2STR(conv(self.bunkers_right_vec[1])) + disp_unit
        upshear = tab.utils.INT2STR(np.float64(self.upshear[0])) + '/' + tab.utils.INT2STR(conv(self.upshear[1])) + disp_unit
        downshear = tab.utils.INT2STR(np.float64(self.downshear[0])) + '/' + tab.utils.INT2STR(conv(self.downshear[1])) + disp_unit

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
            vspace = self.label_height 
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        self.ylast = y1
        y1 += self.label_height + self.tpad # Not entirely sure why this doesn't 
                                            # need the extra pixels on Windows.
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
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## upshear and downshear vectors
        texts = [downshear, upshear]
        for text in texts:
            rect = QtCore.QRect(x1*5, y1, x1, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, text)
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotKinematics()
    tester.show()    
    app_frame.exec_()
