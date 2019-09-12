import numpy as np
import os
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
import sharppy.databases.inset_data as inset_data
from sharppy.sharptab.constants import *
import platform

## routine written by Kelton Halbert and Greg Blumberg
## keltonhalbert@ou.edu and wblumberg@ou.edu

__all__ = ['backgroundSTP', 'plotSTP']

class backgroundSTP(QtWidgets.QFrame):
    '''
    Draw the background frame and lines for the STP plot frame
    '''
    def __init__(self):
        super(backgroundSTP, self).__init__()
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
        self.textpad = 5
        self.font_ratio = 0.0512
        fsize1 = round(self.size().height() * self.font_ratio) + 2
        fsize2 = round(self.size().height() * self.font_ratio)
        self.plot_font = QtGui.QFont('Helvetica', fsize1 )
        self.box_font = QtGui.QFont('Helvetica', fsize2)
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.box_metrics = QtGui.QFontMetrics(self.box_font)
        if platform.system() == "Windows":
            fsize1 -= self.plot_metrics.descent()
            fsize2 -= self.box_metrics.descent()

            self.plot_font = QtGui.QFont('Helvetica', fsize1 )
            self.box_font = QtGui.QFont('Helvetica', fsize2)
            self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
            self.box_metrics = QtGui.QFontMetrics(self.box_font)
        self.plot_height = self.plot_metrics.xHeight()# + self.textpad
        self.box_height = self.box_metrics.xHeight() + self.textpad
        self.tpad = self.plot_height + 15; 
        self.bpad = self.plot_height + 2
        self.lpad = 0.; self.rpad = 0.
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad;
        self.brx = self.wid; 
        self.bry = self.hgt - self.bpad#+ round(self.font_ratio * self.hgt)
        self.stpmax = 11.; self.stpmin = 0.
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

    def draw_frame(self, qp):
        '''
        Draw the background frame.
        qp: QtGui.QPainter object
        '''
        ## set a new pen to draw with
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.plot_font)
        # Left, top, width, height
        rect1 = QtCore.QRectF(0,5, self.brx, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'Effective Layer STP (with CIN)')

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)

        ytick_fontsize = round(self.font_ratio * self.hgt) + 1
        y_ticks_font = QtGui.QFont('Helvetica', ytick_fontsize)
        qp.setFont(y_ticks_font)
        stp_inset_data = inset_data.stpData()
        texts = stp_inset_data['stp_ytexts']
        # Plot the y-tick labels for the box and whisker plots
        for i in range(len(texts)):
            pen = QtGui.QPen(self.line_color, 1, QtCore.Qt.DashLine)
            qp.setPen(pen)
            tick_pxl = self.stp_to_pix(int(texts[i]))
            qp.drawLine(self.tlx, tick_pxl, self.brx, tick_pxl)
            color = QtGui.QColor(self.bg_color)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            ypos = tick_pxl - ytick_fontsize/2
            rect = QtCore.QRect(self.tlx, ypos, 20, ytick_fontsize)
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])
        
        # Draw the box and whisker plots and the x-tick labels
        ef = stp_inset_data['ef']
        width = self.brx / 14
        spacing = self.brx / 7
        center = np.arange(spacing, self.brx, spacing)
        texts = stp_inset_data['stp_xtexts']
        ef = self.stp_to_pix(ef)
        qp.setFont(QtGui.QFont('Helvetica', round(self.font_ratio * self.hgt)))
        for i in range(ef.shape[0]):
            # Set green pen to draw box and whisker plots 
            pen = QtGui.QPen(self.box_color, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            # Draw lower whisker
            qp.drawLine(center[i], ef[i,0], center[i], ef[i,1])
            # Draw box
            qp.drawLine(center[i] - width/2., ef[i,3], center[i] + width/2., ef[i,3])
            qp.drawLine(center[i] - width/2., ef[i,1], center[i] + width/2., ef[i,1])
            qp.drawLine(center[i] - width/2., ef[i,1], center[i] - width/2., ef[i,3])
            qp.drawLine(center[i] + width/2., ef[i,1], center[i] + width/2., ef[i,3])
            # Draw median
            qp.drawLine(center[i] - width/2., ef[i,2], center[i] + width/2., ef[i,2])
            # Draw upper whisker
            qp.drawLine(center[i], ef[i,3], center[i], ef[i,4])
            # Set black transparent pen to draw a rectangle
            color = QtGui.QColor(self.bg_color)
            color.setAlpha(0)
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            rect = QtCore.QRectF(center[i] - width/2., self.bry + round(self.bpad/2), width, self.bpad)

            # Change to a white pen to draw the text below the box and whisker plot
            pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, texts[i])
            #qp.drawText(rect, QtCore.Qt.AlignCenter, texts[i])

    def stp_to_pix(self, stp):
        scl1 = self.stpmax - self.stpmin
        scl2 = self.stpmin + stp
        return self.bry - (scl2 / scl1) * (self.bry - self.tpad)


class plotSTP(backgroundSTP):
    '''
    Plot the data on the frame. Inherits the background class that
    plots the frame.
    '''
    def __init__(self):
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.box_color = QtGui.QColor('#00ff00')
        self.line_color = QtGui.QColor('#0080ff')

        self.alert_colors = [
            QtGui.QColor('#775000'),
            QtGui.QColor('#996600'),
            QtGui.QColor('#ffffff'),
            QtGui.QColor('#ffff00'),
            QtGui.QColor('#ff0000'),
            QtGui.QColor('#e700df'),
        ]

        self.use_left = False

        super(plotSTP, self).__init__()
        self.prof = None

    def setProf(self, prof):
        self.prof = prof

        self.mlcape = prof.mlpcl.bplus
        self.mllcl = prof.mlpcl.lclhght
        self.ebwd = prof.ebwspd

        if self.use_left:
            self.esrh = prof.left_esrh[0]
            self.stpc = prof.left_stp_cin
            self.stpf = prof.left_stp_fixed
        else:
            self.esrh = prof.right_esrh[0]
            self.stpc = prof.right_stp_cin
            self.stpf = prof.right_stp_fixed

        if self.prof.latitude < 0:
            self.esrh = -self.esrh
            self.stpc = -self.stpc
            self.stpf = -self.stpf

        ## get the probabilities
        self.cape_p, self.cape_c = self.cape_prob(self.mlcape)
        self.lcl_p, self.lcl_c = self.lcl_prob(self.mllcl)
        self.esrh_p, self.esrh_c = self.esrh_prob(self.esrh)
        self.ebwd_p, self.ebwd_c = self.ebwd_prob(self.ebwd)
        self.stpc_p, self.stpc_c = self.stpc_prob(self.stpc)
        self.stpf_p, self.stpf_c = self.stpf_prob(self.stpf)

        #self.ylast = self.tpad
        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])
        self.box_color = QtGui.QColor(prefs['stp_box_color'])
        self.line_color = QtGui.QColor(prefs['stp_line_color'])

        self.alert_colors = [
            QtGui.QColor(prefs['alert_l1_color']),
            QtGui.QColor(prefs['alert_l2_color']),
            QtGui.QColor(prefs['alert_l3_color']),
            QtGui.QColor(prefs['alert_l4_color']),
            QtGui.QColor(prefs['alert_l5_color']),
            QtGui.QColor(prefs['alert_l6_color']),
        ]

        if update_gui:
            if self.use_left:
                self.esrh = self.prof.left_esrh[0]
                self.stpc = self.prof.left_stp_cin
                self.stpf = self.prof.left_stp_fixed
            else:
                self.esrh = self.prof.right_esrh[0]
                self.stpc = self.prof.right_stp_cin
                self.stpf = self.prof.right_stp_fixed

            if self.prof is not None and  self.prof.latitude < 0:
                self.esrh = -self.esrh
                self.stpc = -self.stpc
                self.stpf = -self.stpf

            self.cape_p, self.cape_c = self.cape_prob(self.mlcape)
            self.lcl_p, self.lcl_c = self.lcl_prob(self.mllcl)
            self.esrh_p, self.esrh_c = self.esrh_prob(self.esrh)
            self.ebwd_p, self.ebwd_c = self.ebwd_prob(self.ebwd)
            self.stpc_p, self.stpc_c = self.stpc_prob(self.stpc)
            self.stpf_p, self.stpf_c = self.stpf_prob(self.stpf)

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        if self.use_left:
            self.esrh = self.prof.left_esrh[0]
            self.stpc = self.prof.left_stp_cin
            self.stpf = self.prof.left_stp_fixed
        else:
            self.esrh = self.prof.right_esrh[0]
            self.stpc = self.prof.right_stp_cin
            self.stpf = self.prof.right_stp_fixed

        if self.prof.latitude < 0:
            self.esrh = -self.esrh
            self.stpc = -self.stpc
            self.stpf = -self.stpf

        self.esrh_p, self.esrh_c = self.esrh_prob(self.esrh)
        self.stpc_p, self.stpc_c = self.stpc_prob(self.stpc)
        self.stpf_p, self.stpf_c = self.stpf_prob(self.stpf)

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def cape_prob(self, cape):
        if cape == 0.:
            prob = 0.00
            color = self.alert_colors[0]
        elif cape  > 0. and cape < 250.:
            prob = .12
            color = self.alert_colors[1]
        elif cape >= 250. and cape < 500.:
            prob = .14
            color = self.alert_colors[2]
        elif cape >= 500. and cape < 1000.:
            prob = .16
            color = self.alert_colors[2]
        elif cape >= 1000. and cape < 1500.:
            prob = .15
            color = self.alert_colors[2]
        elif cape >= 1500. and cape < 2000.:
            prob = .13
            color = self.alert_colors[2]
        elif cape >= 2000. and cape < 2500.:
            prob = .14
            color = self.alert_colors[2]
        elif cape >= 2500. and cape < 3000.:
            prob = .18
            color = self.alert_colors[3]
        elif cape >= 3000. and cape < 4000.:
            prob = .20
            color = self.alert_colors[3]
        elif cape >= 4000.:
            prob = .16
            color = self.alert_colors[3]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color
    
    def lcl_prob(self, lcl):
        if lcl < 750.:
            prob = .19
            color = self.alert_colors[3]
        elif lcl >= 750. and lcl < 1000.:
            prob = .19
            color = self.alert_colors[3]
        elif lcl >= 1000. and lcl < 1250.:
            prob = .15
            color = self.alert_colors[2] 
        elif lcl >= 1250. and lcl < 1500.:
            prob = .10
            color = self.alert_colors[1]
        elif lcl >= 1500. and lcl < 1750:
            prob = .06
            color = self.alert_colors[0]
        elif lcl >= 1750. and lcl < 2000.:
            prob = .06
            color = self.alert_colors[0]
        elif lcl >= 2000. and lcl < 2500.:
            prob = .02
            color = self.alert_colors[0]
        elif lcl >= 2500:
            prob = 0.0
            color = self.alert_colors[0]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color
    
    def esrh_prob(self, esrh):
        if esrh < 50.:
            prob = .06
            color = self.alert_colors[0]
        elif esrh >= 50. and esrh < 100.:
            prob = .06
            color = self.alert_colors[0]
        elif esrh >= 100. and esrh < 200.:
            prob = .08
            color = self.alert_colors[1]
        elif esrh >= 200. and esrh < 300:
            prob = .14
            color = self.alert_colors[2]
        elif esrh >= 300. and esrh < 400.:
            prob = .20
            color = self.alert_colors[3]
        elif esrh >= 400. and esrh < 500.:
            prob = .27
            color = self.alert_colors[3]
        elif esrh >= 500. and esrh < 600:
            prob = .38
            color = self.alert_colors[4]
        elif esrh >= 600. and esrh < 700.:
            prob = .37
            color = self.alert_colors[4]
        elif esrh >= 700:
            prob = .42
            color = self.alert_colors[4]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color
    
    def ebwd_prob(self, ebwd):
        if ebwd == 0.:
            prob = 0.0
            color = self.alert_colors[0]
        elif ebwd >= .01 and ebwd < 20.:
            prob = .03
            color = self.alert_colors[0]
        elif ebwd >= 20. and ebwd < 30.:
            prob = .05
            color = self.alert_colors[0]
        elif ebwd >= 30. and ebwd < 40.:
            prob = .06
            color = self.alert_colors[0]
        elif ebwd >= 40. and ebwd < 50.:
            prob = .12
            color = self.alert_colors[1]
        elif ebwd >= 50. and ebwd < 60.:
            prob = .19
            color = self.alert_colors[3]
        elif ebwd >= 60. and ebwd < 70.:
            prob = .27
            color = self.alert_colors[3]
        elif ebwd >= 70. and ebwd < 80.:
            prob = .36
            color = self.alert_colors[4]
        elif ebwd >= 80.:
            prob = .26
            color = self.alert_colors[3]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color

    def stpc_prob(self, stpc):
        if stpc < .1:
            prob = .06
            color = self.alert_colors[0]
        elif stpc >= .1 and stpc < .50:
            prob = .08
            color = self.alert_colors[1]
        elif stpc >= .5 and stpc < 1.0:
            prob = .12
            color = self.alert_colors[1]
        elif stpc >= 1. and stpc < 2.:
            prob = .17
            color = self.alert_colors[2]
        elif stpc >= 2. and stpc < 4.:
            prob = .25
            color = self.alert_colors[3]
        elif stpc >= 4. and stpc < 6.:
            prob = .32
            color = self.alert_colors[4]
        elif stpc >= 6. and stpc < 8.:
            prob = .34
            color = self.alert_colors[4]
        elif stpc >= 8. and stpc < 10.:
            prob = .55
            color = self.alert_colors[5]
        elif stpc >= 10.:
            prob = .58
            color = self.alert_colors[5]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color

    def stpf_prob(self, stpf):
        if stpf < .1:
            prob = .05
            color = self.alert_colors[0]
        elif stpf >= .1 and stpf < .5:
            prob = .06
            color = self.alert_colors[0]
        elif stpf >= .5 and stpf < 1.:
            prob = .11
            color = self.alert_colors[1]
        elif stpf >= 1. and stpf < 2.:
            prob = .17
            color = self.alert_colors[2]
        elif stpf >= 2. and stpf < 3.:
            prob = .25
            color = self.alert_colors[3]
        elif stpf >= 3. and stpf < 5.:
            prob = .25
            color = self.alert_colors[3]
        elif stpf >= 5. and stpf < 7.:
            prob = .39
            color = self.alert_colors[4]
        elif stpf >= 7. and stpf < 9.:
            prob = .55
            color = self.alert_colors[5]
        elif stpf >= 9.:
            prob = .59
            color = self.alert_colors[5]
        else:
            prob = np.ma.masked
            color = self.alert_colors[0]
        return prob, color


    def resizeEvent(self, e):
        '''
        Handles when the window is resized
        '''
        super(plotSTP, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotSTP, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)
    
    def plotData(self):
        '''
        Handles painting on the frame
        '''
        if self.prof is None:
            return

        ## this function handles painting the plot
        ## create a new painter obkect
        qp = QtGui.QPainter()
        self.draw_stp(qp)
        self.draw_box(qp)

    def draw_stp(self, qp):
        if not tab.utils.QC(self.stpc):
            return

        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)

        if self.stpc < 0:
            self.stpc = 0
        elif self.stpc > 11.:
            self.stpc = 11.
        prob, color = self.stpc_prob(self.stpc) 
        ef = self.stp_to_pix(self.stpc)
        pen = QtGui.QPen(color, 1.5, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, ef, self.wid, ef)
        qp.end()

    def draw_box(self, qp):
        qp.begin(self.plotBitMap)
        width = self.brx / 14.
        left_x = width * 7
        right_x = self.brx - 5.
        top_y = self.stp_to_pix(11.)
        vspace = self.box_height + 1
        if platform.system() == "Windows":
            vspace += self.box_metrics.descent()
        bot_y = top_y + vspace * 8
        ## fill the box with a black background
        brush = QtGui.QBrush(self.bg_color, QtCore.Qt.SolidPattern)
        pen = QtGui.QPen(self.bg_color, 0, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawRect(left_x, top_y, right_x - left_x, bot_y - top_y)
        ## draw the borders of the box
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setPen(pen)
        qp.setBrush(brush)
        qp.drawLine( left_x, top_y, right_x, top_y )
        qp.drawLine( left_x, bot_y, right_x, bot_y )
        qp.drawLine( left_x, top_y, left_x, bot_y )
        qp.drawLine( right_x, top_y, right_x, bot_y)
        ## set the font and line width for the rest of the plotting
        qp.setFont(self.box_font)
        ## plot the left column of text
        width = right_x - left_x - 3
        y1 = top_y + 2
        x1 = left_x+3
        x2 = x1 + (width * .75)
        ## start with the header/title
        texts = ['Prob EF2+ torn with supercell', 'Sample CLIMO = .15 sigtor']
        for text in texts:
            rect = QtCore.QRectF(x1, y1, width, self.box_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            vspace = self.box_height + 1
            if platform.system() == "Windows":
                vspace += self.box_metrics.descent()
            y1 += vspace
        vspace = y1 - 1
        if platform.system() == "Windows":
            vspace += 2
        qp.drawLine(left_x, vspace, right_x, vspace)
        ## draw the variable names
        texts = ['based on CAPE: ', 'based on LCL:', 'based on ESRH:', 'based on EBWD:',
                 'based on STPC:', 'based on STP_fixed:' ]
        probs = [self.cape_p, self.lcl_p, self.esrh_p, self.ebwd_p, self.stpc_p, self.stpf_p]
        colors = [self.cape_c, self.lcl_c, self.esrh_c, self.ebwd_c, self.stpc_c, self.stpf_c]
        for text, p, c in zip(texts, probs, colors):
            pen = QtGui.QPen(c, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRectF(x1, y1, width, self.box_height)
            rect2 = QtCore.QRectF(x2, y1, width, self.box_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text)
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, tab.utils.FLOAT2STR(p,2) )
            vspace = self.box_height
            if platform.system() == "Windows":
                vspace += self.box_metrics.descent()
            y1 += vspace
        qp.end()

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    tester = plotSTP()
    tester.setGeometry(50,50,293,195)
    #tester.plotBitMap.save('test.png', format='png')
    tester.show()        
    app_frame.exec_()
