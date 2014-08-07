import numpy as np
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
from sharppy.viz.barbs import drawBarb
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtOpenGL import *
import datetime


__all__ = ['backgroundSkewT', 'plotSkewT']

class backgroundSkewT(QtGui.QWidget):
    def __init__(self):
        super(backgroundSkewT, self).__init__()
        self.initUI()

    def initUI(self):
        '''
        Initialize the User Interface.

        '''
        self.lpad = 30; self.rpad = 50
        self.tpad = 20; self.bpad = 20
        self.tlx = self.rpad; self.tly = self.tpad
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.brx = self.wid ; self.bry = self.hgt
        self.pmax = 1050.; self.pmin = 100.
        self.barbx = self.brx + self.rpad / 2
        self.log_pmax = np.log(self.pmax); self.log_pmin = np.log(self.pmin)
        self.bltmpc = -50; self.brtmpc = 50; self.dt = 10
        self.xskew = 100 / 3.
        self.xrange = self.brtmpc - self.bltmpc
        self.yrange = np.tan(np.deg2rad(self.xskew)) * self.xrange
        self.centert = (self.brtmpc - self.bltmpc) / 2.
        self.centerp = self.pix_to_pres(self.hgt/2.)
        if self.physicalDpiX() > 75:
            fsize = 6
        else:
            fsize = 7
        self.title_font = QtGui.QFont('Helvetica', 14)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.title_height = self.title_metrics.xHeight() + 5
        self.label_font = QtGui.QFont('Helvetica', fsize + 2)
        self.environment_trace_font = QtGui.QFont('Helvetica', 11)
        self.in_plot_font = QtGui.QFont('Helvetica', fsize)
        self.esrh_font = QtGui.QFont('Helvetica', fsize + 2)
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()
    
    
    def plotBackground(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        for t in np.arange(self.bltmpc-100, self.brtmpc+self.dt, self.dt):
            self.draw_isotherm(t, qp)
        #for tw in range(self.bltmpc, self.brtmpc, 10): self.draw_moist_adiabat(tw, qp)
        for theta in np.arange(self.bltmpc, 80, 20): self.draw_dry_adiabat(theta, qp)
        for w in [2] + range(4, 33, 4): self.draw_mixing_ratios(w, 600, qp)
        self.draw_frame(qp)
        for p in [1000, 850, 700, 500, 300, 200, 100]:
            self.draw_isobar(p, 1, qp)
        for t in np.arange(self.bltmpc, self.brtmpc+self.dt, self.dt):
            self.draw_isotherm_labels(t, qp)
        for p in range(int(self.pmax), int(self.pmin-50), -50):
            self.draw_isobar(p, 0, qp)
        qp.end()


    
    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        self.initUI()
    
    def wheelEvent(self, e):
        cursor_y = e.y()
        cursor_p = self.centerp
        cursor_t = self.centert
        ## set the upper and lower zoom rate based
        ## on the distance from the ma value displayed
        rate_upperp = np.log10(self.pmax - cursor_p)
        rate_lowerp = np.log10(cursor_p - self.pmin)
        rate_uppert = rate_upperp * 8
        rate_lowert = rate_lowerp * 5
        ## use the rate to give a delta
        deltap_upper = e.delta() / rate_upperp
        deltap_lower = e.delta() / rate_lowerp
        deltat_upper = e.delta() / rate_uppert
        deltat_lower = e.delta() / rate_lowert
        ## change the vertical bounds
        new_pmin = self.pmin - deltap_lower
        new_pmax = self.pmax + deltap_upper
        ## change the horizontal bounds
        new_tmin = self.bltmpc - deltat_lower
        new_tmax = self.brtmpc + deltat_upper
        ## make sure that the vertical zooming
        ## doesn't go out of bounds
        if new_pmin <= self.centerp - 100. and new_pmin >= 100.:
            self.pmin = new_pmin
        else:
            self.pmin = np.floor(self.pmin)
        if new_pmax >= self.centerp + 100. and new_pmax <= 1050.:
            self.pmax = new_pmax
        else:
            self.pmax = int(self.pmax)
        ## make sure that the horizontal zooming
        ## doesn't go out of bounds
        if new_tmin <= cursor_t - 20. and new_tmin > -50:
            self.bltmpc = new_tmin
        else:
            self.bltmpc = np.floor(self.bltmpc)
        if new_tmax >= cursor_t + 20. and new_tmax < 50:
            self.brtmpc = new_tmax
        else:
            self.brtmpc = int(self.brtmpc)
        self.log_pmin = np.log(self.pmin)
        self.log_pmax = np.log(self.pmax)
        self.xrange = int(self.brtmpc) - int(self.bltmpc)
        self.yrange = np.tan(np.deg2rad(self.xskew)) * self.xrange
        self.update()

    def draw_dry_adiabat(self, theta, qp):
        '''
        Draw the given moist adiabat.

        '''
        pen = QtGui.QPen(QtGui.QColor("#333333"), 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dp = -10
        presvals = np.arange(int(self.pmax), int(self.pmin)+dp, dp)
        thetas = ((theta + ZEROCNK) / (np.power((1000. / presvals),ROCP))) - ZEROCNK
        xvals = self.tmpc_to_pix(thetas, presvals)
        yvals = self.pres_to_pix(presvals)
        path = QPainterPath()
        path.moveTo(xvals[0], yvals[0])
        for i in range(1, len(presvals) ):
            p = presvals[i]
            x = xvals[i]
            y = yvals[i]
            path.lineTo(x, y)
        qp.drawPath(path)

    def draw_moist_adiabat(self, tw, qp):
        '''
        Draw the given moist adiabat.

        '''
        pen = QtGui.QPen(QtGui.QColor("#663333"), 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dp = -10
        for p in range(int(self.pmax), int(self.pmin)+dp, dp):
            t = tab.thermo.wetlift(1000., tw, p)
            x = self.tmpc_to_pix(t, p)
            y = self.pres_to_pix(p)
            if p == self.pmax:
                x2 = x; y2 = y
            else:
                x1 = x2; y1 = y2
                x2 = x; y2 = y
                qp.drawLine(x1, y1, x2, y2)

    def draw_mixing_ratios(self, w, pmin, qp):
        '''
        Draw the mixing ratios.

        '''
        t = tab.thermo.temp_at_mixrat(w, self.pmax)
        x1 = self.tmpc_to_pix(t, self.pmax)
        y1 = self.pres_to_pix(self.pmax)
        t = tab.thermo.temp_at_mixrat(w, pmin)
        x2 = self.tmpc_to_pix(t, pmin)
        y2 = self.pres_to_pix(pmin)
        rectF = QtCore.QRectF(x2-5, y2-10, 10, 10)
        pen = QtGui.QPen(QtGui.QColor('#000000'), 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawRect(rectF)
        pen = QtGui.QPen(QtGui.QColor('#006600'), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.in_plot_font)
        qp.drawLine(x1, y1, x2, y2)
        qp.drawText(rectF, QtCore.Qt.AlignBottom | QtCore.Qt.AlignCenter,
            tab.utils.INT2STR(w))

    def draw_frame(self, qp):
        '''
        Draw the frame around the Skew-T.

        '''
        pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawRect(0, 0, self.lpad, self.bry)
        qp.drawRect(0, self.pres_to_pix(self.pmax), self.brx, self.bry)
        qp.drawRect(self.brx, 0, self.wid+self.rpad,
                    self.pres_to_pix(self.pmax))
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(self.lpad, self.tpad, self.brx+self.rpad, self.tpad)
        qp.drawLine(self.brx+self.rpad, self.tpad, self.brx+self.rpad,
                    self.bry)
        qp.drawLine(self.brx+self.rpad, self.bry, self.lpad, self.bry)
        qp.drawLine(self.lpad, self.bry, self.lpad, self.tpad)

    def draw_isotherm_labels(self, t, qp):
        '''
        Add Isotherm Labels.

        '''
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"))
        qp.setFont(self.label_font)
        x1 = self.tmpc_to_pix(t, self.pmax)
        qp.drawText(x1-10, self.bry+2, 20, 20,
                    QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, tab.utils.INT2STR(t))

    def draw_isotherm(self, t, qp):
        '''
        Draw background isotherms.

        '''
        x1 = self.tmpc_to_pix(t, self.pmax)
        x2 = self.tmpc_to_pix(t, self.pmin)
        if int(t) in [0, -20]:
            pen = QtGui.QPen(QtGui.QColor("#0000FF"), 1)
        else:
            pen = QtGui.QPen(QtGui.QColor("#555555"), 1)
        pen.setStyle(QtCore.Qt.CustomDashLine)
        pen.setDashPattern([4, 2])
        qp.setPen(pen)
        qp.drawLine(x1, self.bry, x2, self.tpad)

    def draw_isobar(self, p, flag, qp):
        '''
        Draw background isobars.

        '''
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        y1 = self.pres_to_pix(p)
        offset = 5
        if flag:
            qp.drawLine(self.lpad, y1, self.brx, y1)
            qp.drawText(1, y1-20, self.lpad-4, 40,
                        QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
                        tab.utils.INT2STR(p))
        else:
            qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
            qp.drawLine(self.brx+self.rpad-offset, y1,
                        self.brx+self.rpad, y1)

    def tmpc_to_pix(self, t, p):
        '''
        Function to convert a (temperature, pressure) coordinate
        to an X pixel.

        '''
        scl1 = self.brtmpc - (((self.bry - self.pres_to_pix(p)) /
                              (self.bry - self.tpad)) * self.yrange)
        return self.brx - (((scl1 - t) / self.xrange) * (self.brx - self.lpad))

    def pres_to_pix(self, p):
        '''
        Function to convert a pressure value (level) to a Y pixel.

        '''
        scl1 = self.log_pmax - self.log_pmin
        scl2 = self.log_pmax - np.log(p)
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def pix_to_pres(self, y):
        '''
        Function to convert a Y pixel to a pressure level.

        '''
        scl1 = np.log(self.pmax) - np.log(self.pmin)
        scl2 = self.bry - float(y)
        scl3 = self.bry - self.tly + 1
        return self.pmax / np.exp((scl2 / scl3) * scl1)




class plotSkewT(backgroundSkewT):
    def __init__(self, prof, **kwargs):
        super(plotSkewT, self).__init__()
        ## get the profile data
        self.prof = prof
        self.pres = prof.pres; self.hght = prof.hght
        self.tmpc = prof.tmpc; self.dwpc = prof.dwpc
        self.dew_stdev = prof.dew_stdev
        self.tmp_stdev = prof.tmp_stdev
        self.u = prof.u; self.v = prof.v
        self.wetbulb = prof.wetbulb
        self.dpcl_ttrace = prof.dpcl_ttrace
        self.dpcl_ptrace = prof.dpcl_ptrace
        self.logp = np.log10(prof.pres)
        self.pcl = kwargs.get('pcl', None)
        self.proflist = kwargs.get('proflist', None)
        ## ui stuff
        self.title = kwargs.get('title', '')
        self.dp = -25
        self.temp_color = kwargs.get('temp_color', '#FF0000')
        self.dewp_color = kwargs.get('dewp_color', '#00FF00')
        self.wetbulb_color = kwargs.get('wetbulb_color', '#00FFFF')
        self.setMouseTracking(True)
        ## create the readout labels
        self.presReadout = QLabel(parent=self)
        self.hghtReadout = QLabel(parent=self)
        self.tmpcReadout = QLabel(parent=self)
        self.dwpcReadout = QLabel(parent=self)
        ## set their alignments
        self.presReadout.setAlignment(QtCore.Qt.AlignCenter)
        self.hghtReadout.setAlignment(QtCore.Qt.AlignCenter)
        self.tmpcReadout.setAlignment(QtCore.Qt.AlignCenter)
        self.dwpcReadout.setAlignment(QtCore.Qt.AlignCenter)
        ## initialize the width to 0 so that they don't show up
        ## on initialization
        self.presReadout.setFixedWidth(0)
        self.hghtReadout.setFixedWidth(0)
        self.tmpcReadout.setFixedWidth(0)
        self.dwpcReadout.setFixedWidth(0)
        ## set the style sheet for text size, color, etc
        self.presReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #FFFFFF;}")
        self.hghtReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #FF0000;}")
        self.tmpcReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #FF0000;}")
        self.dwpcReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #00FF00;}")
        self.rubberBand = QRubberBand(QRubberBand.Line, self)
    
    def mousePressEvent(self, e):
        if self.hasMouseTracking():
            self.setMouseTracking(False)
        else:
            self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        pres = self.pix_to_pres(e.y())
        hgt = tab.interp.to_agl( self.prof, tab.interp.hght(self.prof, pres) )
        tmp = tab.interp.temp(self.prof, pres)
        dwp = tab.interp.dwpt(self.prof, pres)
        self.rubberBand.setGeometry(QRect(QPoint(self.lpad,e.y()), QPoint(self.brx,e.y())).normalized())
        self.presReadout.setFixedWidth(60)
        self.hghtReadout.setFixedWidth(65)
        self.tmpcReadout.setFixedWidth(45)
        self.dwpcReadout.setFixedWidth(45)
        self.presReadout.setText(tab.utils.FLOAT2STR(pres, 1) + ' hPa')
        self.hghtReadout.setText(tab.utils.FLOAT2STR(hgt, 1) + ' m')
        self.tmpcReadout.setText(tab.utils.FLOAT2STR(tmp, 1) + ' C')
        self.dwpcReadout.setText(tab.utils.FLOAT2STR(dwp, 1) + ' C')

        self.presReadout.move(self.lpad, e.y())
        self.hghtReadout.move(self.lpad, e.y() - 15)
        self.tmpcReadout.move(self.brx-self.rpad, e.y())
        self.dwpcReadout.move(self.brx-self.rpad, e.y() - 15)
        self.centerp = self.pix_to_pres(e.y())
        self.centert = tmp
        self.rubberBand.show()
    
    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        super(plotSkewT, self).resizeEvent(e)
        self.plotData()
    
    def wheelEvent(self, e):
        super(plotSkewT, self).wheelEvent(e)
        self.clearData()
        self.plotBackground()
        self.plotData()

    def paintEvent(self, e):
        super(plotSkewT, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
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
        Plot the data used in a Skew-T.

       '''
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.drawTitle(qp)
        if self.proflist is not None:
            for profile in self.proflist:
                self.drawTrace(profile.dwpc, QtGui.QColor("#019B06"), qp, p=profile.pres, width=1)
                self.drawTrace(profile.tmpc, QtGui.QColor("#9F0101"), qp, p=profile.pres, width=1)
                self.drawVirtualParcelTrace(profile.mupcl.ttrace, profile.mupcl.ptrace, qp, color="#666666")
        self.drawTrace(self.wetbulb, QtGui.QColor(self.wetbulb_color), qp, width=1)
        self.drawTrace(self.dwpc, QtGui.QColor(self.dewp_color), qp, stdev=self.dew_stdev)
        self.drawTrace(self.tmpc, QtGui.QColor(self.temp_color), qp, stdev=self.tmp_stdev)
        for h in [0,1000.,3000.,6000.,9000.,12000.,15000.]:
            self.draw_height(h, qp)
        if self.pcl is not None:
            self.drawVirtualParcelTrace(self.pcl.ttrace, self.pcl.ptrace, qp)
        self.drawVirtualParcelTrace(self.dpcl_ttrace, self.dpcl_ptrace, qp, color="#FF00FF")
        qp.setRenderHint(qp.Antialiasing, False)
        self.drawBarbs(qp)
        qp.setRenderHint(qp.Antialiasing)
        self.draw_effective_layer(qp)
        qp.end()

    def drawBarbs(self, qp):
        i = 0
        mask1 = self.u.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        pres = self.pres[~mask]
        u = self.u[~mask]
        v = self.v[~mask]
        yvals = self.pres_to_pix(pres)
        for y in yvals:
            if y >= self.tly:
                uu = u[i]
                vv = v[i]
                drawBarb( qp, self.barbx, y, uu, vv )
                i += 1
            else:
                break

    def drawTitle(self, qp):
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(self.lpad, 0, 150, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, self.title)
    
    
    def draw_height(self, h, qp):
        self.hght_font = QtGui.QFont('Helvetica', 9)
        pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.hght_font)
        offset = 10
        txt_offset = 15 
        sfc = tab.interp.hght( self.prof, self.prof.pres[self.prof.sfc] )
        p1 = tab.interp.pres(self.prof, h+sfc)
        if np.isnan(p1) == False:
            y1 = self.pres_to_pix(p1)
            qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
            qp.drawText(self.lpad+txt_offset, y1-20, self.lpad+txt_offset, 40,
                QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
                tab.utils.INT2STR(h/1000)+' km')

    def draw_effective_layer(self, qp):
        '''
        Draw the bounds of the effective inflow layer.
        '''
        ptop = self.prof.etop; pbot = self.prof.ebottom
        len = 15
        text_offset = 10
        if ptop is np.ma.masked and pbot is np.ma.masked:
            pass
        else:
            x1 = self.tmpc_to_pix(-20, 1000)
            y1 = self.pres_to_pix(pbot)
            y2 = self.pres_to_pix(ptop)
            rect1 = QtCore.QRectF(x1-60, y1+4, 50, 20)
            rect2 = QtCore.QRectF(x1-60, y2-15, 50, 20)
            rect3 = QtCore.QRectF(x1-15, y2-15, 50, 20)
            pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
            brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
            qp.setPen(pen)
            qp.setBrush(brush)
            sfc = tab.interp.hght( self.prof, self.prof.pres[self.prof.sfc] )
            if self.prof.pres[ self.prof.sfc ] == pbot:
                text_bot = 'SFC'
            else:
                text_bot = tab.interp.hght(self.prof, pbot) - sfc
                text_bot = tab.utils.INT2STR( text_bot ) + 'm'
            text_top = tab.interp.hght(self.prof, ptop) - sfc
            text_top = tab.utils.INT2STR( text_top ) + 'm'
            qp.drawRect(rect1)
            qp.drawRect(rect2)
            qp.drawRect(rect3)
            pen = QtGui.QPen(QtGui.QColor('#04DBD8'), 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            font = QtGui.QFont('Helvetica', 9, QtGui.QFont.Bold)
            qp.setFont(self.esrh_font)
            qp.drawLine(x1-len, y1, x1+len, y1)
            qp.drawLine(x1-len, y2, x1+len, y2)
            qp.drawLine(x1, y1, x1, y2)
            qp.drawText(rect1, QtCore.Qt.AlignCenter, text_bot)
            qp.drawText(rect2, QtCore.Qt.AlignCenter, text_top)
            qp.drawText(rect3, QtCore.Qt.AlignCenter,
                tab.utils.INT2STR(self.prof.right_esrh[0]) + ' m2s2')
           # qp.drawText(x1-2*len, y1-text_offset, 40, 40,
           #     QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
           #     text_bot)
    
    def drawVirtualParcelTrace(self, ttrace, ptrace, qp, width=1, color="#FFFFFF"):
        '''
        Draw a parcel trace.
        '''
        pen = QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.DashLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        path = QPainterPath()
        yvals = self.pres_to_pix(ptrace)
        xvals = self.tmpc_to_pix(ttrace, ptrace)
        path.moveTo(xvals[0], yvals[0])
        for i in range(1, len(yvals)):
            x = xvals[i]; y = yvals[i]
            if y < self.tpad:
                break
            else:
                path.lineTo(x, y)
        qp.drawPath(path)

    def drawTrace(self, data, color, qp, width=3, p=None, stdev=None):
        '''
        Draw an environmental trace.

        '''
        pen = QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        mask1 = data.mask
        if p is not None:
            mask2 = p.mask
            pres = p
        else:
            mask2 = self.pres.mask
            pres = self.pres
        mask = np.maximum(mask1, mask2)
        data = data[~mask]
        pres = pres[~mask]
        if stdev is not None:
            stdev = stdev[~mask]
        path = QPainterPath()
        x = self.tmpc_to_pix(data, pres)
        y = self.pres_to_pix(pres)
        path.moveTo(x[0], y[0])
        for i in range(1, x.shape[0]):
            if y[i] < self.tpad:
                break
            else:
                qp.save()
                path.lineTo(x[i], y[i])
                if stdev is not None:
                    self.drawSTDEV(pres[i], data[i], stdev[i], color, qp)
                qp.restore()
        qp.drawPath(path)
        label = (1.8 * data[0]) + 32.
        pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        rect = QtCore.QRectF(x[0]-8, y[0]+4, 16, 12)
        qp.drawRect(rect)
        pen = QtGui.QPen(QtGui.QColor(color), 3, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.environment_trace_font)
        qp.drawText(rect, QtCore.Qt.AlignCenter, tab.utils.INT2STR(label))

    def drawSTDEV(self, pres, data, stdev, color, qp, width=1):
        '''
        Draw the error bars on the profile.
        '''
        pen = QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        path = QPainterPath()
        offset = 5.
        x = self.tmpc_to_pix(data, pres)
        y = self.pres_to_pix(pres)
        err_left = self.tmpc_to_pix(data - stdev, pres)
        err_right = self.tmpc_to_pix(data + stdev, pres)
        path.moveTo(err_left, y)
        path.lineTo(err_left, y-offset)
        path.lineTo(err_left, y+offset)
        path.moveTo(err_left, y)
        path.lineTo(err_right, y)
        path.lineTo(err_right, y-offset)
        path.lineTo(err_right, y+offset)
        qp.drawPath(path)

