
import numpy as np

from qtpy.QtGui import *
from qtpy.QtCore import *

class Draggable(object):
    """
    The Draggable class implements low-level clicking and dragging on widgets.
    """
    def __init__(self, x_obj, y_obj, background, cutoff=5, lock_dim=None, line_color=QColor('#FFFFFF')):
        """
        Construct a draggable object
        x_obj:  Numpy array or Python float containing the x coordinate(s) in pixels of the draggable object.
        y_obj:  Numpy array or Python float containing the y coordinate(s) in pixels of the draggable object.
        background: A QPixmap containing the image displayed in the widget.
        cutoff: The radius of the buffer around each vertex when looking for clicks. Default is 5 px.
        lock_dim: A dimension to lock in place when doing the dragging. Allowed values are 'x' (dragging
                    is allowed in the y dimension only), 'y' (dragging is allowed in the x direction 
                    only). Default is to allow dragging in both dimensions.
        line_color: The color to use for the line drawn while dragging.
        """
        self._background = background
        self._x_obj = x_obj
        self._y_obj = y_obj
        self._cutoff = cutoff
        self._lock_dim = lock_dim
        self._line_color = line_color
        self._drag_idx = None
        self._save_bitmap = None
        self._drag_buffer = 5

        self._click_start = None

        if type(self._x_obj) != np.ma.MaskedArray:
            self._x_obj = np.ma.array([ self._x_obj ])
        if type(self._y_obj) != np.ma.MaskedArray:
            self._y_obj = np.ma.array([ self._y_obj ])

    def click(self, click_x, click_y):
        """
        Check to see whether the user clicked on a vertex in this profile. If they did, initialize
            the drag operation.
        click_x:    x coordinate in pixels of the click
        click_y:    y coordinate in pixels of the click
        Returns a boolean specifying whether a drag operation was initialized.
        """
        dists = np.hypot(click_x - self._x_obj, click_y - self._y_obj)
        if np.any(dists <= self._cutoff):
            self._drag_idx = np.argmin(dists)
            self._click_start = (click_x, click_y)

        return self._drag_idx is not None

    def drag(self, drag_x, drag_y, restrictions=None):
        """
        Drag a point or a vertex in a line. Applies restrictions to the drag point based on the lock_dim
            argument to the constructor and the restrictions argument to this method.
        drag_x: x coordinate in pixels of the point to drag to.
        drag_y: y coordinate in pixels of the point to drag to.
        restrictions:   A callable object (e.g. callback function) that takes two arguments (x and y 
                            coordinates) and returns a modified x and y based on restrictions on the
                            dragging. Used, for example, to restrict dragging on the temperature line
                            to be greater than the dewpoint.
        """
        if self._drag_idx is None:
            return

        if self._lock_dim == 'x':
            drag_x = self._x_obj[self._drag_idx]
        elif self._lock_dim == 'y':
            drag_y = self._y_obj[self._drag_idx]

        if restrictions is not None:
            drag_x, drag_y = restrictions(drag_x, drag_y)

        if len(self._x_obj) == 1:
            self._dragPoint(drag_x, drag_y)
        else:
            self._dragLine(drag_x, drag_y)

    def _dragLine(self, drag_x, drag_y):
        """
        Drag a line [private method].
        drag_x: x coordinate in pixels of the drag point.
        drag_y: y coordinate in pixels of the drag point.
        """
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

        self._restoreBitmap(qp)
        self._saveBitmap(lb_x, lb_y, ub_x, ub_y)

        pen = QPen(self._line_color, 1, Qt.SolidLine)
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

    def _dragPoint(self, drag_x, drag_y):
        """
        Drag a point [private method].
        drag_x: x coordinate in pixels of the drag point
        drag_y: y coordinate in pixels of the drag point
        """
        qp = QPainter()
        qp.begin(self._background)

        self._restoreBitmap(qp)
        self._saveBitmap(drag_x, drag_y, drag_x, drag_y)

        pen = QPen(self._line_color, 1, Qt.SolidLine)
        qp.setPen(pen)

        qp.drawEllipse(QPointF(drag_x, drag_y), 3, 3)
        qp.end()
       
    def release(self, rls_x, rls_y, restrictions=None):
        """
        Release the drag, which finishes the drag operation.
        rls_x:  x coordinate in pixels of the release point
        rls_y:  y coordinate in pixels of the release point
        restrictions: [See the release argument to the drag method]
        """
        if self._drag_idx is None:
            return

        start_x, start_y = self._click_start
        if rls_x == start_x and rls_y == start_y:
            rls_x = self._x_obj[self._drag_idx]
            rls_y = self._y_obj[self._drag_idx]
        else:
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
        self._click_start = None
        return drag_idx, rls_x, rls_y

    def setBackground(self, background):
        """
        Change the background pixmap.
        background: A QPixmap containing the new background
        """
        self._background = background

    def setCoords(self, x_obj, y_obj):
        """
        Change the coordinates.
        x_obj:  x coordinate(s) in pixels of the new object
        y_obj:  y coordinate(s) in pixesl of the new object
        """
        self._x_obj = x_obj
        self._y_obj = y_obj

        if type(self._x_obj) != np.ma.MaskedArray:
            self._x_obj = np.ma.array([ self._x_obj ])
        if type(self._y_obj) != np.ma.MaskedArray:
            self._y_obj = np.ma.array([ self._y_obj ])

    def getBackground(self):
        """
        Returns the current background as a QPixmap
        """
        return self._background

    def getCoords(self):
        """
        Returns the current coordinates as numpy arrays
        """
        return self._x_obj, self._y_obj

    def isDragging(self):
        """
        Returns a boolean specifying whether or not this object is in the 
        middle of a drag operation.
        """
        return self._drag_idx is not None

    def _saveBitmap(self, lb_x, lb_y, ub_x, ub_y):
        """
        Save a section of the background image [private method]. A 5 px buffer is applied 
            in all directions.
        lb_x:   Lower bound on the x coordinate in pixels.
        ub_x:   Upper bound on the x coordinate in pixels.
        lb_y:   Lower bound on the y coordinate in pixels.
        ub_y:   Upper bound on the y coordinate in pixels.
        """
        origin = QPoint(max(lb_x - self._drag_buffer, 0), max(lb_y - self._drag_buffer, 0))
        size = QSize(ub_x - lb_x + 2 * self._drag_buffer, ub_y - lb_y + 2 * self._drag_buffer)
        bmap = self._background.copy(QRect(origin, size))
        self._save_bitmap = (origin, size, bmap)

    def _restoreBitmap(self, qp):
        """
        Restore the section of the background image saved by _saveBitmap [private method].
        qp: A QPainter to use to draw the bitmap.
        """
        if self._save_bitmap is not None:
            (origin, size, bmap) = self._save_bitmap
            qp.drawPixmap(origin, bmap, QRect(QPoint(0, 0), size))

