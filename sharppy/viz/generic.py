__author__ = 'Kelton Halbert'

__all__ = ['backgroundGeneric', 'plotGeneric']

import numpy as np
from sharppy.sharptab.constants import *
from PySide import QtGui, QtCore
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtOpenGL import *

class backgroundGeneric(QtGui.QFrame):
    """
    A generic class for drawing the background of a widget.
    """

    def __init__(self, **kwargs):
        super(backgroundGeneric, self).__init__()
        self.initUI(**kwargs)

    def initUI(self, **kwargs):
        """
        Initialize the user interface. This will set necessary constants
        such as margins, min/max axes values, font sizes, etc.

        :return: None
        """

        ## initialize the frame variables
        self.lpad = 0.; self.rpad = 0.
        self.bpad = 20.; self.tpad = 0.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt

        ## set the default min/max axes range.
        self.xmin = 0.; self.xmax = 100.
        self.ymin = 0.; self.ymax = 100.

        ## initialize background and border color
        self.backgroundColor = kwargs.get('background', BLACK)
        self.borderColor = kwargs.get('border', WHITE)

        ## initialize the QPixmap that everything gets drawn on
        self.plotBitMap = QtGui.QPixmap(self.size().width(), self.size().height())
        self.plotBitMap.fill(QtCore.Qt.black)

        ## and draw the background
        self.plotBackground()

    def plotBackground(self):
        """
        Handles the drawing of the background on the widget.
        :return: None
        """

        ## initialize a new QPainter object for drawing the stuffs
        qp = QtGui.QPainter()
        ## draw onto the QPixmap
        qp.begin(self.plotBitMap)
        ## these settings usually give better performance
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw background frame
        self.draw_frame(qp)
        ## end the painter
        qp.end()


    def resizeEvent(self, e):
        """
        Handles what to do when the widget is resized.
        This will call self.initUI() when resized in order
        to re-generate the necessary variables.

        :return: None
        """

        self.initUI()

    def x_to_pix(self, x):
        """
        Scale an x coordinate value to pixel space and return it.

        :param x: An x coordinate value
        :return: x converted to pixel space
        """

        scl1 = self.xmax - self.xmin
        scl2 = self.xmax - x
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def y_to_pix(self, y):
        """
        Scale a y coordinate value to pixel space and return it.

        :param y: A y coordinate value
        :return: y converted to pixel space
        """

        scl1 = self.ymax - self.ymin
        scl2 = self.ymax - y
        return self.bry - (scl2 / scl1 ) * ( self.bry - self.tpad)

    def draw_frame(self, qp):
        """
        Draws the background frame for the widget. The background
        frame includes the background color and the frame border.
        This is primarily used in the initUI function and is not
        necessarily intended to be called outside of it.

        :param qp: QtGui.QPainter object
        :return: None
        """

        ## initialize a new pen and brush
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## draw the borders in white
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)

    def set_xlim(self, xmin, xmax):
        """
        Set the range of values for the x axis.

        :param xmin: The minimum x axis value
        :param xmax: The maximum x axis value
        :return: None
        """

        self.xmin = xmin; self.xmax = xmax

    def set_ylim(self, ymin, ymax):
        """
        Set the range of values for the y axis.

        :param ymin: The minimum y axis value
        :param ymax: The maximum y axis value
        :return: None
        """

        self.ymin = ymin; self.ymax = ymax


class plotGeneric(backgroundGeneric):
    """
    A generic object to plot the foreground of a plot.
    This inherits from the Background Class that holds
    frame constants, getters, and setters.
    """
    def __init__(self, x, y, **kwargs):
        ## construct the super object
        super(plotGeneric, self).__init__(**kwargs)
        ## set some object variables
        self.x = x; self.y = y
        self.color = kwargs.get('color', RED)
        self.width = kwargs.get('width', 2)
        ## reset the x and y limits based on the data given

    def resizeEvent(self, e):
        """
        Handles the resizing of the frame

        :param e: an Event object
        :return: None
        """
        super(plotGeneric, self).resizeEvent(e)
        ## update the min and max bounds based on the data
        self.set_xlim( self.x.min()-10, self.x.max()+10)
        self.set_ylim( self.y.min(), self.y.max())
        ## you have to call update after setting the variables
        self.update()
        self.plotData()

    def paintEvent(self, e):
        """
        Handles the paint event and calls the functions
        to draw on the frame.

        :param e: an Event object
        :return: None
        """

        super(backgroundGeneric, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
        qp.end()

    def plotData(self):
        """
        Plot the data on the frame.
        :return: None
        """
        ## create a new painter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.draw_lines(qp)
        ## end the painter
        qp.end()

    def draw_lines(self, qp):
        """
        Draw the line profile on the widget

        :param qp: QtGui.QPainter object
        :return: None
        """
        ## initialize a new pen
        pen = QtGui.QPen(QtGui.QColor(self.color), self.width)
        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## initialize a painter path
        path = QPainterPath()

        ## get the data mask if there is one
        try:
            mask1 = self.x.mask
            mask2 = self.y.mask
            mask = np.maximum(mask1, mask2)
            y = self.y[~mask]
            x = self.x[~mask]

        ## if the data is not masked, just use the provided arrays!
        except:
            y = self.y
            x = self.x

        ## start the path at the first data value
        path.moveTo(self.x_to_pix(x[0]), self.y_to_pix(y[0]))
        ## now we need to loop through the array
        for i in range( 1, y.shape[0] ):
            ## make sure we are plotting in our minimum and maximum bounds
            if y[i] > self.ymin and y[i] < self.ymax:
                xp = x[i]; yp = y[i]
                ## convert from unit space to pixel space
                x1 = self.x_to_pix(xp)
                y1 = self.y_to_pix(yp)
                ## set the pen and draw a line between the two points
                path.lineTo(x1, y1)

            ## if we are outside our bounds, stop drawing
            else:
                continue
        qp.drawPath(path)

