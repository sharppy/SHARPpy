import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.viz.draggable import Draggable
from sharppy.sharptab.profile import Profile, create_profile
from sharppy.sharptab.constants import *
from PySide.QtGui import *
from PySide.QtCore import *

__all__ = ['backgroundHodo', 'plotHodo']


class backgroundHodo(QtGui.QFrame):
    '''
    Handles the plotting of the backgroun frame onto
    a QPixmap. Inherits from the QtGui.QFrame object.
    Unlike most plotting classes in SHARPPy, this class
    will not call the function to draw the background.
    This is so that the background can be redrawn when 
    the hodograph gets centered on a vector.
    '''
    def __init__(self, **kwargs):
        super(backgroundHodo, self).__init__(**kwargs)
        self.wind_units = kwargs.get('wind_units', 'knots')

        self.hodomag = 160.
        ## ring increment
        self.ring_increment = 10
        self.min_zoom = 40.
        self.max_zoom = 200.

        self.initUI()

    def initUI(self):
        '''
        Initialize the User Interface

        '''
        ## set the interface variables for width, height, padding, etc.
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 0
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## set default center to the origin
        self.point = (0,0)
        self.centerx = self.wid / 2; self.centery = self.hgt / 2
        self.scale = (self.brx - self.tlx) / self.hodomag
        self.rings = range(self.ring_increment, 100+self.ring_increment,
            self.ring_increment)
        if self.physicalDpiX() > 75:
            fsize = 7
        else:
            fsize = 9
        self.label_font = QtGui.QFont('Helvetica', fsize + (self.hgt * 0.0045))
        self.label_font.setBold(True)
        self.critical_font = QtGui.QFont('Helvetica', fsize + 2 +  (self.hgt * 0.0045))
        self.critical_font.setBold(True)
        self.readout_font = QtGui.QFont('Helvetica', 11 +  (self.hgt * 0.0045))
        self.readout_font.setBold(True)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.critical_metrics = QtGui.QFontMetrics( self.critical_font )
        self.label_height = self.label_metrics.xHeight() + 5 +  (self.hgt * 0.0045)
        self.critical_height = self.critical_metrics.xHeight() + 5 +  (self.hgt * 0.0045)

        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.saveBitMap = None
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
        self.backgroundBitMap = self.plotBitMap.copy()

    def center_hodo(self, point):
        '''
        Center the hodograph in the window. It will either center it about
        the origin, about the mean wind vector, or the storm motion vector.
        
        Parameters
        ----------
        point: A (u,v) vector that the hodograph is to be centered on.

        '''
        ## modify the center based on an offset from the origin
        centerx = self.wid / 2; centery = self.hgt / 2
        point = self.uv_to_pix(point[0], point[1])
        ## if the function was called but the center hasn't changed in pixel space,
        ## just leave the center as is
        if self.point == point:
            self.centerx = self.centerx
            self.centery = self.centery
        ## otherwise, offset the hodograph center
        else:
            self.point = point
            diffx = centerx - point[0]; diffy = centery - point[1]
            self.centerx += diffx; self.centery += diffy
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
        self.backgroundBitMap = self.plotBitMap.copy()

    def wheelEvent(self, e):
        '''
        Handeles the zooming of the hodograph window.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        ## get the new scaling magnitude
        new_mag = self.hodomag - e.delta() / 5
        ## make sure the user doesn't zoom out of
        ## bounds to prevent drawing issues
        if new_mag >= self.min_zoom and new_mag <= self.max_zoom:
            self.hodomag = new_mag
        ## if it is out of bounds, do nothing
        else:
            self.hodomag = self.hodomag

        if self.wind_units == 'm/s':
            conv = tab.utils.KTS2MS
        else:
            conv = lambda s: s
        ## get the maximum speed value in the frame for the ring increment.
        ## this is to help reduce drawing resources
        max_uv = int(conv(np.hypot(*self.pix_to_uv(self.brx, self.bry))))
        self.rings = range(self.ring_increment, max_uv+self.ring_increment,
                           self.ring_increment)
        ## reassign the new scale
        self.scale = (self.brx - self.tlx) / self.hodomag

        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
        self.backgroundBitMap = self.plotBitMap.copy()
        self.plotData()

        ## update
        self.update()

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.
        
        Parameters
        ----------
        e: an Event object

        '''
        self.initUI()

    def plotBackground(self):
        '''
        Handles painting the frame background onto the
        QPixmap.
        '''
        ## initialize a QPainter object.
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the wind speed rings
        for spd in self.rings: self.draw_ring(spd, qp)
        ## draw the frame axes
        self.draw_axes(qp)
        self.draw_frame(qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draw frame around object.
        
        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame
        pen = QtGui.QPen(self.fg_color, 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame borders
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

    def draw_axes(self, qp):
        '''
        Draw the X, Y Axes.
        
        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## initialize a white pen to draw the frame axes
        pen = QtGui.QPen(self.fg_color, 2)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the frame axes
        qp.drawLine(self.centerx, self.tly, self.centerx, self.bry)
        qp.drawLine(self.tlx, self.centery, self.brx, self.centery)

    def draw_ring(self, spd, qp):
        '''
        Draw a range ring.
        
        Parameters
        ----------
        spd: wind speed
        qp: QtGui.QPainter object

        '''
        ## set the ring color and get the u and v components of a
        ## 0 direction vector with speed spd.
        color = self.isotach_color 
        uu, vv = tab.utils.vec2comp(0, spd)
        vv *= self.scale
        ## create a center point
        center = QtCore.QPointF(self.centerx, self.centery)
        ## initialize a pen to draw with
        pen = QtGui.QPen(QtGui.QColor(color), 1)
        pen.setStyle(QtCore.Qt.DashLine)
        qp.setPen(pen)
        ## draw the range ring
        qp.drawEllipse(center, vv, vv)
        qp.setFont(self.label_font)
        ## reset the pen to draw with. Color is set to black and width zero
        ## because we actually don't want to draw and lines yet.
        pen = QtGui.QPen(self.bg_color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        offset = 5; width = 15; hght = 15;
        ## crete some rectangles
        top_rect = QtCore.QRectF(self.centerx+offset,
                    self.centery+vv-offset, width, hght)
        bottom_rect = QtCore.QRectF(self.centerx+offset,
                    self.centery-vv-offset, width, hght)

        right_rect = QtCore.QRectF(self.centerx+vv-offset,
                    self.centery+offset, width, hght)
        left_rect = QtCore.QRectF(self.centerx-vv-offset,
                    self.centery+offset, width, hght)
        ## draw some invisible rectangles
        qp.drawRect(top_rect); qp.drawRect(right_rect)
        qp.drawRect(bottom_rect); qp.drawRect(left_rect)
        ## now make the pen white and draw text using
        ## the invisible rectangles
        pen = QtGui.QPen(self.fg_color)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        qp.drawText(top_rect, QtCore.Qt.AlignCenter, tab.utils.INT2STR(spd))
        qp.drawText(right_rect, QtCore.Qt.AlignCenter, tab.utils.INT2STR(spd))
        qp.drawText(bottom_rect, QtCore.Qt.AlignCenter, tab.utils.INT2STR(spd))
        qp.drawText(left_rect, QtCore.Qt.AlignCenter, tab.utils.INT2STR(spd))

    def hodo_to_pix(self, ang, spd):
        '''
        Function to convert a (direction, speed) to (x, y) coordinates.
        
        Parameters
        ----------
        ang: wind direction
        spd: wind speed

        '''
        uu, vv = tab.utils.vec2comp(ang, spd)
        xx = self.centerx + (uu * self.scale)
        yy = self.centery + (vv * self.scale)
        return xx, yy

    def uv_to_pix(self, u, v):
        '''
        Function to convert (u, v) to (x, y) coordinates.
        
        Parameters
        ----------
        u: the u wind component
        v: the v wind component

        '''
        if self.wind_units == 'm/s':
            conv = tab.utils.KTS2MS
        else:
            conv = lambda s: s

        xx = self.centerx + (conv(u) * self.scale)
        yy = self.centery - (conv(v) * self.scale)
        return xx, yy

    def pix_to_uv(self, xx, yy):
        '''
        Function to convert (x,y) to (u,v) coordinates.
        
        Parameters
        ----------
        xx: the x pixel value
        yy: the y pixel value
        
        '''
        if self.wind_units == 'm/s':
            conv = tab.utils.MS2KTS
        else:
            conv = lambda s: s

        u = conv((xx - self.centerx) / self.scale)
        v = conv((self.centery - yy) / self.scale)
        return u, v




class plotHodo(backgroundHodo):
    '''
    Plots the data on the hodograph. Inherits from the backgroundHodo
    class that plots the background frame onto a QPixmap.
    '''

    modified = Signal(int, dict)
    modified_vector = Signal(str, float, float)
    reset = Signal(list)
    reset_vector = Signal()
    toggle_vector = Signal(str)

    def __init__(self, **kwargs):
        '''
        Initialize the data used in the class.
        '''
        self.bg_color = QtGui.QColor("#000000")
        self.fg_color = QtGui.QColor("#FFFFFF")
        self.isotach_color = QtGui.QColor("#555555")

        super(plotHodo, self).__init__(**kwargs)
        self.prof = None
        self.pc_idx = 0
        self.prof_collections = []

        self.all_observed = False

        self.colors = [
            QtGui.QColor("#FF0000"), 
            QtGui.QColor("#00FF00"), 
            QtGui.QColor("#FFFF00"), 
            QtGui.QColor("#00FFFF") 
        ]

        self.ens_colors = [
            QtGui.QColor("#880000"), 
            QtGui.QColor("#008800"), 
            QtGui.QColor("#888800"), 
            QtGui.QColor("#008888") 
        ]

        self.eff_inflow_color = QtGui.QColor("#00FFFF")
        self.crit_color = QtGui.QColor("#00FFFF")

        self.use_left = False

        self.background_colors = kwargs.get('background_colors', ['#6666CC', '#CC9966', '#66CC99'])
        ## if you want the storm motion vector, you need to
        ## provide the profile.
        self.cursor_type = kwargs.get('cursor', 'none')
        self.bndy_spd = kwargs.get('bndy_spd', 0)
        self.bndy_dir = kwargs.get('bndy_dir', 0)
        self.bndy_u, self.bndy_v = tab.utils.vec2comp(self.bndy_dir, self.bndy_spd)

        self.track_cursor = False
        self.was_right_click = False
        self.drag_hodo = None
        self.drag_lm = None
        self.drag_rm = None

        self.centered = kwargs.get('centered', (0,0))
        self.center_loc = 'centered'

        ## the following is used for the dynamic readout
        self.setMouseTracking(True)
        self.bndyReadout = QLabel(parent=self)
        self.bndyReadout.setFixedWidth(0)

        ## these stylesheets have to be set for
        ## each readout
        self.bndyReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #00FF00;}")

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showCursorMenu)
        self.popupmenu=QMenu("Cursor Type:")
        ag = QtGui.QActionGroup(self, exclusive=True)

        self.readout_hght = -999.
        self.readout_visible = False

        nocurs = QAction(self)
        nocurs.setText("No Cursor")
        nocurs.setCheckable(True)
        nocurs.setChecked(True)
        nocurs.triggered.connect(self.setNoCursor)
        a = ag.addAction(nocurs)
        self.popupmenu.addAction(a)

        bnd = QAction(self)
        bnd.setText("Bndy Cursor")
        bnd.setCheckable(True)
        bnd.triggered.connect(self.setBndyCursor)
        a = ag.addAction(bnd)
        self.popupmenu.addAction(a)

        self.popupmenu.addSeparator()
        ag2 = QtGui.QActionGroup(self, exclusive=True)

        norm = QAction(self)
        norm.setText("Normal")
        norm.setCheckable(True)
        norm.setChecked(True)
        norm.triggered.connect(self.setNormalCenter)
        a = ag2.addAction(norm)        
        self.popupmenu.addAction(a)

        sr = QAction(self)
        sr.setText("Storm Relative")
        sr.setCheckable(True)
        sr.triggered.connect(self.setSRCenter)       
        a = ag2.addAction(sr)
        self.popupmenu.addAction(a)

        mw = QAction(self)
        mw.setText("Mean Wind")
        mw.setCheckable(True)
        mw.triggered.connect(self.setMWCenter)
        a = ag2.addAction(mw)
        self.popupmenu.addAction(a)

        self.popupmenu.addSeparator()
        
        reset = QAction(self)
        reset.setText("Reset Hodograph")
        reset.triggered.connect(lambda: self.reset.emit(['u', 'v']))
        self.popupmenu.addAction(reset)

        reset_vec = QAction(self)
        reset_vec.setText("Reset Storm Motion")
        reset_vec.triggered.connect(lambda: self.reset_vector.emit())
        self.popupmenu.addAction(reset_vec)

    def addProfileCollection(self, prof_coll):
        self.prof_collections.append(prof_coll)

    def rmProfileCollection(self, prof_coll):
        self.prof_collections.remove(prof_coll)

    def setActiveCollection(self, pc_idx, **kwargs):
        self.pc_idx = pc_idx
        prof = self.prof_collections[pc_idx].getHighlightedProf()

        self.prof = prof
        self.hght = prof.hght
        hght_agl = tab.interp.to_agl(self.prof, self.hght)
        self.u = prof.u; self.v = prof.v

        cutoff_msl = tab.interp.to_msl(self.prof, 12000.)
        u_12km = tab.interp.generic_interp_hght(12000., hght_agl, self.u)
        v_12km = tab.interp.generic_interp_hght(12000., hght_agl, self.v)

        idx_12km = np.searchsorted(hght_agl, 12000.)
        self.u = np.ma.append(self.u[:idx_12km], np.ma.append(u_12km, self.u[idx_12km:]))
        self.v = np.ma.append(self.v[:idx_12km], np.ma.append(v_12km, self.v[idx_12km:]))
        self.hght = np.ma.append(self.hght[:idx_12km], np.ma.append(cutoff_msl, self.hght[idx_12km:]))
        hght_agl = tab.interp.to_agl(self.prof, self.hght)

        ## if you want the storm motion vector, you need to
        ## provide the profile.
        self.srwind = self.prof.srwind
        self.ptop = self.prof.etop
        self.pbottom = self.prof.ebottom

        xs, ys = self.uv_to_pix(self.u[hght_agl <= 12000.], self.v[hght_agl <= 12000.])
        self.drag_hodo = Draggable(xs, ys, self.plotBitMap, line_color=self.fg_color)
        rm_x, rm_y = self.uv_to_pix(self.srwind[0], self.srwind[1])
        self.drag_rm = Draggable(rm_x, rm_y, self.plotBitMap, line_color=self.fg_color)
        lm_x, lm_y = self.uv_to_pix(self.srwind[2], self.srwind[3])
        self.drag_lm = Draggable(lm_x, lm_y, self.plotBitMap, line_color=self.fg_color)

        mean_lcl_el = self.prof.mean_lcl_el
        if tab.utils.QC(mean_lcl_el[0]):
            self.mean_lcl_el = tab.utils.vec2comp(*self.prof.mean_lcl_el)
        else:
            self.mean_lcl_el = (np.ma.masked, np.ma.masked)

        self.corfidi_up_u = self.prof.upshear_downshear[0]
        self.corfidi_up_v = self.prof.upshear_downshear[1]
        self.corfidi_dn_u = self.prof.upshear_downshear[2]
        self.corfidi_dn_v = self.prof.upshear_downshear[3]
        self.bunkers_right_vec = tab.utils.comp2vec(self.prof.srwind[0], self.prof.srwind[1])
        self.bunkers_left_vec = tab.utils.comp2vec(self.prof.srwind[2], self.prof.srwind[3])
        self.upshear = tab.utils.comp2vec(self.prof.upshear_downshear[0],self.prof.upshear_downshear[1])
        self.downshear = tab.utils.comp2vec(self.prof.upshear_downshear[2],self.prof.upshear_downshear[3])
        self.mean_lcl_el_vec = self.prof.mean_lcl_el

        self.clearData()
        self.plotData()
        self.update()

    def setBndyCursor(self):
        self.track_cursor = True
        self.cursor_type = 'boundary'
        self.plotBndy(self.bndy_dir)
        self.bndyReadout.show()
        self.clearData()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def setNoCursor(self):
        self.track_cursor = False 
        self.cursor_type = 'none'
        self.unsetCursor()
        self.clearData()
        self.plotData()
        self.update()
        self.bndyReadout.hide()
        self.parentWidget().setFocus()

    def showCursorMenu(self, pos):
        self.popupmenu.popup(self.mapToGlobal(pos))

    def setNormalCenter(self):
        self.centered = (0, 0)
        self.center_loc = 'centered'
        self.clearData()
        self.center_hodo(self.centered)
        self.updateDraggables()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def setMWCenter(self):
        if not tab.utils.QC(self.mean_lcl_el[0]):
            return

        self.centered = (self.mean_lcl_el[0],self.mean_lcl_el[1])
        self.center_loc = 'meanwind'
        self.clearData()
        self.center_hodo(self.centered)
        self.updateDraggables()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def setSRCenter(self):
        rstu,rstv,lstu,lstv = self.srwind
        self.centered = (rstu, rstv)
        self.center_loc = 'stormrelative'
        self.clearData()
        self.center_hodo(self.centered)
        self.updateDraggables()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def setAllObserved(self, all_observed, update_gui=True):
        self.all_observed = all_observed

        if update_gui:
            self.clearData()
            self.plotData()
            self.update()
            self.parentWidget().setFocus()

    def setPreferences(self, update_gui=True, **kwargs):
        self.wind_units = kwargs['wind_units']

        self.bg_color = QtGui.QColor(kwargs['bg_color'])
        self.fg_color = QtGui.QColor(kwargs['fg_color'])
        self.isotach_color = QtGui.QColor(kwargs['hodo_itach_color'])
        self.crit_color = QtGui.QColor(kwargs['hodo_crit_color'])

        self.colors = [
            QtGui.QColor(kwargs['0_3_color']),
            QtGui.QColor(kwargs['3_6_color']),
            QtGui.QColor(kwargs['6_9_color']),
            QtGui.QColor(kwargs['9_12_color']),
        ]

        self.eff_inflow_color = QtGui.QColor(kwargs['eff_inflow_color'])

        if self.wind_units == 'm/s':
            self.ring_increment = 5
            self.hodomag = 80.
            self.min_zoom = 20.
            self.max_zoom = 100.
            conv = tab.utils.KTS2MS
        else:
            self.ring_increment = 10
            self.hodomag = 160.
            self.min_zoom = 40.
            self.max_zoom = 200.
            conv = lambda s: s         

        self.scale = (self.brx - self.tlx) / self.hodomag
        max_uv = int(conv(np.hypot(*self.pix_to_uv(self.brx, self.bry))))
        self.rings = range(self.ring_increment, max_uv+self.ring_increment,
                           self.ring_increment)

        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()
        self.backgroundBitMap = self.plotBitMap.copy()

        if update_gui:
            self.clearData()
            self.plotData()
            self.update()
            self.parentWidget().setFocus()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        self.clearData()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def wheelEvent(self, e):
        '''
        Handles the zooming of the hodograph.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotHodo, self).wheelEvent(e)
        self.updateDraggables()

    def mousePressEvent(self, e):
        '''
        Handles when the mouse is pressed.
        Used to set the storm motion vector.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        if self.prof is None:
            return

        self.was_right_click = e.button() & QtCore.Qt.RightButton

        if self.cursor_type == 'none' and not self.was_right_click:
            self.drag_rm.click(e.x(), e.y())
            self.drag_lm.click(e.x(), e.y())
            self.drag_hodo.click(e.x(), e.y())

    def mouseReleaseEvent(self, e):
        if self.prof is None:
            return

        if self.cursor_type == 'boundary' and not self.was_right_click:
            if self.track_cursor:
                qp = QtGui.QPainter()
                self.bndy_u, self.bndy_v = self.pix_to_uv(e.x(), e.y())
                self.bndy_dir, self.bndy_spd = tab.utils.comp2vec(self.bndy_u, self.bndy_v)
                y1 = 400*np.sin(np.radians(self.bndy_dir)) + e.y()
                x1 = 400*np.cos(np.radians(self.bndy_dir)) + e.x()
                y2 = e.y() - 400*np.sin(np.radians(self.bndy_dir))
                x2 = e.x() - 400*np.cos(np.radians(self.bndy_dir))
                penwidth = 2
                width = 300
                hght = 14
                # Plot the actual boundary 
                boundary_color = QtGui.QColor("#CC9900")
                pen = QtGui.QPen(boundary_color, penwidth)
                qp.begin(self.plotBitMap)
                qp.setRenderHint(qp.Antialiasing)
                qp.setRenderHint(qp.TextAntialiasing)
                qp.setPen(pen)
                qp.drawLine(x1, y1, x2, y2)
                center_rm = QtCore.QPointF(e.x(),e.y())
                qp.setPen(pen)
                pen = QtGui.QPen(boundary_color, 50)
                pen.setStyle(QtCore.Qt.SolidLine)
                qp.drawEllipse(center_rm, 3, 3)

                # Plot the shear vector
                width = 150
                qp = self.setBlackPen(qp)
                rect = QtCore.QRectF(3, self.bry-35, width, hght)
                qp.drawRect(rect)
                shear_color = QtGui.QColor("#0099CC")
                pen = QtGui.QPen(shear_color, penwidth)
                qp.setFont(self.critical_font)
                qp.setPen(pen)
                to_add = self.pix_to_uv(e.x(), e.y())
                x2, y2 = self.uv_to_pix(self.prof.sfc_6km_shear[0] + to_add[0], self.prof.sfc_6km_shear[1]+ to_add[1])
                qp.drawLine(e.x(), e.y(), x2, y2)
                dir, spd = tab.utils.comp2vec(self.prof.sfc_6km_shear[0], self.prof.sfc_6km_shear[1])
                qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, "0 - 6 km Shear: " + tab.utils.INT2STR(np.float64(dir)) + '/' + tab.utils.INT2STR(spd) + ' kts')

                # Plot the 9-11 km Storm Relative Winds
                width = 200
                qp = self.setBlackPen(qp)
                rect = QtCore.QRectF(3, self.bry-20, width, hght)
                qp.drawRect(rect)
                srw_color = QtGui.QColor("#FF00FF")
                pen = QtGui.QPen(srw_color, penwidth)
                qp.setPen(pen)
                if self.use_left:
                    srw_9_11km = self.prof.left_srw_9_11km
                else:
                    srw_9_11km = self.prof.right_srw_9_11km
                x2, y2 = self.uv_to_pix(srw_9_11km[0] + to_add[0], srw_9_11km[1] + to_add[1])
                qp.drawLine(e.x(), e.y(), x2, y2)
                dir, spd = tab.utils.comp2vec(srw_9_11km[0], srw_9_11km[1])
                if spd >= 70:
                    supercell_type = "LP"
                elif spd < 70 and spd > 40:
                    supercell_type = "Classic"
                else:
                    supercell_type = "HP"
                qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, "9 - 11 km SR-Wind: " + tab.utils.INT2STR(np.float64(dir)) + '/' + tab.utils.INT2STR(spd) + ' kts - (' + supercell_type + ')')
                # Removing this function until @wblumberg can finish fixing this function.
                """
                # Draw the descrete vs mixed/linear mode output only if there is an LCL-EL layer.
                norm_Shear, mode_Shear, norm_Wind, norm_Mode = self.calculateStormMode()
 
                if tab.utils.QC(norm_Wind) and self.prof.mupcl.bplus != 0:
                    width = 80
                    qp = self.setBlackPen(qp)
                    rect = QtCore.QRectF(3, self.bry-80, width, hght)
                    qp.drawRect(rect)
                    color = QtGui.QColor(YELLOW)
                    pen = QtGui.QPen(color, penwidth)
                    qp.setPen(pen)
                    qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, "...Storm Mode...")
                    
                    width = 270
                    qp = self.setBlackPen(qp)
                    rect = QtCore.QRectF(3, self.bry-50, width, hght)
                    qp.drawRect(rect)
                    if norm_Wind < 6:
                        color = QtGui.QColor(RED)
                    else:
                        color = QtGui.QColor(MAGENTA)
                    pen = QtGui.QPen(color, penwidth)
                    qp.setPen(pen)
                    qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, "From Cloud Layer Wind - Bndy Diff (" + tab.utils.INT2STR(norm_Wind) + " m/s): " + norm_Mode)
                    width = 200
                    
                    qp = self.setBlackPen(qp)
                    rect = QtCore.QRectF(3, self.bry-65, width, hght)
                    qp.drawRect(rect)
                    if norm_Shear < 15:
                        color = QtGui.QColor(RED)
                    else:
                        color = QtGui.QColor(MAGENTA)
                    pen = QtGui.QPen(color, penwidth)
                    qp.setPen(pen)
                    qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, "From Bndy 0-6 km Shr Diff (" + tab.utils.INT2STR(norm_Shear) + " m/s): " + mode_Shear)
                """
                qp.end()

                self.update()
                self.track_cursor = False
            else:
                self.plotBndy(self.bndy_dir)
                self.clearData()
                self.plotData()
                self.update()               
                self.track_cursor = True
        elif self.cursor_type == 'none':

            if self.drag_hodo.isDragging():
                drag_idx, rls_x, rls_y = self.drag_hodo.release(e.x(), e.y())
                u, v = self.pix_to_uv(rls_x, rls_y)

                self.modified.emit(drag_idx, {'u':u, 'v':v})
            elif self.drag_rm.isDragging():
                drag_idx, rls_x, rls_y = self.drag_rm.release(e.x(), e.y())
                u, v = self.pix_to_uv(rls_x, rls_y)
                self.modified_vector.emit('right', u, v)

            elif self.drag_lm.isDragging():
                drag_idx, rls_x, rls_y = self.drag_lm.release(e.x(), e.y())
                u, v = self.pix_to_uv(rls_x, rls_y)
                self.modified_vector.emit('left', u, v)

    def mouseDoubleClickEvent(self, e):
        if self.prof is None:
            return

        tol = 5
        lm_x, lm_y = self.uv_to_pix(self.srwind[2], self.srwind[3])
        rm_x, rm_y = self.uv_to_pix(self.srwind[0], self.srwind[1])

        if np.hypot(e.x() - lm_x, e.y() - lm_y) < tol:
            self.toggle_vector.emit('left')
        elif np.hypot(e.x() - rm_x, e.y() - rm_y) < tol:
            self.toggle_vector.emit('right')

    def setBlackPen(self, qp):
        color = self.bg_color
        color.setAlphaF(.5)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(self.bg_color, QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        return qp

    def calculateStormMode(self):
        """
            Logic based off of some of the key findings in Dial et al. (2010)
        """
        dir_06shear, mag_06shear = tab.utils.comp2vec(self.prof.sfc_6km_shear[0], self.prof.sfc_6km_shear[1])
        norm_shear = mag_06shear * np.sin( np.radians( dir_06shear - (self.bndy_dir + 90)) )
        norm_shear = np.abs(tab.utils.KTS2MS(norm_shear))
        if norm_shear < 15: # M/S
            shear_mode = "Linear/Mixed"
        else:
            shear_mode = "Discrete"

        if not tab.utils.QC(self.mean_lcl_el[0]) or (self.mean_lcl_el[0] == 0 and self.mean_lcl_el[1] == 0):
            wind_mode = np.ma.masked
            wind_diff = np.ma.masked
        else:
            dir_cloud, mag_cloud = tab.utils.comp2vec(self.prof.mean_lcl_el[0], self.prof.mean_lcl_el[1])
            norm_cloudmotion = mag_cloud * np.sin( np.radians( dir_cloud - (self.bndy_dir + 90) ) )
            wind_diff = tab.utils.KTS2MS(np.abs(norm_cloudmotion) - self.bndy_spd)
            if wind_diff > 6: # M/S
                wind_mode = "Discrete"
            else:
                wind_mode = "Linear/Mixed"

        return norm_shear, shear_mode, wind_diff, wind_mode

    def plotBndy(self, direction):
        length = 40
        y1 = length*np.sin(np.radians(direction))
        x1 = length*np.cos(np.radians(direction))
        penwidth = 2

        top_x_pix = x1 + length/2
        top_y_pix = y1 + length/2
        bot_x_pix = length/2 - x1
        bot_y_pix = length/2 - y1

        pixmap = QPixmap(length,length)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        boundary_color = QtGui.QColor("#CC9900")
        pen = QtGui.QPen(boundary_color, penwidth)
        painter.setPen(pen)
        painter.drawLine(top_x_pix, top_y_pix, bot_x_pix, bot_y_pix)
        center_rm = QtCore.QPointF(length/2, length/2)
        pen = QtGui.QPen(boundary_color, 2)
        painter.setPen(pen)
        painter.drawEllipse(center_rm, 3, 3)
        painter.end()
        self.setCursor(pixmap)

    def mouseMoveEvent(self, e):
        '''
        Handles the tracking of the mouse to
        provide the dynamic readouts.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        # TAS: Why are these necessary?
        if self.prof is None:
            return

        if self.cursor_type == 'boundary':
            u, v = self.pix_to_uv(e.x(), e.y())

            ## get the direction and speed from u,v
            dir, spd = tab.utils.comp2vec(u,v)
            self.plotBndy(dir)
            self.bndyReadout.setText('Bndy Motion: ' + tab.utils.INT2STR(np.float64(dir)) + '/' + tab.utils.INT2STR(spd))
            self.bndyReadout.setFixedWidth(120)
            self.bndyReadout.move(self.brx-130, self.bry-30)
        elif self.cursor_type == 'none':
            self.drag_hodo.drag(e.x(), e.y())
            self.drag_rm.drag(e.x(), e.y())
            self.drag_lm.drag(e.x(), e.y())
            self.update()

    def updateDraggables(self):
        hght_agl = tab.interp.to_agl(self.prof, self.hght)
        xs, ys = self.uv_to_pix(self.u[hght_agl <= 12000.], self.v[hght_agl <= 12000.])
        self.drag_hodo.setCoords(xs, ys)
        rm_x, rm_y = self.uv_to_pix(self.srwind[0], self.srwind[1])
        self.drag_rm.setCoords(rm_x, rm_y)
        lm_x, lm_y = self.uv_to_pix(self.srwind[2], self.srwind[3])
        self.drag_lm.setCoords(lm_x, lm_y)

    @Slot(bool)
    def cursorToggle(self, toggle):
        self.readout_visible = toggle
        self.update()

    @Slot(float)
    def cursorMove(self, hght):
        self.readout_hght = hght
        self.update()

    def resizeEvent(self, e):
        '''
        Resize the plot based on adjusting the main window.
        
        Parameters
        ----------
        e: an Event object

        '''
        super(plotHodo, self).resizeEvent(e)
        self.plotData()

    def paintEvent(self, e):
        '''
        Handles painting the QPixmap onto the QWidget frame.
        
        Parameters
        ----------
        e: an Event object
        
        '''

        if self.prof:
            draw_readout = self.readout_visible and self.readout_hght >= 0 and self.readout_hght <= 12000.
        else:
            draw_readout = False

        if draw_readout:
            hght_agl = tab.interp.to_agl(self.prof, self.hght)
            u_interp = tab.interp.generic_interp_hght(self.readout_hght, hght_agl, self.u)
            v_interp = tab.interp.generic_interp_hght(self.readout_hght, hght_agl, self.v)
            if tab.utils.QC(u_interp):

                wd_interp, ws_interp = tab.utils.comp2vec(u_interp, v_interp)
                if self.wind_units == 'm/s':
                    ws_interp = tab.utils.KTS2MS(ws_interp)
                    units = 'm/s'
                else:
                    units = 'kts'

                xx, yy = self.uv_to_pix(u_interp, v_interp)
                readout = "%03d/%02d %s" % (wd_interp, ws_interp, units)
            else:
                readout = "--/-- %s" % (self.wind_units)
 
        super(plotHodo, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)

        if draw_readout and tab.utils.QC(u_interp):
            h_offset = 2; v_offset=5; width = 55; hght = 16;
            text_rect = QtCore.QRectF(xx+h_offset, yy+v_offset, width, hght)
            qp.fillRect(text_rect, self.bg_color)

            qp.setPen(QtGui.QPen(self.fg_color, 1))
            qp.drawEllipse(QPointF(xx, yy), 4, 4)
            ## now make the pen white and draw text using
            ## the invisible rectangles
            qp.setFont(self.readout_font)
            qp.drawText(text_rect, QtCore.Qt.AlignCenter, readout)

        qp.end()
    
    def clearData(self):
        '''
        Clears/resets the base QPixmap.
        '''
        self.plotBitMap = self.backgroundBitMap.copy()
        self.drag_hodo.setBackground(self.plotBitMap)    
        self.drag_rm.setBackground(self.plotBitMap)    
        self.drag_lm.setBackground(self.plotBitMap)    

    def plotData(self):
        '''
        Handles the plotting of the data in the QPixmap.
        '''
        ## initialize a QPainter object
        if self.prof is None:
            return

        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)

        cur_dt = self.prof_collections[self.pc_idx].getCurrentDate()
        bc_idx = 0
        for idx, prof_coll in enumerate(self.prof_collections):
            # Draw all unhighlighed members
            if prof_coll.getCurrentDate() == cur_dt:
                proflist = list(prof_coll.getCurrentProfs().values())

                if idx == self.pc_idx:
                    for prof in proflist:
                        if prof.wdir.count() > 1:
                            self.draw_hodo(qp, prof, self.ens_colors, width=1)
                else:
                    for prof in proflist:
                        self.draw_profile(qp, prof, color=self.background_colors[bc_idx], width=1)
                    bc_idx = (bc_idx + 1) % len(self.background_colors)

        bc_idx = 0
        for idx, prof_coll in enumerate(self.prof_collections):
            # Draw all highlighted members that aren't the active one.
            if idx != self.pc_idx and (prof_coll.getCurrentDate() == cur_dt or self.all_observed):
                prof = prof_coll.getHighlightedProf()
                self.draw_profile(qp, prof, color=self.background_colors[bc_idx])
                bc_idx = (bc_idx + 1) % len(self.background_colors)

        # ONLY DRAW A HODOGRAPH IF THERE'S WIND DATA
        if self.prof.wdir.count() > 1:
            ## draw the hodograph
            self.draw_hodo(qp, self.prof, self.colors)
            ## draw the storm motion vector
            self.drawSMV(qp)
            self.drawCorfidi(qp)
            self.drawLCLtoEL_MW(qp)
            if self.cursor_type in [ 'none', 'stormmotion' ]:
                self.drawCriticalAngle(qp)

        qp.end()
    
    def drawLCLtoEL_MW(self, qp):
        '''
        Draws the LCL to EL mean wind onto the hodo.
        
        Parameters
        ----------
        qp: a QPainter object
        
        '''
        penwidth = 2
        pen = QtGui.QPen(QtGui.QColor("#B8860B"), penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)

        try:
            mean_u, mean_v = self.uv_to_pix(self.mean_lcl_el[0],self.mean_lcl_el[1])
            half_length = (8./2.)
            qp.drawRect(mean_u-half_length, mean_v+half_length ,8,8)
        except:
            return
        # This probably needs to be checked. 

        color = self.bg_color
        color.setAlpha(0)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        v_offset=5; h_offset = 1; width = 40; hght = 12;
        
        mw_rect = QtCore.QRectF(mean_u+h_offset, mean_v+v_offset, width, hght)
        qp.drawRect(mw_rect)
        
        pen = QtGui.QPen(QtGui.QColor("#B8860B"))
        qp.setPen(pen)
        qp.setFont(self.label_font)
        mw_spd = self.mean_lcl_el_vec[1]

        if self.wind_units == 'm/s':
            mw_spd = tab.utils.KTS2MS(mw_spd)

        mw_str = tab.utils.INT2STR(np.float64(self.mean_lcl_el_vec[0])) + '/' + tab.utils.INT2STR(mw_spd)
        qp.drawText(mw_rect, QtCore.Qt.AlignCenter, mw_str)

    def drawCorfidi(self, qp):
        '''
        Draw the Corfidi upshear/downshear vectors
        
        Parameters
        ----------
        qp: a QPainter object
        
        '''
        penwidth = 1
        pen = QtGui.QPen(QtGui.QColor("#00BFFF"), penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)

        if not np.isfinite(self.corfidi_up_u) or not np.isfinite(self.corfidi_up_v) or \
            not np.isfinite(self.corfidi_dn_u) or not np.isfinite(self.corfidi_dn_v):
            return

        try:
            up_u, up_v = self.uv_to_pix(self.corfidi_up_u, self.corfidi_up_v)
            dn_u, dn_v = self.uv_to_pix(self.corfidi_dn_u, self.corfidi_dn_v)
            center_up = QtCore.QPointF(up_u, up_v)
            center_dn = QtCore.QPointF(dn_u, dn_v)
            ## draw circles around the center point of the Corfidi vectors
            qp.drawEllipse(center_up, 3, 3)
            qp.drawEllipse(center_dn, 3, 3)
        except:
            return
    
        up_u, up_v = self.uv_to_pix(self.corfidi_up_u, self.corfidi_up_v)
        dn_u, dn_v = self.uv_to_pix(self.corfidi_dn_u, self.corfidi_dn_v)
        center_up = QtCore.QPointF(up_u, up_v)
        center_dn = QtCore.QPointF(dn_u, dn_v)
        ## draw circles around the center point of the Corfidi vectors
        qp.drawEllipse(center_up, 3, 3)
        qp.drawEllipse(center_dn, 3, 3)

        color = self.bg_color
        color.setAlpha(0)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        v_offset=3; h_offset = 1; width = 60; hght = 10;
        
        up_rect = QtCore.QRectF(up_u+h_offset, up_v+v_offset, width, hght)
        dn_rect = QtCore.QRectF(dn_u+h_offset, dn_v+v_offset, width, hght)
        qp.drawRect(up_rect)
        qp.drawRect(dn_rect) 
        ## now make the pen white and draw text using
        ## the invisible rectangles
        pen = QtGui.QPen(QtGui.QColor("#00BFFF"))
        qp.setPen(pen)
        qp.setFont(self.label_font)

        up_spd = self.upshear[1]
        dn_spd = self.downshear[1]

        if self.wind_units == 'm/s':
            up_spd = tab.utils.KTS2MS(up_spd)
            dn_spd = tab.utils.KTS2MS(dn_spd)

        up_stuff = tab.utils.INT2STR(np.float64(self.upshear[0])) + '/' + tab.utils.INT2STR(up_spd)
        dn_stuff = tab.utils.INT2STR(np.float64(self.downshear[0])) + '/' + tab.utils.INT2STR(dn_spd)
        qp.drawText(up_rect, QtCore.Qt.AlignCenter, "UP=" + up_stuff)
        qp.drawText(dn_rect, QtCore.Qt.AlignCenter, "DN=" + dn_stuff)


    def drawSMV(self, qp):
        '''
        Draws the storm motion vector.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## set a pen with white color, width 1, solid line.
        penwidth = 1
        pen = QtGui.QPen(self.fg_color, penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## check and make sure there is no missing data
        rstu,rstv,lstu,lstv = self.srwind
        bkru,bkrv,bklu,bklv = self.prof.bunkers

        # make sure the storm motion exists
        if not tab.utils.QC(rstu) or not tab.utils.QC(lstu):
            return

        ## convert the left and right mover vector components to pixel values
        ruu, rvv = self.uv_to_pix(bkru, bkrv)
        luu, lvv = self.uv_to_pix(bklu, bklv)
        ## calculate the center points of the storm motion vectors
        center_rm = QtCore.QPointF(ruu, rvv)
        center_lm = QtCore.QPointF(luu, lvv)
        # Draw +'s at the bunkers vector locations
        qp.drawLine(center_rm - QPoint(2, 0), center_rm + QPoint(2, 0))
        qp.drawLine(center_rm - QPoint(0, 2), center_rm + QPoint(0, 2))
        qp.drawLine(center_lm - QPoint(2, 0), center_lm + QPoint(2, 0))
        qp.drawLine(center_lm - QPoint(0, 2), center_lm + QPoint(0, 2))

        # Repeat for the user storm motion vectors
        ruu, rvv = self.uv_to_pix(rstu,rstv)
        luu, lvv = self.uv_to_pix(lstu,lstv)
        center_rm = QtCore.QPointF(ruu,rvv)
        center_lm = QtCore.QPointF(luu,lvv)
        ## draw circles around the storm motion vectors
        qp.drawEllipse(center_rm, 5, 5)
        qp.drawEllipse(center_lm, 5, 5)

        ## get the effective inflow layer
        ptop, pbottom = self.ptop, self.pbottom
        ## make sure the effective inflow layer and storm motion vectors exist
        if tab.utils.QC(ptop) and tab.utils.QC(pbottom):
            ## get the interpolated wind at the bottom and top
            ## of the effective inflow layer
            utop,vtop = tab.interp.components(self.prof, ptop)
            ubot,vbot = tab.interp.components(self.prof, pbottom)
            ## convert these values to pixels
            uutop, vvtop = self.uv_to_pix(utop, vtop)
            uubot, vvbot = self.uv_to_pix(ubot, vbot)
            ## set a pen
            pen = QtGui.QPen(self.eff_inflow_color, penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ## draw lines showing the effective inflow layer
            if self.use_left:
                qp.drawLine(center_lm.x(), center_lm.y(), uubot, vvbot)
                qp.drawLine(center_lm.x(), center_lm.y(), uutop, vvtop)
            else:
                qp.drawLine(center_rm.x(), center_rm.y(), uubot, vvbot)
                qp.drawLine(center_rm.x(), center_rm.y(), uutop, vvtop)
                
        color = self.bg_color
        color.setAlpha(0)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        h_offset = 2; v_offset=5; width = 55; hght = 12;
        rm_rect = QtCore.QRectF(ruu+h_offset, rvv+v_offset, width, hght)
        lm_rect = QtCore.QRectF(luu+h_offset, lvv+v_offset, width, hght)
        qp.drawRect(rm_rect)
        qp.drawRect(lm_rect) 
        ## now make the pen white and draw text using
        ## the invisible rectangles
        pen = QtGui.QPen(self.fg_color)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rm_spd = self.bunkers_right_vec[1]
        lm_spd = self.bunkers_left_vec[1]

        if self.wind_units == 'm/s':
            rm_spd = tab.utils.KTS2MS(rm_spd)
            lm_spd = tab.utils.KTS2MS(lm_spd)

        rm_stuff = tab.utils.INT2STR(np.float64(self.bunkers_right_vec[0])) + '/' + tab.utils.INT2STR(rm_spd)
        lm_stuff = tab.utils.INT2STR(np.float64(self.bunkers_left_vec[0])) + '/' + tab.utils.INT2STR(lm_spd)
        qp.drawText(rm_rect, QtCore.Qt.AlignCenter, rm_stuff + " RM")
        qp.drawText(lm_rect, QtCore.Qt.AlignCenter, lm_stuff + " LM")

    def drawCriticalAngle(self, qp):
        '''
        Plot the critical angle on the hodograph and show the value in the hodograph.
        
        Parameters
        ----------
        qp : QtGui.QPainter object
        '''

        pres_500m = tab.interp.pres(self.prof, tab.interp.to_msl(self.prof, 500))
        sfc_u, sfc_v = tab.interp.components(self.prof, self.prof.pres[self.prof.get_sfc()])
        u500, v500 = tab.interp.components(self.prof, pres_500m)
        if tab.utils.QC(self.ptop) and tab.utils.QC(self.pbottom) and \
           self.pbottom == self.prof.pres[self.prof.sfc] and \
           tab.utils.QC(sfc_u) and tab.utils.QC(sfc_v) and \
           tab.utils.QC(u500) and tab.utils.QC(v500):
            # There is an effective inflow layer at the surface so draw the critical angle line
            ca_color = QtGui.QColor("#FF00FF")
            sfc_u_pix, sfc_v_pix = self.uv_to_pix(sfc_u,sfc_v)
            u500_pix, v500_pix = self.uv_to_pix(u500, v500)
            pen = QtGui.QPen(ca_color, 1.0, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            print(sfc_u_pix, sfc_v_pix, u500_pix, v500_pix)
            qp.drawLine(sfc_u_pix, sfc_v_pix, u500_pix, v500_pix)
            vec1_u, vec1_v = u500 - sfc_u, v500 - sfc_v
            try:
                mask = np.maximum( self.u, self.v )
                rstu,rstv,lstu,lstv = self.srwind
                rstu = rstu[~mask]; rstv = rstv[~mask]
            except:
                rstu,rstv,lstu,lstv = self.srwind

            if tab.utils.QC(rstu) and tab.utils.QC(lstu):
                qp = self.setBlackPen(qp)
                rect = QtCore.QRectF(15, self.bry-36, 100, self.critical_height + 5)
                qp.drawRect(rect)     
                ca_text_color = self.crit_color
                pen = QtGui.QPen(ca_text_color, 1.0, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                qp.setFont(self.critical_font)
                offset = 10
                if self.use_left:
                    critical_angle = self.prof.left_critical_angle
                else:
                    critical_angle = self.prof.right_critical_angle
                qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Critical Angle = ' + tab.utils.INT2STR(critical_angle) + u"\u00B0")

    def draw_hodo(self, qp, prof, colors, width=2):
        '''
        Plot the Hodograph.
        
        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## check for masked daata
        try:
            mask = np.maximum(np.maximum(prof.u.mask, prof.v.mask), prof.hght.mask)
            z = tab.interp.to_agl(prof, prof.hght)[~mask]
            u = prof.u[~mask]
            v = prof.v[~mask]
        ## otherwise the data is fine
        except:
            z = tab.interp.to_agl(prof, prof.hght )
            u = prof.u
            v = prof.v

        ## convert the u and v values to x and y pixels
        xx, yy = self.uv_to_pix(u, v)
        ## define the colors for the different hodograph heights
        penwidth = width
        seg_bnds = [0., 3000., 6000., 9000., 12000.]
        seg_x = [ tab.interp.generic_interp_hght(bnd, z, xx) for bnd in seg_bnds if bnd <= z.max() ]
        seg_y = [ tab.interp.generic_interp_hght(bnd, z, yy) for bnd in seg_bnds if bnd <= z.max() ]

        seg_idxs = np.searchsorted(z, seg_bnds)
        for idx in range(len(seg_x) - 1):
            ## define a pen to draw with
            pen = QtGui.QPen(colors[idx], penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)

            path = QPainterPath()
            path.moveTo(seg_x[idx], seg_y[idx])
            for z_idx in range(seg_idxs[idx], seg_idxs[idx + 1]):
                path.lineTo(xx[z_idx], yy[z_idx])
            path.lineTo(seg_x[idx + 1], seg_y[idx + 1])

            qp.drawPath(path)

        if z.max() < max(seg_bnds):
            idx = len(seg_x) - 1
            pen = QtGui.QPen(colors[idx], penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)

            path = QPainterPath()
            path.moveTo(seg_x[idx], seg_y[idx])
            for z_idx in range(seg_idxs[idx], len(xx)):
                path.lineTo(xx[z_idx], yy[z_idx])

            qp.drawPath(path)
         

    def draw_profile(self, qp, prof, color="#6666CC", width=2):
        '''
        Plot the Hodograph.

        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## check for masked daata
        try:
            mask = np.maximum(np.maximum(prof.u.mask, prof.v.mask), prof.hght.mask)
            z = tab.interp.to_agl(prof, prof.hght[~mask])
            u = prof.u[~mask]
            v = prof.v[~mask]
        ## otherwise the data is fine
        except:
            z = tab.interp.to_agl(prof, prof.hght )
            u = prof.u
            v = prof.v
        ## convert the u and v values to x and y pixels
        xx, yy = self.uv_to_pix(u, v)

        penwidth = width
        pen = QtGui.QPen(QtGui.QColor(color), penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)

        seg_bnds = [0., 3000., 6000., 9000., 12000.]
        seg_x = [ tab.interp.generic_interp_hght(bnd, z, xx) for bnd in seg_bnds if bnd <= z.max() ]
        seg_y = [ tab.interp.generic_interp_hght(bnd, z, yy) for bnd in seg_bnds if bnd <= z.max() ]

        seg_idxs = np.searchsorted(z, seg_bnds)
        for idx in range(len(seg_x) - 1):
            ## define a pen to draw with
            pen = QtGui.QPen(QtGui.QColor(color), penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)

            path = QPainterPath()
            path.moveTo(seg_x[idx], seg_y[idx])
            for z_idx in range(seg_idxs[idx], seg_idxs[idx + 1]):
                path.lineTo(xx[z_idx], yy[z_idx])
            path.lineTo(seg_x[idx + 1], seg_y[idx + 1])

            qp.drawPath(path)

        if z.max() < max(seg_bnds):
            idx = len(seg_x) - 1
            pen = QtGui.QPen(QtGui.QColor(color), penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)

            path = QPainterPath()
            path.moveTo(seg_x[idx], seg_y[idx])
            for z_idx in range(seg_idxs[idx], len(xx)):
                path.lineTo(xx[z_idx], yy[z_idx])

            qp.drawPath(path)


if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    tester = plotHodo()
    #tester.setProf()
    tester.show()        
    app_frame.exec_()
