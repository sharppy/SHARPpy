import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
from PySide.QtGui import *
from PySide.QtCore import *


__all__ = ['backgroundHodo', 'plotHodo']


class backgroundHodo(QtGui.QFrame):
    '''
    Handles the plotting of the backgroun frame onto
    a QPixmap. Inherits from the QtGui.QFrame object.
    '''
    def __init__(self):
        super(backgroundHodo, self).__init__()
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
        self.center_hodo()
        self.ring_increment = 10
        self.rings = range(self.ring_increment, 100+self.ring_increment,
            self.ring_increment)
        self.label_font = QtGui.QFont('Helvetica', 9)
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()


    def center_hodo(self):
        '''
        Center the hodograph in the window. Can/Should be overwritten.

        '''
        self.centerx = self.wid / 2; self.centery = self.hgt / 2
        self.hodomag = 160.
        self.scale = (self.brx - self.tlx) / self.hodomag
    
    def wheelEvent(self, e):
        '''
        Handeles the zooming of the hodograph window.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        ## get the new scaling magnitude
        new_mag = self.hodomag + e.delta() / 5
        ## make sure the user doesn't zoom out of
        ## bounds to prevent drawing issues
        if new_mag >= 40. and new_mag <= 200.:
            self.hodomag = new_mag
        ## if it is out of bounds, do nothing
        else:
            self.hodomag = self.hodomag
        ## get the maximum speed value in the frame for the ring increment.
        ## this is to help reduce drawing resources
        max_uv = int(self.pix_to_uv(self.brx, 0)[0])
        self.rings = range(self.ring_increment, max_uv+self.ring_increment,
                           self.ring_increment)
        ## reassign the new scale
        self.scale = (self.brx - self.tlx) / self.hodomag
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
        pen = QtGui.QPen(QtGui.QColor(WHITE), 2)
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
        pen = QtGui.QPen(QtGui.QColor(WHITE), 2)
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
        color = "#555555"
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
        pen = QtGui.QPen(QtGui.QColor('#000000'), 0, QtCore.Qt.SolidLine)
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
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"))
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
        xx = self.centerx + (u * self.scale)
        yy = self.centery - (v * self.scale)
        return xx, yy

    def pix_to_uv(self, xx, yy):
        '''
        Function to convert (x,y) to (u,v) coordinates.
        
        Parameters
        ----------
        xx: the x pixel value
        yy: the y pixel value
        
        '''
        u = (xx - self.centerx) / self.scale
        v = (self.centery - yy) / self.scale
        return u, v




class plotHodo(backgroundHodo):
    '''
    Plots the data on the hodograph. Inherits from the backgroundHodo
    class that plots the background frame onto a QPixmap.
    '''
    def __init__(self, hght, u, v, **kwargs):
        '''
        Initialize the data used in the class.
        '''
        super(plotHodo, self).__init__()
        ## initialize the variables needed to plot the hodo.
        self.hght = hght
        self.u = u; self.v = v
        ## if you want the storm motion vector, you need to
        ## provide the profile.
        self.prof = kwargs.get('prof', None)
        self.srwind = self.prof.srwind
        self.ptop = self.prof.etop
        self.pbottom = self.prof.ebottom
        self.mean_lcl_el = self.prof.mean_lcl_el
        self.corfidi_up_u = self.prof.upshear_downshear[0]
        self.corfidi_up_v = self.prof.upshear_downshear[1]
        self.corfidi_dn_u = self.prof.upshear_downshear[2]
        self.corfidi_dn_v = self.prof.upshear_downshear[3]
        self.bunkers_right_vec = tab.utils.comp2vec(self.prof.srwind[0], self.prof.srwind[1])
        self.bunkers_left_vec = tab.utils.comp2vec(self.prof.srwind[2], self.prof.srwind[3])
        self.upshear = tab.utils.comp2vec(self.prof.upshear_downshear[0],self.prof.upshear_downshear[1])
        self.downshear = tab.utils.comp2vec(self.prof.upshear_downshear[2],self.prof.upshear_downshear[3])
        self.mean_lcl_el_vec = tab.utils.comp2vec(self.prof.mean_lcl_el[0], self.prof.mean_lcl_el[1])
        ## the following is used for the dynamic readout
        self.setMouseTracking(True)
        self.wndReadout = QLabel(parent=self)
        self.srh1kmReadout = QLabel(parent=self)
        self.srh3kmReadout = QLabel(parent=self)
        self.esrhReadout = QLabel(parent=self)
        self.wndReadout.setFixedWidth(0)
        self.srh1kmReadout.setFixedWidth(0)
        self.srh3kmReadout.setFixedWidth(0)
        self.esrhReadout.setFixedWidth(0)
        ## these stylesheets have to be set for
        ## each readout
        self.wndReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #FFFFFF;}")
        self.srh1kmReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #FF0000;}")
        self.srh3kmReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #00FF00;}")
        self.esrhReadout.setStyleSheet("QLabel {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 0px;"
            "  font-size: 11px;"
            "  color: #00FFFF;}")
        self.hband = QRubberBand(QRubberBand.Line, self)
        self.vband = QRubberBand(QRubberBand.Line, self)
    
    
    def wheelEvent(self, e):
        '''
        Handles the zooming of the hodograph.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotHodo, self).wheelEvent(e)
        self.clearData()
        self.plotBackground()
        self.plotData()
    
    def mousePressEvent(self, e):
        '''
        Handles when the mouse is pressed.
        Used to set the storm motion vector.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        if self.hasMouseTracking():
            self.setMouseTracking(False)
        else:
            self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        '''
        Handles the tracking of the mouse to
        provide the dynamic readouts.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        ## convert the location of the mouse to u,v space
        u, v = self.pix_to_uv(e.x(), e.y())
        ## get the direction and speed from u,v
        dir, spd = tab.utils.comp2vec(u,v)
        ## calculate the storm relative helicity for a storm motion
        ## vector with a u,v at the mouse pointer
        srh1km = tab.winds.helicity(self.prof, 0, 1000., stu=u, stv=v)[0]
        srh3km = tab.winds.helicity(self.prof, 0, 3000., stu=u, stv=v)[0]
        ## do some sanity checks to prevent crashing if there is no
        ## effective inflow layer
        etop, ebot = self.prof.etopm, self.prof.ebotm
        if etop is np.ma.masked or ebot is np.ma.masked:
            esrh = np.ma.masked
            self.esrhReadout.setText('effective: ' + str(esrh) + ' m2/s2')
        else:
            esrh = tab.winds.helicity(self.prof, ebot, etop, stu=u, stv=v)[0]
            self.esrhReadout.setText('effective: ' + tab.utils.INT2STR(esrh) + ' m2/s2')
        ## set the crosshair in the window
        self.hband.setGeometry(QRect(QPoint(self.lpad,e.y()), QPoint(self.brx,e.y())).normalized())
        self.vband.setGeometry(QRect(QPoint(e.x(), self.tpad), QPoint(e.x(),self.bry)).normalized())
        ## set the readout texts
        self.wndReadout.setText(tab.utils.INT2STR(dir) + '/' + tab.utils.FLOAT2STR(spd, 1))
        self.srh1kmReadout.setText('sfc-1km: ' + tab.utils.INT2STR(srh1km) + ' m2/s2')
        self.srh3kmReadout.setText('sfc-3km: ' + tab.utils.INT2STR(srh3km) + ' m2/s2')
        ## set the readout width
        self.wndReadout.setFixedWidth(50)
        self.srh1kmReadout.setFixedWidth(120)
        self.srh3kmReadout.setFixedWidth(120)
        self.esrhReadout.setFixedWidth(120)
        ## place the readout
        self.wndReadout.move(1, self.bry-15)
        self.srh1kmReadout.move(self.brx-130, self.bry-45)
        self.srh3kmReadout.move(self.brx-130, self.bry-30)
        self.esrhReadout.move(self.brx-130, self.bry-15)
        ## show the crosshair
        self.hband.show()
        self.vband.show()

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
        super(plotHodo, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()
    
    def clearData(self):
        '''
        Clears/resets the base QPixmap.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(QtCore.Qt.black)
    
    def plotData(self):
        '''
        Handles the plotting of the data in the QPixmap.
        '''
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the hodograph
        self.draw_hodo(qp)
        ## draw the storm motion vector
        self.drawSMV(qp)
        self.drawCorfidi(qp)
        self.drawLCLtoEL_MW(qp)
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

        color = QtGui.QColor('#000000')
        color.setAlpha(0)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        v_offset=5; h_offset = 1; width = 40; hght = 12;
        
        mw_rect = QtCore.QRectF(mean_u+h_offset, mean_v+v_offset, width, hght)
        qp.drawRect(mw_rect)
        
        pen = QtGui.QPen(QtGui.QColor("#B8860B"))
        qp.setPen(pen)
        qp.setFont(self.label_font)
        mw_str = tab.utils.INT2STR(self.mean_lcl_el_vec[0]) + '/' + tab.utils.INT2STR(self.mean_lcl_el_vec[1])
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
        color = QtGui.QColor('#000000')
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
        up_stuff = tab.utils.INT2STR(self.upshear[0]) + '/' + tab.utils.INT2STR(self.upshear[1])
        dn_stuff = tab.utils.INT2STR(self.downshear[0]) + '/' + tab.utils.INT2STR(self.downshear[1])
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
        pen = QtGui.QPen(QtGui.QColor(WHITE), penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## check and make sure there is no missing data
        try:
            mask = np.maximum( self.u, self.v )
            hght = self.hght[~mask]
            u = self.u[~mask]; v = self.v[~mask]
            ## calculate the left and right storm motion vectors
            rstu,rstv,lstu,lstv = self.srwind
            rstu = rstu[~mask]; rstv = rstv[~mask]
            lstu = lstu[~mask]; lstv = lstv[~mask]
        ## otherwise the data is fine
        except:
            hght = self.hght
            u = self.u; v = self.v
            rstu,rstv,lstu,lstv = self.srwind
        ## convert the left and right mover vector components to pixel values
        ruu, rvv = self.uv_to_pix(rstu,rstv)
        luu, lvv = self.uv_to_pix(lstu, lstv)
        ## calculate the center points of the storm motion vectors
        center_rm = QtCore.QPointF(ruu,rvv)
        center_lm = QtCore.QPointF(luu,lvv)
        ## draw circles around the sorm motion vectors
        qp.drawEllipse(center_rm, 5, 5)
        qp.drawEllipse(center_lm, 5, 5)
        ## get the effective inflow layer
        ptop, pbottom = self.ptop, self.pbottom
        ## make sure the effective inflow layer exists
        if ptop is np.ma.masked and pbottom is np.ma.masked:
            pass
        else:
            ## get the interpolated wind at the bottom and top
            ## of the effective inflow layer
            utop,vtop = tab.interp.components(self.prof, ptop)
            ubot,vbot = tab.interp.components(self.prof, pbottom)
            ## convert these values to pixels
            uutop, vvtop = self.uv_to_pix(utop, vtop)
            uubot, vvbot = self.uv_to_pix(ubot, vbot)
            ## set a pen
            pen = QtGui.QPen(QtGui.QColor("#00FFFF"), penwidth)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ## draw lines showing the effective inflow layer
            qp.drawLine(center_rm.x(), center_rm.y(), uubot, vvbot)
            qp.drawLine(center_rm.x(), center_rm.y(), uutop, vvtop)
        color = QtGui.QColor('#000000')
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
        pen = QtGui.QPen(QtGui.QColor("#FFFFFF"))
        qp.setPen(pen)
        qp.setFont(self.label_font)
        rm_stuff = tab.utils.INT2STR(self.bunkers_right_vec[0]) + '/' + tab.utils.INT2STR(self.bunkers_right_vec[1])
        lm_stuff = tab.utils.INT2STR(self.bunkers_left_vec[0]) + '/' + tab.utils.INT2STR(self.bunkers_left_vec[1])
        qp.drawText(rm_rect, QtCore.Qt.AlignCenter, rm_stuff + " RM")
        qp.drawText(lm_rect, QtCore.Qt.AlignCenter, lm_stuff + " LM")

    def drawCriticalAngle(self, qp):
        '''
        Plot the critical angle on the hodograph and show the value in the hodograph.
        
        Parameters
        ----------
        qp : QtGui.QPainter object
        '''

        if self.ptop is np.ma.masked and self.pbottom is np.ma.masked:
            pass
        elif self.prof.pres[self.prof.get_sfc()] == self.pbottom:
            # There is an effective inflow layer at the surface so draw the critical angle line
            ca_color = QtGui.QColor("#FF00FF")
            pres_500m = tab.interp.pres(self.prof, tab.interp.to_msl(self.prof, 500))
            u500, v500 = tab.interp.components(self.prof, pres_500m)
            sfc_u, sfc_v = tab.interp.components(self.prof, self.prof.pres[self.prof.get_sfc()])
            sfc_u_pix, sfc_v_pix = self.uv_to_pix(sfc_u,sfc_v)
            u500_pix, v500_pix = self.uv_to_pix(u500, v500)
            pen = QtGui.QPen(ca_color, 1.0, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(sfc_u_pix, sfc_v_pix, u500_pix, v500_pix)
            vec1_u, vec1_v = u500 - sfc_u, v500 - sfc_v
            try:
                mask = np.maximum( self.u, self.v )
                rstu,rstv,lstu,lstv = self.srwind
                rstu = rstu[~mask]; rstv = rstv[~mask]
            except:
                rstu,rstv,lstu,lstv = self.srwind
    
            vec2_u, vec2_v = rstu - sfc_u, rstv - sfc_v
            vec_1_mag = np.sqrt(np.power(vec1_u, 2) + np.power(vec1_v, 2))
            vec_2_mag = np.sqrt(np.power(vec2_u, 2) + np.power(vec2_v, 2))
            dot = vec1_u * vec2_u + vec1_v * vec2_v
            angle = np.degrees(np.arccos(dot / (vec_1_mag * vec_2_mag)))
            ca_text_color = QtGui.QColor("#00FFFF")
            pen = QtGui.QPen(ca_text_color, 1.0, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setFont(QtGui.QFont('Helvetica', 11))
            offset = 10
            rect = QtCore.QRectF(15, self.bry-36, 140, 12)
            qp.drawText(rect, QtCore.Qt.AlignLeft, 'Critical Angle = ' + str(int(round(angle,0))))
    


    def draw_hodo(self, qp):
        '''
        Plot the Hodograph.
        
        Parameters
        ----------
        qp: QtGui.QPainter object

        '''
        ## check for masked daata
        try:
            mask = np.maximum(self.u.mask, self.v.mask)
            z = tab.interp.to_agl(self.prof, self.hght[~mask])
            u = self.u[~mask]
            v = self.v[~mask]
        ## otherwise the data is fine
        except:
            z = tab.interp.to_agl(self.prof, self.hght )
            u = self.u
            v = self.v
        ## convert the u and v values to x and y pixels
        xx, yy = self.uv_to_pix(u, v)
        ## define the colors for the different hodograph heights
        low_level_color = QtGui.QColor("#FF0000")
        mid_level_color = QtGui.QColor("#00FF00")
        upper_level_color = QtGui.QColor("#FFFF00")
        trop_level_color = QtGui.QColor("#00FFFF")
        ## define a pen to draw with
        penwidth = 2
        pen = QtGui.QPen(low_level_color, penwidth)
        pen.setStyle(QtCore.Qt.SolidLine)
        ## loop through the profile. Loop through shape - 1 since
        ## i + 1 is indexed
        for i in range(xx.shape[0]-1):
            ## draw the hodograph in the lowest 3km
            if z[i] < 3000:
                if z[i+1] < 3000:
                    pen = QtGui.QPen(low_level_color, penwidth)
                else:
                    pen = QtGui.QPen(low_level_color, penwidth)
                    ## get the interpolated wind at 3km
                    tmp_u = tab.interp.generic_interp_hght(3000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(3000, z, v)
                    ## get the pixel value
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    ## draw the hodograph
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(mid_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 3-6km range
            elif z[i] < 6000:
                if z[i+1] < 6000:
                    pen = QtGui.QPen(mid_level_color, penwidth)
                else:
                    pen = QtGui.QPen(mid_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(6000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(6000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(upper_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 6-9km layer
            elif z[i] < 9000:
                if z[i+1] < 9000:
                    pen = QtGui.QPen(upper_level_color, penwidth)
                else:
                    pen = QtGui.QPen(upper_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(9000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(9000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    pen = QtGui.QPen(trop_level_color, penwidth)
                    qp.setPen(pen)
                    qp.drawLine(tmp_x, tmp_y, xx[i+1], yy[i+1])
                    continue
            ## draw the hodograph in the 9-12km layer
            elif z[i] < 12000:
                if z[i+1] < 12000:
                    pen = QtGui.QPen(trop_level_color, penwidth)
                else:
                    pen = QtGui.QPen(low_level_color, penwidth)
                    tmp_u = tab.interp.generic_interp_hght(12000, z, u)
                    tmp_v = tab.interp.generic_interp_hght(12000, z, v)
                    tmp_x, tmp_y = self.uv_to_pix(tmp_u, tmp_v)
                    qp.drawLine(xx[i], yy[i], tmp_x, tmp_y)
                    break
            else:
                break
            qp.setPen(pen)
            qp.drawLine(xx[i], yy[i], xx[i+1], yy[i+1])
