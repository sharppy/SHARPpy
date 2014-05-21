import numpy as np
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
from sharppy.viz.barbs import drawBarb
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *


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
        self.log_pmax = np.log(1050.); self.log_pmin = np.log(self.pmin)
        self.bltmpc = -50; self.brtmpc = 50; self.dt = 10
        self.xskew = 100 / 3.
        self.xrange = self.brtmpc - self.bltmpc
        self.yrange = np.tan(np.deg2rad(self.xskew)) * self.xrange
        self.title_font = QtGui.QFont('Helvetica', 14)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.title_height = self.title_metrics.height()
        self.label_font = QtGui.QFont('Helvetica', 10)
        self.environment_trace_font = QtGui.QFont('Helvetica', 11)
        self.in_plot_font = QtGui.QFont('Helvetica', 7)
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()
    
    
    def plotBackground(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        for t in range(self.bltmpc-100, self.brtmpc+self.dt+100, self.dt):
            self.draw_isotherm(t, qp)
        for tw in range(-160, 61, 10): self.draw_moist_adiabat(tw, qp)
        for theta in range(-70, 350, 20): self.draw_dry_adiabat(theta, qp)
        for w in [2] + range(4, 33, 4): self.draw_mixing_ratios(w, 600, qp)
        self.draw_frame(qp)
        for p in [1000, 850, 700, 500, 300, 200, 100]:
            self.draw_isobar(p, 1, qp)
        for t in range(self.bltmpc, self.brtmpc+self.dt, self.dt):
            self.draw_isotherm_labels(t, qp)
        for p in range(int(self.pmax), int(self.pmin-50), -50):
            self.draw_isobar(p, 0, qp)
        qp.end()


    
    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        self.initUI()

    def draw_dry_adiabat(self, theta, qp):
        '''
        Draw the given moist adiabat.

        '''
        pen = QtGui.QPen(QtGui.QColor("#333333"), 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dt = -10
        presvals = np.arange(int(self.pmax), int(self.pmin)+dt, dt)
        thetas = tab.thermo.theta(presvals, theta)
        thetas = ((theta + ZEROCNK) / ((1000. / presvals)**ROCP)) - ZEROCNK
        for t, p in zip(thetas, presvals):
            x = self.tmpc_to_pix(t, p)
            y = self.pres_to_pix(p)
            if p == self.pmax:
                x2 = x; y2 = y
            else:
                x1 = x2; y1 = y2
                x2 = x; y2 = y
                qp.drawLine(x1, y1, x2, y2)

    def draw_moist_adiabat(self, tw, qp):
        '''
        Draw the given moist adiabat.

        '''
        pen = QtGui.QPen(QtGui.QColor("#663333"), 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dt = -10
        for p in range(int(self.pmax), int(self.pmin)+dt, dt):
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
            str(int(w)))

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
                    QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, str(int(t)))

    def draw_isotherm(self, t, qp):
        '''
        Draw background isotherms.

        '''
        x1 = self.tmpc_to_pix(t, self.pmax)
        x2 = self.tmpc_to_pix(t, self.pmin)
        if t in [0, -20]:
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
                        str(int(p)))
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
        self.prof = prof
        self.pres = prof.pres; self.hght = prof.hght
        self.tmpc = prof.tmpc; self.dwpc = prof.dwpc
        self.u = prof.u; self.v = prof.v
        self.wetbulb = prof.wetbulb
        self.logp = np.log10(prof.pres)
        self.pcl = kwargs.get('pcl', None)
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
        self.presReadout.setText(str(np.around(pres, 1)) + ' hPa')
        try:
            self.hghtReadout.setText(str(np.around(hgt, 1)) + ' km')
        except:
            self.hghtReadout.setText(str(hgt) + ' km')
        try:
            self.tmpcReadout.setText(str(np.around(tmp, 1)) + ' C')
        except:
            self.tmpcReadout.setText(str(tmp) + ' C')
        try:
            self.dwpcReadout.setText(str(np.around(dwp, 1)) + ' C')
        except:
            self.dwpcReadout.setText(str(tmp) + ' C')

        self.presReadout.move(self.lpad, e.y())
        self.hghtReadout.move(self.lpad, e.y() - 15)
        self.tmpcReadout.move(self.brx-self.rpad, e.y())
        self.dwpcReadout.move(self.brx-self.rpad, e.y() - 15)
        self.rubberBand.show()
    
    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        super(plotSkewT, self).resizeEvent(e)
        self.plotData()

    def paintEvent(self, e):
        super(plotSkewT, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()
    
    def plotData(self):
        '''
        Plot the data used in a Skew-T.

       '''
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        self.drawTitle(qp)
        self.drawWetBulb(self.wetbulb, QtGui.QColor(self.wetbulb_color), qp)
        self.drawTrace(self.dwpc, QtGui.QColor(self.dewp_color), qp)
        self.drawTrace(self.tmpc, QtGui.QColor(self.temp_color), qp)
        for h in [0,1000.,3000.,6000.,9000.,12000.,15000.]:
            self.draw_height(h, qp)
        if self.pcl is not None:
            self.drawVirtualParcelTrace(qp)
        self.drawBarbs(qp)
        self.draw_effective_layer(qp)
        qp.end()

    def drawBarbs(self, qp):
        i = 0
        mask1 = self.u.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        pres = self.pres[~mask][::1]
        u = self.u[~mask][::1]
        v = self.v[~mask][::1]
        for p in pres:
            y = self.pres_to_pix(p)
            if y >= self.tly:
                uu = u[i]
                vv = v[i]
                drawBarb( qp, self.barbx, y, uu, vv )
                i = i + 1
            else:
                pass

    def drawTitle(self, qp):
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(self.lpad*3, 0, 150, self.title_height)
        rect1 = QtCore.QRect(self.lpad*6, 0, 150, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignRight, self.title)
    
    
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
                str(int(h/1000))+' km')

    def draw_effective_layer(self, qp):
        ptop = self.prof.etop; pbot = self.prof.ebottom
        len = 15
        text_offset = 10
        if ptop is np.ma.masked and pbot is np.ma.masked:
            pass
        else:
            x1 = self.tmpc_to_pix(-20, 1000)
            y1 = self.pres_to_pix(pbot)
            y2 = self.pres_to_pix(ptop)
            rect1 = QtCore.QRectF(x1-60, y1+4, 40, 15)
            rect2 = QtCore.QRectF(x1-60, y2-15, 40, 15)
            rect3 = QtCore.QRectF(x1-15, y2-15, 40, 15)
            pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
            brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
            qp.setPen(pen)
            qp.setBrush(brush)
            sfc = tab.interp.hght( self.prof, self.prof.pres[self.prof.sfc] )
            if self.prof.pres[ self.prof.sfc ] == pbot:
                text_bot = 'SFC'
            else:
                text_bot = tab.interp.hght(self.prof, pbot) - sfc
                text_bot = str( int( text_bot ) ) + 'm'
            text_top = tab.interp.hght(self.prof, ptop) - sfc
            text_top = str( int( text_top ) ) + 'm'
            qp.drawRect(rect1)
            qp.drawRect(rect2)
            qp.drawRect(rect3)
            pen = QtGui.QPen(QtGui.QColor('#04DBD8'), 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            font = QtGui.QFont('Helvetica', 9, QtGui.QFont.Bold)
            qp.setFont(font)  
            qp.drawLine(x1-len, y1, x1+len, y1)
            qp.drawLine(x1-len, y2, x1+len, y2)
            qp.drawLine(x1, y1, x1, y2)
            qp.drawText(rect1, QtCore.Qt.AlignCenter, text_bot)
            qp.drawText(rect2, QtCore.Qt.AlignCenter, text_top)
            qp.drawText(rect3, QtCore.Qt.AlignCenter, str(int(self.prof.right_esrh[0])))
           # qp.drawText(x1-2*len, y1-text_offset, 40, 40,
           #     QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
           #     text_bot)
    
    def drawVirtualParcelTrace(self,qp):
        ''' Draw the trace of supplied parcel '''
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        p = self.pcl.pres
        t = self.pcl.tmpc
        td = self.pcl.dwpc
        x1 = self.tmpc_to_pix(tab.thermo.virtemp(p, t, td), p)
        y1 = self.pres_to_pix(p)
        p2, t2 = tab.thermo.drylift(p, t, td)
        x2 = self.tmpc_to_pix(tab.thermo.virtemp(p2, t2, t2), p2)
        y2 = self.pres_to_pix(p2)
        qp.drawLine( x1, y1, x2, y2 )
        for i in range(int(p2 + self.dp), int(self.pmin-1), int(self.dp)):
            x1 = x2
            y1 = y2
            t3 = tab.thermo.wetlift(p2, t2, float(i))
            x2 = self.tmpc_to_pix(tab.thermo.virtemp(i, t3, t3), float(i))
            y2 = self.pres_to_pix(float(i))
            if x2 < self.tlx: break
            qp.drawLine( x1, y1, x2, y2 )

    def drawWetBulb(self, data, color, qp):
        '''
        Draw an environmental trace.
        '''
        pen = QtGui.QPen(QtGui.QColor(color), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        mask1 = data.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        data = data[~mask]
        pres = self.pres[~mask]
        x = self.tmpc_to_pix(data, pres)
        y = self.pres_to_pix(pres)
        for i in range(x.shape[0]-1):
            if y[i+1] > self.tpad:
                qp.drawLine(x[i], y[i], x[i+1], y[i+1])
            else:
                qp.drawLine(x[i], y[i], x[i+1], self.tpad+2)
                break

    def drawTrace(self, data, color, qp):
        '''
        Draw an environmental trace.

        '''
        pen = QtGui.QPen(QtGui.QColor(color), 3, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        mask1 = data.mask
        mask2 = self.pres.mask
        mask = np.maximum(mask1, mask2)
        data = data[~mask]
        pres = self.pres[~mask]
        x = self.tmpc_to_pix(data, pres)
        y = self.pres_to_pix(pres)
        for i in range(x.shape[0]-1):
            if y[i+1] > self.tpad:
                qp.drawLine(x[i], y[i], x[i+1], y[i+1])
            else:
                qp.drawLine(x[i], y[i], x[i+1], self.tpad+2)
                break
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
        qp.drawText(rect, QtCore.Qt.AlignCenter, str(int(label)))


