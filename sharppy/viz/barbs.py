import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

def drawFlag(path, shemis=False):
    side = -1 if shemis else 1
    pos = path.currentPosition()
    path.lineTo(pos.x(), pos.y() + side * 10)
    path.lineTo(pos.x() - 4, pos.y())
    path.moveTo(pos.x() - 6, pos.y())

def drawFullBarb(path, shemis=False):
    side = -1 if shemis else 1
    pos = path.currentPosition()
    path.lineTo(pos.x(), pos.y() + side * 10)
    path.moveTo(pos.x() - 4, pos.y())

def drawHalfBarb(path, shemis=False):
    side = -1 if shemis else 1
    pos = path.currentPosition()
    path.lineTo(pos.x(), pos.y() + side * 5)
    path.moveTo(pos.x() - 4, pos.y())

def drawBarb(qp, origin_x, origin_y, wdir, wspd, color='#FFFFFF', shemis=False):
    pen = QtGui.QPen(QtGui.QColor(color), 1, QtCore.Qt.SolidLine)
    pen.setWidthF(1.)
    qp.setPen(pen)
    qp.setBrush(QtCore.Qt.NoBrush)

    try:
        wspd = int(round(wspd / 5.) * 5) # Round to the nearest 5
    except ValueError:
        return

    qp.translate(origin_x, origin_y)

    if wspd > 0:
        qp.rotate(wdir - 90)

        path = QtGui.QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(25, 0)

        while wspd >= 50:
            drawFlag(path, shemis=shemis)
            wspd -= 50

        while wspd >= 10:
            drawFullBarb(path, shemis=shemis)
            wspd -= 10

        while wspd >= 5:
            drawHalfBarb(path, shemis=shemis)
            wspd -= 5

        qp.drawPath(path)
        qp.rotate(90 - wdir)
    else:
        qp.drawEllipse(QtCore.QPoint(0, 0), 3, 3)
    qp.translate(-origin_x, -origin_y)

def drawBarb_old( qp, origin_x, origin_y, u, v, color='#FFFFFF' ):
    pen = QtGui.QPen(QtGui.QColor(color), 1, QtCore.Qt.SolidLine)
    pen.setWidthF(1.)
    qp.setPen(pen)
    wnd = np.ceil( tab.utils.mag(u, v) )
    ## check if there are any 50kt triangles needed
    if wnd < 5.:
        point = QtCore.QPoint( origin_x, origin_y )
        qp.drawEllipse(point, 3, 3)
    else:
        ## turn the vector into a normal vector
        u_norm = (u / wnd)
        v_norm = (v / wnd)
        ## get the end point of the vector. The scalar multiple is to give it length
        end_x = origin_x - u_norm * 25
        end_y = origin_y + v_norm * 25
        qp.drawLine(origin_x, origin_y, end_x, end_y)
        num_flag_barbs = int( wnd / 50. )
        num_full_barbs = int( wnd / 10. ) % 5
        num_half_barbs = int( wnd / 5. ) % 2
        ## draw the flag barbs
        for i in range(num_flag_barbs):
            ## use this as a linear offset from the previous barb,
            ## starting at the end
            offset1 = 4. * i
            offset2 = 4. * (i+1)
            ## calculate the u nd v offset
            offset_x1 = u_norm * offset1
            offset_x2 = u_norm * offset2
            offset_y1 = v_norm * offset1
            offset_y2 = v_norm * offset2
            ## starting from the end of the wind barb, work back
            ## towards the origin in increments of the offset
            barbx_start = end_x + offset_x1
            flagx_start = end_x + offset_x2
            barby_start = end_y - offset_y1
            flagy_start = end_y - offset_y2
            ## then draw outward perpendicular to the wind barb
            barbx_end = barbx_start - v_norm * 10
            barby_end = barby_start - u_norm * 10
            ## draw the barb
            qp.drawLine(barbx_start, barby_start, barbx_end, barby_end)
            qp.drawLine(flagx_start, flagy_start, barbx_end, barby_end)
        
        for i in range(num_full_barbs):
            ## use this as a linear offset from the previous barb,
            ## starting at the end
            if num_flag_barbs > 0:
                offset = 4. * num_flag_barbs + 4 * i + 2
            else:
                offset = 4. * i
            ## calculate the u nd v offset
            offset_x = u_norm * offset
            offset_y = v_norm * offset
            ## starting from the end of the wind barb, work back
            ## towards the origin in increments of the offset
            barbx_start = end_x + offset_x
            barby_start = end_y - offset_y
            ## then draw outward perpendicular to the wind barb
            barbx_end = barbx_start - v_norm * 10
            barby_end = barby_start - u_norm * 10
            ## draw the barb
            qp.drawLine(barbx_start, barby_start, barbx_end, barby_end)
        
        ## draw the half barbs
        for i in range(num_half_barbs):
            ## this time we want to index from 1 so that we don't
            ## draw on top of the full barbs
            if num_flag_barbs > 0:
                i = i + 1
                offset = 4. * (num_flag_barbs + 1 + num_full_barbs)
            else:
                i = i + 1
                offset = 4. * (num_full_barbs) * i
            ## start at the increment after the last full barb
            ## get the u and v offset
            offset_x = u_norm * offset
            offset_y = v_norm * offset
            ## starting from the end of the wind barb, work back
            ## towards the origin in increments of the offset
            barbx_start = end_x + offset_x
            barby_start = end_y - offset_y
            ## then draw outward perpendicular to the wind barb
            barbx_end = barbx_start - v_norm * 5
            barby_end = barby_start - u_norm * 5
            qp.drawLine(barbx_start, barby_start, barbx_end, barby_end)
