import numpy as np
import os
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
import sharppy.sharptab.utils as utils
import sharppy.databases.inset_data as inset_data
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundVROT', 'plotVROT']

class backgroundVROT(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the Theta-E plot frame
    '''
    def __init__(self):
        super(backgroundVROT, self).__init__()
        self.initUI()


    def initUI(self):
        ## window configuration settings,
        ## sich as padding, width, height, and
        ## min/max plot axes
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        if self.physicalDpiX() > 75:
            fsize = 10
        else:
            fsize = 11
                
        self.font_ratio = 0.0512
        self.plot_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio + 1))
        self.label_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio ))
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.label_metrics = QtGui.QFontMetrics(self.label_font)
        self.plot_height = self.plot_metrics.xHeight() + 5
        self.label_height = self.label_metrics.xHeight() + 5
        self.vrot_inset_data = inset_data.vrotData()
        self.lpad = 5.; self.rpad = 0.
        self.tpad = 5 + self.plot_height + self.label_height ;
        self.bpad = self.label_height + 5
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.probmax = 70.; self.probmin = 0.
        self.vrotmax = 110.; self.vrotmin = 0
        self.EF01_color = "#006600"
        self.EF23_color = "#FFCC33"
        self.EF45_color = "#FF00FF"
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        Handles painting the frame.
        '''
        ## initialize a painter object and draw the frame
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        self.draw_frame(qp)
        qp.end()

    def setBlackPen(self, qp):
        color = QtGui.QColor(self.bg_color)
        color.setAlphaF(.5)
        pen = QtGui.QPen(color, 0, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        qp.setBrush(brush)
        return qp

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with

        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRectF(1.5, 2, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Conditional EF-scale Probs based on Vrot')

        qp.setFont(QtGui.QFont('Helvetica',  self.size().height() * self.font_ratio))
        color = QtGui.QColor(self.EF01_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(25), 4 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF0-EF1')

        color = QtGui.QColor(self.EF23_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(50), 4 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF2-EF3')

        color = QtGui.QColor(self.EF45_color)
        pen = QtGui.QPen(color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect1 = QtCore.QRectF(self.vrot_to_pix(75), 4 + self.plot_height, 10, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'EF4-EF5')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)

        # Plot all of the Y-ticks for the probabilities
        ytick_fontsize =  round(self.size().height() * self.font_ratio)
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        texts = self.vrot_inset_data['ytexts']
        spacing = self.bry / 10.
        for i in range(len(texts)):
            pen = QtGui.QPen(QtGui.QColor("#0080FF"), 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            try:
                qp.drawLine(self.tlx, self.prob_to_pix(int(texts[i])), self.brx, self.prob_to_pix(int(texts[i])))
            except:
                continue
            color = QtGui.QColor(self.bg_color)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = spacing*(i+1) - (spacing/4.)
            ypos = self.prob_to_pix(int(texts[i])) - ytick_fontsize/2
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])

        width = self.brx / 12
        texts = np.arange(10, 110, 10)

        # Draw the x tick marks
        
        qp.setFont(QtGui.QFont('Helvetica', self.font_ratio * self.hgt ))
        for i in range(texts.shape[0]):
            color = QtGui.QColor(self.bg_color)
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRectF(self.vrot_to_pix(texts[i]) - width/2, self.bry + self.bpad/2, width, 4)
            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, str(texts[i]))
        
        xpts = self.vrot_inset_data['xpts']
        
        # Draw the EF1+ stuff
        ef01 = self.vrot_inset_data['EF0-EF1']
        color = QtGui.QColor(self.EF01_color)
        lastprob = ef01[0]
        if lastprob > 70:
            lastprob = 70
        for i in range(1, np.asarray(xpts).shape[0], 1):
            if ef01[i] > 70:
                prob = 70
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.DotLine)
                qp.setPen(pen)
            else:
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                prob = ef01[i]

            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob

        # Draw the EF2-EF3 stuff
        ef23 = self.vrot_inset_data['EF2-EF3']
        color = QtGui.QColor(self.EF23_color)
        lastprob = ef23[0]
        if lastprob > 70:
            lastprob = 70
        for i in range(1, np.asarray(xpts).shape[0], 1):
            if ef23[i] > 70:
                prob = 70
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.DotLine)
                qp.setPen(pen)
            else:
                pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                prob = ef23[i]

            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob

        # Draw the EF4-EF5 stuff
        ef45 = self.vrot_inset_data['EF4-EF5']
        color = QtGui.QColor(self.EF45_color)
        lastprob = ef45[0]
        for i in range(1, np.asarray(xpts).shape[0], 1):
            pen = QtGui.QPen(color, 2.5, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            prob = ef45[i]
            qp.drawLine(self.vrot_to_pix(xpts[i-1]), self.prob_to_pix(lastprob), self.vrot_to_pix(xpts[i]), self.prob_to_pix(prob))
            lastprob = prob
        
    def prob_to_pix(self, prob):
        scl1 = self.probmax - self.probmin
        scl2 = self.probmin + prob
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)

    def vrot_to_pix(self, vrot):
        '''
        Function to convert a wind speed value to a X pixel.
        
        Parameters
        ----------
        s: speed in kts
        '''
        scl1 = self.vrotmax - self.vrotmin
        scl2 = self.vrotmax - vrot
        return self.lpad + self.brx - (scl2 / scl1) * (self.brx - self.rpad)


class plotVROT(backgroundVROT):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')

        super(plotVROT, self).__init__()
        self.prof = None
        self.vrot = 0

    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotVROT, self).resizeEvent(e)
        self.interp_vrot()
        self.plotData()

    def paintEvent(self, e):
        super(plotVROT, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()

    def setProf(self, prof):
        return

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            self.plotBitMap.fill(self.bg_color)
            self.plotBackground()
            self.interp_vrot()
            self.plotData()
            self.update()

    def plotData(self):
        '''
        Handles painting on the frame
        '''
        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        self.draw_vrot(qp)

    def interp_vrot(self):
        self.probef01 = self.vrot_inset_data['EF0-EF1'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]
        self.probef23 = self.vrot_inset_data['EF2-EF3'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]
        self.probef45 = self.vrot_inset_data['EF4-EF5'][np.argmin(np.abs(self.vrot - self.vrot_inset_data['xpts']))]

    def mouseDoubleClickEvent(self, e):
        super(plotVROT, self).resizeEvent(e)
        self.openInputDialog()
        self.interp_vrot()
        self.plotData()
        self.update()

    def openInputDialog(self):
        """
        Opens the text version of the input dialog
        """
        text, result = QtGui.QInputDialog.getText(None, "VROT Input",
                                            "Enter the VROT:")
        if result:
            self.vrot = int(text)

    def draw_vrot(self, qp):
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        vrot_pix = self.vrot_to_pix(self.vrot)
        # plot the white dashed line
        pen = QtGui.QPen(self.fg_color, 1.5, QtCore.Qt.DotLine)
        qp.setPen(pen)
        qp.drawLine(vrot_pix, self.prob_to_pix(0), vrot_pix, self.prob_to_pix(70))
        
        # Draw the probabilties.
        color = QtGui.QColor(self.EF01_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot-7), self.prob_to_pix(self.probef01), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, utils.INT2STR(self.probef01))

        color = QtGui.QColor(self.EF23_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot), self.prob_to_pix(self.probef23), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, utils.INT2STR(self.probef23))

        color = QtGui.QColor(self.EF45_color)
        pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        rect = QtCore.QRectF(self.vrot_to_pix(self.vrot), self.prob_to_pix(self.probef45), 4, 7)
        qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, utils.INT2STR(self.probef45))
        qp.end()



if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    tester = plotVROT()
    tester.setGeometry(50,50,293,195)
    tester.show()        
    app_frame.exec_()
