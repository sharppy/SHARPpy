
import numpy as np

from PySide.QtGui import *
from PySide.QtCore import *

class Draggable(object):
    def __init__(self, x_obj, y_obj, background, cutoff=5, lock_dim=None, line_color='#FFFFFF'):
        self._background = background
        self._x_obj = x_obj
        self._y_obj = y_obj
        self._cutoff = cutoff
        self._lock_dim = lock_dim
        self._line_color = line_color
        self._drag_idx = None
        self._save_bitmap = None
        self._drag_buffer = 5

        if type(self._x_obj) != np.ma.MaskedArray:
            self._x_obj = np.ma.array([ self._x_obj ])
        if type(self._y_obj) != np.ma.MaskedArray:
            self._y_obj = np.ma.array([ self._y_obj ])

    def click(self, click_x, click_y):
        dists = np.hypot(click_x - self._x_obj, click_y - self._y_obj)
        if np.any(dists <= self._cutoff):
            self._drag_idx = np.argmin(dists)

        return self._drag_idx is not None

    def drag(self, drag_x, drag_y, restrictions=None):
        if not self._drag_idx:
            return

        if self._lock_dim == 'x':
            drag_x = self._x_obj[self._drag_idx]
        elif self._lock_dim == 'y':
            drag_y = self._y_obj[self._drag_idx]

        if restrictions is not None:
            drag_x, drag_y = restrictions(drag_x, drag_y)

        lb_idx, ub_idx = max(self._drag_idx - 1, 0), min(self._drag_idx + 1, self._x_obj.shape[0] - 1)

        while lb_idx >= 0 and (self._x_obj.mask[lb_idx] or self._y_obj.mask[lb_idx]):
            lb_idx -= 1

        while ub_idx < self._x_obj.shape[0] and (self._x_obj.mask[ub_idx] or self._y_obj.mask[ub_idx]):
            ub_idx += 1

        if lb_idx != -1:
            lb_x, ub_x = min(drag_x, self._x_obj[lb_idx]), max(drag_x, self._x_obj[lb_idx])
            lb_y, ub_y = min(drag_y, self._y_obj[lb_idx]), max(drag_y, self._y_obj[lb_idx])
        else:
            lb_x = ub_x = drag_x
            lb_y = ub_y = drag_y

        if ub_idx != self._x_obj.shape[0]:
            lb_x, ub_x = min(lb_x, self._x_obj[ub_idx]), max(ub_x, self._x_obj[ub_idx])
            lb_y, ub_y = min(lb_y, self._y_obj[ub_idx]), max(ub_y, self._y_obj[ub_idx])

        qp = QPainter()
        qp.begin(self._background)

        if self._save_bitmap is not None:
            (origin, size, bmap) = self._save_bitmap
            qp.drawPixmap(origin, bmap, QRect(QPoint(0, 0), size))

        origin = QPoint(max(lb_x - self._drag_buffer, 0), max(lb_y - self._drag_buffer, 0))
        size = QSize(ub_x - lb_x + 2 * self._drag_buffer, ub_y - lb_y + 2 * self._drag_buffer)
        bmap = self._background.copy(QRect(origin, size))
        self._save_bitmap = (origin, size, bmap)

        pen = QPen(QColor(self._line_color), 1, Qt.SolidLine)
        qp.setPen(pen)
        if lb_idx != -1:
            x1, y1 = self._x_obj[lb_idx], self._y_obj[lb_idx]
            x2, y2 = drag_x, drag_y
            qp.drawLine(x1, y1, x2, y2)
        if ub_idx != self._x_obj.shape[0]:
            x1, y1 = drag_x, drag_y
            x2, y2 = self._x_obj[ub_idx], self._y_obj[ub_idx]
            qp.drawLine(x1, y1, x2, y2)

        qp.end()

    def release(self, rls_x, rls_y, restrictions=None):
        if not self._drag_idx:
            return

        if self._lock_dim == 'x':
            rls_x = self._x_obj[self._drag_idx]
        elif self._lock_dim == 'y':
            rls_y = self._y_obj[self._drag_idx]

        if restrictions:
            rls_x, rls_y = restrictions(rls_x, rls_y)

        self._x_obj[self._drag_idx] = rls_x
        self._y_obj[self._drag_idx] = rls_y

        drag_idx = self._drag_idx
        self._drag_idx = None
        self._save_bitmap = None
        return drag_idx, rls_x, rls_y

    def setBackground(self, background):
        self._background = background

    def setCoords(self, x_obj, y_obj):
        self._x_obj = x_obj
        self._y_obj = y_obj

    def getBackground(self):
        return self._background

    def getCoords(self):
        return self._x_obj, self._y_obj

    def isDragging(self):
        return self._drag_idx is not None
