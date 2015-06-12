import numpy as np
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
from sharppy.sharptab.profile import Profile, create_profile
from sharppy.viz.barbs import drawBarb
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtOpenGL import *

from datetime import datetime, timedelta

__all__ = ['backgroundSkewT', 'plotSkewT']

class backgroundSkewT(QtGui.QWidget):
    def __init__(self, plot_omega=False):
        super(backgroundSkewT, self).__init__()
        self.plot_omega = plot_omega
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
        self.clip = QRect(QPoint(self.lpad, self.tly), QPoint(self.brx + self.rpad, self.bry))
#       self.centert = (self.brtmpc - self.bltmpc) / 2.
#       self.centerp = self.pix_to_pres(self.hgt/2.)
        self.originx = 0. # self.size().width() / 2
        self.originy = 0. # self.size().height() / 2
        self.scale = 1.
        if self.physicalDpiX() > 75:
            fsize = 6
            fsizet = 10
        else:
            fsize = 7
            fsizet = 14
        self.title_font = QtGui.QFont('Helvetica', fsizet)
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.title_height = self.title_metrics.xHeight() + 5
        self.label_font = QtGui.QFont('Helvetica', fsize + 2)
        self.environment_trace_font = QtGui.QFont('Helvetica', 11)
        self.in_plot_font = QtGui.QFont('Helvetica', fsize)
        self.esrh_font = QtGui.QFont('Helvetica', fsize + 2)
        self.esrh_metrics = QtGui.QFontMetrics( self.esrh_font )
        self.esrh_height = self.esrh_metrics.xHeight() + 9
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.saveBitMap = None
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()
    
    def plotBackground(self):
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setClipRect(self.clip)

        qp.translate(self.originx, self.originy)
        qp.scale(1. / self.scale, 1. / self.scale)

        self.transform = qp.transform()

        qp.scale(self.scale, self.scale)
        qp.translate(-self.originx, -self.originy)

        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        for t in np.arange(self.bltmpc-100, self.brtmpc+self.dt, self.dt):
            self.draw_isotherm(t, qp)
        #for tw in range(self.bltmpc, self.brtmpc, 10): self.draw_moist_adiabat(tw, qp)
        for theta in np.arange(self.bltmpc, 80, 20): self.draw_dry_adiabat(theta, qp)
        for w in [2] + np.arange(4, 33, 4): self.draw_mixing_ratios(w, 600, qp)
        self.draw_frame(qp)
        for p in [1000, 850, 700, 500, 300, 200, 100]:
            self.draw_isobar(p, 1, qp)
        for t in np.arange(self.bltmpc, self.brtmpc+self.dt, self.dt):
            self.draw_isotherm_labels(t, qp)
        for p in xrange(int(self.pmax), int(self.pmin-50), -50):
            self.draw_isobar(p, 0, qp)

        if self.plot_omega:
            plus10_bound = -49
            minus10_bound = -41
            x1_m10 = self.tmpc_to_pix(minus10_bound, 1000)
            y1_m10 = self.pres_to_pix(1000)
            y2_m10 = self.pres_to_pix(111)
            pen = QtGui.QPen(QtCore.Qt.magenta, 1, QtCore.Qt.DashDotLine)
            qp.setPen(pen)
            qp.drawLine(x1_m10, y1_m10, x1_m10, y2_m10)
            x1_10 = self.tmpc_to_pix(plus10_bound, 1000)
            y1_10 = self.pres_to_pix(1000)
            y2_10 = self.pres_to_pix(111)
            qp.drawLine(x1_10, y1_10, x1_10, y2_10)
            pen = QtGui.QPen(QtCore.Qt.magenta, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.tmpc_to_pix((plus10_bound + minus10_bound)/2., 1000)
            y1 = self.pres_to_pix(1000)
            y2 = self.pres_to_pix(111)
            qp.drawLine(x1, y1, x1, y2)
            rect3 = QtCore.QRectF(x1_10, y2 - 18, x1_m10 - x1_10, 4) 
            qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "OMEGA")  
            rect3 = QtCore.QRectF(x1_m10-3, y2 - 7, 5, 4) 
            qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "-10")               
            rect3 = QtCore.QRectF(x1_10-3, y2 - 7, 5, 4) 
            qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "+10")

        qp.end()
        self.backgroundBitMap = self.plotBitMap.copy(0, 0, self.width(), self.height())

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        self.initUI()
    
    def wheelEvent(self, e):
        centerx, centery = e.x(), e.y()

        # From map
        max_speed = 100.
        delta = max(min(-e.delta(), max_speed), -max_speed)
        scale_fac = 10 ** (delta / 1000.)

        if self.scale * scale_fac > 1.0:
            scale_fac = 1. / self.scale

        self.scale *= scale_fac

        self.originx = centerx - (centerx - self.originx) / scale_fac
        self.originy = centery - (centery - self.originy) / scale_fac

        ll_x = self.originx + self.width() / self.scale
        ll_y = self.originy + self.height() / self.scale

        if ll_x < self.width():
            self.originx += (self.width() - ll_x)
        elif self.originx > 0:
            self.originx = 0

        if ll_y < self.height():
            self.originy += (self.height() - ll_y)
        elif self.originy > 0:
            self.originy = 0

        self.plotBackground()
        self.update()

    def draw_dry_adiabat(self, theta, qp):
        '''
        Draw the given moist adiabat.
        '''
        qp.setClipping(True)
        pen = QtGui.QPen(QtGui.QColor("#333333"), 1)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dp = -10
        presvals = np.arange(int(self.pmax), int(self.pmin)+dp, dp)
        thetas = ((theta + ZEROCNK) / (np.power((1000. / presvals),ROCP))) - ZEROCNK
        xvals = self.originx + self.tmpc_to_pix(thetas, presvals) / self.scale
        yvals = self.originy + self.pres_to_pix(presvals) / self.scale
        path = QPainterPath()
        path.moveTo(xvals[0], yvals[0])
        for i in xrange(1, len(presvals) ):
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
        for p in xrange(int(self.pmax), int(self.pmin)+dp, dp):
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
        qp.setClipping(True)
        t = tab.thermo.temp_at_mixrat(w, self.pmax)
        x1 = self.originx + self.tmpc_to_pix(t, self.pmax) / self.scale
        y1 = self.originy + self.pres_to_pix(self.pmax) / self.scale
        t = tab.thermo.temp_at_mixrat(w, pmin)
        x2 = self.originx + self.tmpc_to_pix(t, pmin) / self.scale
        y2 = self.originy + self.pres_to_pix(pmin) / self.scale
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
        qp.setClipping(False)
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
        x1 = self.originx + self.tmpc_to_pix(t, self.pmax) / self.scale

        if x1 >= self.lpad and x1 <= self.wid:
            qp.setClipping(False)
            qp.drawText(x1-10, self.bry+2, 20, 20,
                        QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, tab.utils.INT2STR(t))

    def draw_isotherm(self, t, qp):
        '''
        Draw background isotherms.

        '''

        qp.setClipping(True)
        x1 = self.originx + self.tmpc_to_pix(t, self.pmax) / self.scale
        x2 = self.originx + self.tmpc_to_pix(t, self.pmin) / self.scale
        y1 = self.originy + self.bry / self.scale
        y2 = self.originy + self.tpad / self.scale
        if int(t) in [0, -20]:
            pen = QtGui.QPen(QtGui.QColor("#0000FF"), 1)
        else:
            pen = QtGui.QPen(QtGui.QColor("#555555"), 1)
        pen.setStyle(QtCore.Qt.CustomDashLine)
        pen.setDashPattern([4, 2])
        qp.setPen(pen)
        qp.drawLine(x1, y1, x2, y2)

    def draw_isobar(self, p, flag, qp):
        '''
        Draw background isobars.

        '''
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        y1 = self.originy + self.pres_to_pix(p) / self.scale
        if y1 >= self.tpad and y1 <= self.hgt:
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

    def pix_to_tmpc(self, x, y):
        '''
        Function to convert an (x, y) pixel into a temperature
        '''
        scl1 = self.brtmpc - (((self.bry - y) /
                              float(self.bry - self.tpad)) * self.yrange)
        return scl1 - (((self.brx - x) / float(self.brx - self.lpad)) * self.xrange)

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
    modified = Signal(int, dict)
    parcel = Signal(tab.params.Parcel)
    reset = Signal(list)

    def __init__(self, **kwargs):
        super(plotSkewT, self).__init__(plot_omega=False)
        ## get the profile data
        self.prof = None
        self.pcl = None
        self.proflist = []

        self.plotdgz = kwargs.get('dgz', False)
        self.interpWinds = kwargs.get('interpWinds', True)

        ## ui stuff
        self.title = kwargs.get('title', '')
        self.dp = -25
        self.temp_color = kwargs.get('temp_color', '#FF0000')
        self.dewp_color = kwargs.get('dewp_color', '#00FF00')
        self.wetbulb_color = kwargs.get('wetbulb_color', '#00FFFF')
        self.setMouseTracking(True)
        self.was_right_click = False
        self.track_cursor = False
        self.readout = False
        self.readout_pres = 1000.
        self.initdrag = False
        self.dragging = False
        self.drag_idx = None
        self.drag_prof = None
        self.drag_buffer = 5
        self.clickradius = 6
        self.cursor_loc = None
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

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showCursorMenu)
        self.parcelmenu = QMenu("Lift Parcel")
        #ag = QtGui.QActionGroup(self, exclusive=True)

        # List of parcels that can be lifted
        pcl1 = QAction(self)
        pcl1.setText("This Parcel")
        pcl1.triggered.connect(lambda: self.liftparcellevel(0))
        #ag.addAction(pcl1)
        self.parcelmenu.addAction(pcl1)

        pcl2 = QAction(self)
        pcl2.setText("50 mb Layer Parcel")
        pcl2.triggered.connect(lambda: self.liftparcellevel(50))
        #ag.addAction(pcl2)
        self.parcelmenu.addAction(pcl2)

        pcl3 = QAction(self)
        pcl3.setText("100 mb Layer Parcel")
        pcl3.triggered.connect(lambda: self.liftparcellevel(100))
        #ag.addAction(pcl3)
        self.parcelmenu.addAction(pcl3)

        pcl4 = QAction(self)
        pcl4.setText("Custom Parcel")
        pcl4.triggered.connect(lambda: self.liftparcellevel(-9999))
        #ag.addAction(pcl4)
        self.parcelmenu.addAction(pcl4)
        self.parcelmenu.setEnabled(False)
        self.popupmenu=QMenu("Cursor Type:")
        ag = QtGui.QActionGroup(self, exclusive=True)

        nocurs = QAction(self)
        nocurs.setText("No Cursor")
        nocurs.setCheckable(True)
        nocurs.setChecked(True)
        nocurs.triggered.connect(self.setNoCursor)
        a = ag.addAction(nocurs)
        self.popupmenu.addAction(a)

        storm_motion = QAction(self)
        storm_motion.setText("Readout Cursor")
        storm_motion.setCheckable(True)
        storm_motion.triggered.connect(self.setReadoutCursor)
        a = ag.addAction(storm_motion)
        self.popupmenu.addAction(a)

        self.popupmenu.addSeparator()
        self.popupmenu.addMenu(self.parcelmenu)

        #odify_sfc = QAction(self)
        #modify_sfc.setText("Modify Surface")
        #modify_sfc.setCheckable(True)
        #modify_sfc.setEnabled(False)
        #modify_sfc.triggered.connect(self.setReadoutCursor)
        #self.popupmenu.addAction(modify_sfc)

        #self.interp_prof = QAction(self)
        #self.interp_prof.setText("Interpolate Profile")
        #self.interp_prof.setCheckable(True)
        #self.interp_prof.triggered.connect(self.interpProfile)
        #self.popupmenu.addAction(self.interp_prof)

        self.popupmenu.addSeparator()

        reset = QAction(self)
        reset.setText("Reset Skew-T")
        reset.triggered.connect(lambda: self.reset.emit(['tmpc', 'dwpc']))
        self.popupmenu.addAction(reset)

    def liftparcellevel(self, i):
        pres = self.pix_to_pres( self.cursor_loc.y())
        tmp = tab.interp.temp(self.prof, pres)
        dwp = tab.interp.dwpt(self.prof, pres)
        if i == 0:

            usrpcl = tab.params.parcelx(self.prof, flag=5, pres=pres, tmpc=tmp, dwpc=dwp)
        else:
            if i == -9999:
                depth, result = QInputDialog.getText(None, "Parcel Depth (" + str(int(pres)) + "to __)",\
                                            "Mean Layer Depth (mb):")
                try:
                    i = int(depth)
                except:
                    return
            user_initpcl = tab.params.DefineParcel(self.prof, flag=4, pbot=pres, pres=i)
            usrpcl = tab.params.parcelx(self.prof, pres=user_initpcl.pres, tmpc=user_initpcl.tmpc,\
                                          dwpc=user_initpcl.dwpc)
        self.parcel.emit(usrpcl) # Emit a signal that a new profile has been created

    def setProf(self, prof, **kwargs):
        self.prof = prof
        self.pres = prof.pres; self.hght = prof.hght
        self.tmpc = prof.tmpc; self.dwpc = prof.dwpc
        self.dew_stdev = prof.dew_stdev
        self.tmp_stdev = prof.tmp_stdev
        self.u = prof.u; self.v = prof.v
        self.wetbulb = prof.wetbulb
        self.proflist = kwargs.get('proflist', None)
        self.interpWinds = kwargs.get('interpWinds', True)
        self.title = kwargs.get('title', '')

        self.clearData()
        self.plotData()
        if self.readout:
            self.updateReadout()
        self.update()

    def setParcel(self, parcel):
        self.pcl = parcel

        self.clearData()
        self.plotData()
        self.update()

    def setDGZ(self, flag):
        self.plotdgz = flag

        self.clearData()
        self.plotData()
        self.update()
        return

    def interpProfile(self):
        # Step 1, interpolate the profile to 25 mb pressure levels
        new_pres = np.arange(self.prof.pres[self.prof.sfc], self.prof.pres[self.prof.top], -25)
        new_dwp = tab.interp.dwpt(self.prof, new_pres)
        new_tmp = tab.interp.temp(self.prof, new_pres)
        new_hght = tab.interp.hght(self.prof, new_pres)
        new_wdir, new_wspd = tab.interp.vec(self.prof, new_pres)
        new_prof = tab.profile.create_profile(pres=new_pres, hght=new_hght, tmpc=new_tmp, dwpc=new_dwp, wspd=new_wspd, wdir=new_wdir, profile='convective', missing=self.prof.missing)
        self.interp_prof.setEnabled(False)

        # Step 2, emit the signal that a new profile has been created
        self.updated.emit(new_prof, 'skew', True, self.pcl)

    def mouseReleaseEvent(self, e):
        if not self.was_right_click and self.readout:
            self.track_cursor = not self.track_cursor
            self.cursor_loc = e.pos()
        if self.dragging:
            trans_inv = self.transform.inverted()[0]
            trans_x = (e.x() - self.originx) * self.scale
            trans_y = (e.y() - self.originy) * self.scale
            tmpc = self.pix_to_tmpc(trans_x, trans_y)
            prof_name, prof = self.drag_prof

            if prof_name == 'tmpc':
                tmpc = max(tmpc, self.dwpc[self.drag_idx])
            elif prof_name == 'dwpc':
                tmpc = min(tmpc, self.tmpc[self.drag_idx])

            self.modified.emit(self.drag_idx, {prof_name:tmpc})

            self.drag_idx = None
            self.dragging = False
            self.saveBitMap = None

        elif self.initdrag:
            self.initdrag = False

        self.was_right_click = False
        self.drag_prof = None

    def mousePressEvent(self, e):
        if self.prof is None:
            return

        self.was_right_click = e.button() & QtCore.Qt.RightButton

        if not self.was_right_click and not self.readout:
            self.initDrag(e)

    def initDrag(self, e):
        prof_ys = self.pres_to_pix(self.pres)
        tmpc_xs = self.tmpc_to_pix(self.tmpc, self.pres)
        dwpc_xs = self.tmpc_to_pix(self.dwpc, self.pres)

        trans_x = (e.x() - self.originx) * self.scale
        trans_y = (e.y() - self.originy) * self.scale

        dist_tmpc = np.min(np.hypot(tmpc_xs - trans_x, prof_ys - trans_y))
        dist_dwpc = np.min(np.hypot(dwpc_xs - trans_x, prof_ys - trans_y))

        self.initdrag = True
        if dist_tmpc <= self.clickradius and dist_dwpc > self.clickradius:
            # Temperature was in the click radius and dewpoint wasn't; take the temperature
            prof_name = 'tmpc'
        elif dist_dwpc <= self.clickradius and dist_tmpc > self.clickradius:
            # Dewpoint was within the click radius and temperature wasn't; take the dewpoint
            prof_name = 'dwpc'
        elif dist_tmpc <= self.clickradius and dist_dwpc <= self.clickradius:
            # Both profiles have points within the click radius
            if dist_tmpc < dist_dwpc:
                # The temperature point is closer than the dewpoint point, so take the temperature
                prof_name = 'tmpc'
            elif dist_dwpc < dist_tmpc:
                # The dewpoint point is closer than the temperature point, so take the dewpoint
                prof_name = 'dwpc'
            else:
                # They were both the same distance away (probably a saturated profile).  If the click
                #   was to the left, take the dewpoint, if it was to the right, take the temperature.
                idx = np.argmin(np.abs(prof_ys - trans_y))
                prof_x = self.tmpc_to_pix(self.tmpc[idx], self.pres[idx])
                if trans_x < prof_x:
                    prof_name = 'dwpc'
                else:
                    prof_name = 'tmpc'
        else:
            # Click wasn't within range of any points.  Move along, folks, nothing to see here.
            self.initdrag = False

        if self.initdrag:
            self.drag_prof = (prof_name, self.__dict__[prof_name])

    def mouseMoveEvent(self, e):
        if self.track_cursor:
            self.readout_pres = self.pix_to_pres((e.y() - self.originy) * self.scale)
            self.updateReadout()

        elif self.initdrag or self.dragging:
            self.dragging = True
            self.initdrag = False
            self.dragLine(e)

    def updateReadout(self):
        y = self.originy + self.pres_to_pix(self.readout_pres) / self.scale
        hgt = tab.interp.to_agl( self.prof, tab.interp.hght(self.prof, self.readout_pres) )
        tmp = tab.interp.temp(self.prof, self.readout_pres)
        dwp = tab.interp.dwpt(self.prof, self.readout_pres)

        self.rubberBand.setGeometry(QRect(QPoint(self.lpad,y), QPoint(self.brx,y)).normalized())
        self.presReadout.setFixedWidth(60)
        self.hghtReadout.setFixedWidth(65)
        self.tmpcReadout.setFixedWidth(45)
        self.dwpcReadout.setFixedWidth(45)
        self.presReadout.setText(tab.utils.FLOAT2STR(self.readout_pres, 1) + ' hPa')
        self.hghtReadout.setText(tab.utils.FLOAT2STR(hgt, 1) + ' m')
        self.tmpcReadout.setText(tab.utils.FLOAT2STR(tmp, 1) + ' C')
        self.dwpcReadout.setText(tab.utils.FLOAT2STR(dwp, 1) + ' C')

        self.presReadout.move(self.lpad, y)
        self.hghtReadout.move(self.lpad, y - 15)
        self.tmpcReadout.move(self.brx-self.rpad, y)
        self.dwpcReadout.move(self.brx-self.rpad, y - 15)
        self.rubberBand.show()

    def dragLine(self, e):
        trans_x = (e.x() - self.originx) * self.scale
        trans_y = (e.y() - self.originy) * self.scale
        tmpc = self.pix_to_tmpc(trans_x, trans_y)

        if self.drag_idx is None:
            pres = self.pix_to_pres(trans_y)
            idx = np.argmin(np.abs(pres - self.pres))
            while self.tmpc.mask[idx] or self.dwpc.mask[idx]:
                idx += 1
            self.drag_idx = idx
        else:
            idx = self.drag_idx
 
        prof_name, drag_prof = self.drag_prof

        if prof_name == 'tmpc':
            tmpc = max(tmpc, self.dwpc[idx])
        elif prof_name == 'dwpc':
            tmpc = min(tmpc, self.tmpc[idx])

        # Figure out the bounds of the box we need to update
        if idx == 0 or self.pres.mask[idx - 1] or self.tmpc.mask[idx - 1] or self.dwpc.mask[idx - 1]:
            lb_p, ub_p = self.pres[idx], self.pres[idx + 1]
            t_points = [ (tmpc, self.pres[idx]), (drag_prof[idx + 1], self.pres[idx + 1]) ]
        elif idx == self.pres.shape[0] - 1:
            lb_p, ub_p = self.pres[idx - 1], self.pres[idx]
            t_points = [ (drag_prof[idx - 1], self.pres[idx - 1]), (tmpc, self.pres[idx]) ]
        else:
            lb_p, ub_p = self.pres[idx - 1], self.pres[idx + 1]
            t_points = [ (drag_prof[idx - 1], self.pres[idx - 1]), (tmpc, self.pres[idx]), (drag_prof[idx + 1], self.pres[idx + 1]) ]

        x_points = [ self.tmpc_to_pix(*pt) for pt in t_points ]
        lb_x = self.originx + min(x_points) / self.scale
        ub_x = self.originx + max(x_points) / self.scale
        lb_y = self.originy + self.pres_to_pix(ub_p) / self.scale
        ub_y = self.originy + self.pres_to_pix(lb_p) / self.scale

        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        # If we have something saved, restore it
        if self.saveBitMap is not None:
            origin, size, bmap = self.saveBitMap
            qp.drawPixmap(origin, bmap, QRect(QPoint(0, 0), size))

        # Capture the new portion of the image to save
        origin = QPoint(max(lb_x - self.drag_buffer, 0), max(lb_y - self.drag_buffer, 0))
        size = QSize(ub_x - lb_x + 2 * self.drag_buffer, ub_y - lb_y + 2 * self.drag_buffer)
        bmap = self.plotBitMap.copy(QRect(origin, size))
        self.saveBitMap = (origin, size, bmap)

        # Draw lines
        if prof_name == 'dwpc':
            color = QtGui.QColor("#019B06")
        else:
            color = QtGui.QColor("#9F0101")
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        if idx != 0 and not self.pres.mask[idx - 1] and not self.tmpc.mask[idx - 1] and not self.dwpc.mask[idx - 1]:
            x1 = self.originx + self.tmpc_to_pix(drag_prof[idx - 1], self.pres[idx - 1]) / self.scale
            x2 = self.originx + self.tmpc_to_pix(tmpc, self.pres[idx]) / self.scale
            y1 = self.originy + self.pres_to_pix(self.pres[idx - 1]) / self.scale
            y2 = self.originy + self.pres_to_pix(self.pres[idx]) / self.scale
            qp.drawLine(x1, y1, x2, y2)
        if idx != self.pres.shape[0] - 1:
            x1 = self.originx + self.tmpc_to_pix(tmpc, self.pres[idx]) / self.scale
            x2 = self.originx + self.tmpc_to_pix(drag_prof[idx + 1], self.pres[idx + 1]) / self.scale
            y1 = self.originy + self.pres_to_pix(self.pres[idx]) / self.scale
            y2 = self.originy + self.pres_to_pix(self.pres[idx + 1]) / self.scale
            qp.drawLine(x1, y1, x2, y2)

        qp.end()
        self.update()

    def setReadoutCursor(self):
        self.parcelmenu.setEnabled(True)
        self.readout = True
        self.track_cursor = True
        self.presReadout.show()
        self.hghtReadout.show()
        self.tmpcReadout.show()
        self.dwpcReadout.show()
        self.rubberBand.show()
        self.clearData()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def setNoCursor(self):
        self.parcelmenu.setEnabled(False)
        self.readout = False
        self.track_cursor = False
        self.presReadout.hide()
        self.hghtReadout.hide()
        self.tmpcReadout.hide()
        self.dwpcReadout.hide()      
        self.rubberBand.hide()
        self.clearData()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.

        '''
        super(plotSkewT, self).resizeEvent(e)
        self.plotData()

    def closeEvent(self, e):
        pass

    def showCursorMenu(self, pos):
        if self.cursor_loc is None or self.track_cursor:
            self.cursor_loc = pos
        self.popupmenu.popup(self.mapToGlobal(pos))

    def wheelEvent(self, e):
        super(plotSkewT, self).wheelEvent(e)
        self.plotBitMap.fill(QtCore.Qt.black)
        if self.readout:
            self.updateReadout()
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
        self.plotBitMap = self.backgroundBitMap.copy(0, 0, self.width(), self.height())
    
    def plotData(self):
        '''
        Plot the data used in a Skew-T.

        '''
        if self.prof is None:
            return

        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setClipRect(self.clip)

        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.drawTitle(qp)
        if self.proflist is not None:
            for profile in self.proflist:
                #purple #666699
                self.drawTrace(profile.tmpc, QtGui.QColor("#6666CC"), qp, p=profile.pres)
                self.drawTrace(profile.dwpc, QtGui.QColor("#6666CC"), qp, p=profile.pres)
                #self.drawVirtualParcelTrace(profile.mupcl.ttrace, profile.mupcl.ptrace, qp, color="#666666")
                self.drawBarbs(profile, qp, color="#6666CC")
        self.drawTrace(self.wetbulb, QtGui.QColor(self.wetbulb_color), qp, width=1)
        self.drawTrace(self.tmpc, QtGui.QColor(self.temp_color), qp, stdev=self.tmp_stdev)

        if self.plotdgz is True and (self.prof.dgz_pbot != self.prof.dgz_ptop):
#           idx = np.ma.where((self.prof.pres <= self.prof.dgz_pbot) & (self.prof.pres >= self.prof.dgz_ptop))
#           idx_pbot, idx_ptop = np.searchsorted(np.array([self.prof.dgz_pbot, self.prof.dgz_ptop]), self.prof.pres)

            pres = np.ma.masked_invalid(np.arange(self.prof.dgz_ptop, self.prof.dgz_pbot, 5)[::-1])
            tmpc = np.ma.masked_invalid(tab.interp.temp(self.prof, pres))

            self.drawTrace(tmpc, QtGui.QColor("#F5D800"), qp, p=pres, label=False)
            self.draw_sig_levels(qp, plevel=self.prof.dgz_pbot, color="#F5D800")
            self.draw_sig_levels(qp, plevel=self.prof.dgz_ptop, color="#F5D800")

        self.drawTrace(self.dwpc, QtGui.QColor(self.dewp_color), qp, stdev=self.dew_stdev)

        for h in [0,1000.,3000.,6000.,9000.,12000.,15000.]:
            self.draw_height(h, qp)
        if self.pcl is not None:
            self.dpcl_ttrace = self.prof.dpcl_ttrace
            self.dpcl_ptrace = self.prof.dpcl_ptrace
            self.drawVirtualParcelTrace(self.pcl.ttrace, self.pcl.ptrace, qp)
            self.drawVirtualParcelTrace(self.dpcl_ttrace, self.dpcl_ptrace, qp, color="#FF00FF")
        self.draw_parcel_levels(qp)
        qp.setRenderHint(qp.Antialiasing, False)
        self.drawBarbs(self.prof, qp)
        qp.setRenderHint(qp.Antialiasing)

        self.draw_effective_layer(qp)
        if self.plot_omega:
            self.draw_omega_profile(qp)

        qp.end()

    def drawBarbs(self, prof, qp, color="#FFFFFF"):
        qp.setClipping(True)

        rect_size = self.clip.size()
        rect_size.setHeight(rect_size.height() + self.bpad / 2)
        mod_clip = QRect(self.clip.topLeft(), rect_size)
        qp.setClipRect(mod_clip)

        if self.interpWinds is False:
            i = 0
            mask1 = prof.u.mask
            mask2 = prof.pres.mask
            mask = np.maximum(mask1, mask2)
            pres = prof.pres[~mask]
            u = prof.u[~mask]
            v = prof.v[~mask]
            wdir, wspd = tab.utils.comp2vec(u, v)
            yvals = self.originy + self.pres_to_pix(pres) / self.scale
            for y in yvals:
                dd = wdir[i]
                ss = wspd[i]
                drawBarb( qp, self.barbx, y, dd, vv )
                i += 1
        else:
            pres = np.arange(prof.pres[prof.sfc], prof.pres[prof.top], -40)
            wdir, wspd = tab.interp.vec(prof, pres)
            for p, dd, ss in zip(pres, wdir, wspd):
                if not tab.utils.QC(dd) or np.isnan(ss) or p < self.pmin:
                    continue

                y = self.originy + self.pres_to_pix(p) / self.scale
                drawBarb( qp, self.barbx, y, dd, ss, color=color)
        qp.setClipRect(self.clip)

    def drawTitle(self, qp):
        qp.setClipping(False)
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(self.lpad, 0, 150, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, self.title)
    
    
    def draw_height(self, h, qp):
        qp.setClipping(True)
        self.hght_font = QtGui.QFont('Helvetica', 9)
        pen = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.hght_font)
        offset = 10
        txt_offset = 15 
        sfc = tab.interp.hght( self.prof, self.prof.pres[self.prof.sfc] )
        p1 = tab.interp.pres(self.prof, h+sfc)
        if np.isnan(p1) == False:
            y1 = self.originy + self.pres_to_pix(p1) / self.scale
            qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
            qp.drawText(self.lpad+txt_offset, y1-20, self.lpad+txt_offset, 40,
                QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,
                tab.utils.INT2STR(h/1000)+' km')

    def draw_sig_levels(self, qp, plevel=1000, color="#FFFFFF"):
        qp.setClipping(True)
        if not tab.utils.QC(plevel):
            return
        xbounds = [37,45]
        z = tab.utils.M2FT(tab.interp.hght(self.prof, plevel))

        x = self.tmpc_to_pix(xbounds, [1000.,1000.])
        y = self.originy + self.pres_to_pix(plevel) / self.scale
        pen = QtGui.QPen(QtGui.QColor(color), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(x[0], y, x[1], y)
        rect1 = QtCore.QRectF(self.tmpc_to_pix(29, 1000.), y-3, x[1] - x[0], 4) 
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.INT2STR(z) + '\'')
        

    def draw_parcel_levels(self, qp):
        if self.pcl is None:
            return
        qp.setClipping(True)
        xbounds = [37,41]
        x = self.tmpc_to_pix(xbounds, [1000.,1000.])
        lclp = self.pcl.lclpres
        lfcp = self.pcl.lfcpres
        elp = self.pcl.elpres

        # Plot LCL
        if lclp is not np.ma.masked:
            y = self.originy + self.pres_to_pix(lclp) / self.scale
            pen = QtGui.QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(x[0], y, x[1], y)
            rect1 = QtCore.QRectF(x[0], y+6, x[1] - x[0], 4) 
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "LCL")
        # Plot LFC
        if lfcp is not np.ma.masked:
            y = self.originy + self.pres_to_pix(lfcp) / self.scale
            pen = QtGui.QPen(QtCore.Qt.yellow, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(x[0], y, x[1], y)
            rect2 = QtCore.QRectF(x[0], y-8, x[1] - x[0], 4) 
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "LFC")
        # Plot EL
        if elp is not np.ma.masked and elp != lclp:
            y = self.originy + self.pres_to_pix(elp) / self.scale
            pen = QtGui.QPen(QtCore.Qt.magenta, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(x[0], y, x[1], y)
            rect3 = QtCore.QRectF(x[0], y-8, x[1] - x[0], 4) 
            qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, "EL")

    def omeg_to_pix(self, omeg):
        plus10_bound = -49
        minus10_bound = -41
        x1_m10 = self.tmpc_to_pix(minus10_bound, 1000)
        x1_10 = self.tmpc_to_pix(plus10_bound, 1000)
        x1_0 = self.tmpc_to_pix((plus10_bound + minus10_bound)/2., 1000)
        if omeg > 0:
            return ((x1_0 - x1_10)/(0.-10.)) * omeg + x1_0    
        elif omeg < 0:
            return ((x1_0 - x1_m10)/(0.+10.)) * omeg + x1_0 
        else:
            return x1_0

    def draw_omega_profile(self, qp):
        qp.setClipping(True)
        plus10_bound = -49
        minus10_bound = -41
        x1 = self.tmpc_to_pix((plus10_bound + minus10_bound)/2., 1000)

        for i in range(len(self.prof.omeg)):
            pres_y = self.originy + self.pres_to_pix(self.prof.pres[i]) / self.scale
            if self.prof.omeg[i] == np.ma.masked or self.prof.pres[i] < 111:
                continue
            if self.prof.omeg[i] > 0:
                pen = QtGui.QPen(QtGui.QColor("#0066CC"), 1.5, QtCore.Qt.SolidLine)
            elif self.prof.omeg[i] < 0:
                pen = QtGui.QPen(QtGui.QColor("#FF6666"), 1.5, QtCore.Qt.SolidLine)
            else:
                pen = QtGui.QPen(QtCore.Qt.magenta, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)                
            x2 = self.omeg_to_pix(self.prof.omeg[i]*10.)
            qp.drawLine(x1, pres_y, x2, pres_y)


    def draw_effective_layer(self, qp):
        '''
        Draw the bounds of the effective inflow layer.
        '''
        qp.setClipping(True)
        ptop = self.prof.etop; pbot = self.prof.ebottom
        len = 15
        text_offset = 10
        if ptop is np.ma.masked and pbot is np.ma.masked:
            pass
        else:
            x1 = self.tmpc_to_pix(-20, 1000)
            x2 = self.tmpc_to_pix(-33, 1000)
            y1 = self.originy + self.pres_to_pix(pbot) / self.scale
            y2 = self.originy + self.pres_to_pix(ptop) / self.scale
            rect1 = QtCore.QRectF(x2, y1+4, 25, self.esrh_height)
            rect2 = QtCore.QRectF(x2, y2-self.esrh_height, 50, self.esrh_height)
            rect3 = QtCore.QRectF(x1-15, y2-self.esrh_height, 50, self.esrh_height)
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
            qp.setFont(self.esrh_font)
            qp.drawLine(x1-len, y1, x1+len, y1)
            qp.drawLine(x1-len, y2, x1+len, y2)
            qp.drawLine(x1, y1, x1, y2)
            qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text_bot)
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text_top)
            qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft,
                tab.utils.INT2STR(self.prof.right_esrh[0]) + ' m2s2')
           # qp.drawText(x1-2*len, y1-text_offset, 40, 40,
           #     QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
           #     text_bot)
    
    def drawVirtualParcelTrace(self, ttrace, ptrace, qp, width=1, color="#FFFFFF"):
        '''
        Draw a parcel trace.
        '''
        qp.setClipping(True)
        pen = QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.DashLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        path = QPainterPath()
        if not tab.utils.QC(ptrace):
            return
        yvals = self.originy + self.pres_to_pix(ptrace) / self.scale
        xvals = self.originx + self.tmpc_to_pix(ttrace, ptrace) / self.scale
        path.moveTo(xvals[0], yvals[0])
        for i in xrange(1, len(yvals)):
            x = xvals[i]; y = yvals[i]
#           if y < self.tpad:
#               break
#           else:
            path.lineTo(x, y)
        qp.drawPath(path)

    def drawTrace(self, data, color, qp, width=3, p=None, stdev=None, label=True):
        '''
        Draw an environmental trace.

        '''
        qp.setClipping(True)
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
        x = self.originx + self.tmpc_to_pix(data, pres) / self.scale
        y = self.originy + self.pres_to_pix(pres) / self.scale

        path.moveTo(x[0], y[0])
        for i in xrange(1, x.shape[0]):
            path.lineTo(x[i], y[i])
            if stdev is not None:
                self.drawSTDEV(pres[i], data[i], stdev[i], color, qp)

        qp.drawPath(path)

        if label is True:
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

