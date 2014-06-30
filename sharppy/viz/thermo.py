import numpy as np
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import datetime

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundText', 'plotText']

class backgroundText(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundText, self).__init__()
        self.initUI()

    def initUI(self):
        ## initialize fram variables such as size,
        ## padding, etc.
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        self.label_font = QtGui.QFont('Helvetica', 10)
        self.severe_font = QtGui.QFont('Helvetica', 12)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.severe_metrics = QtGui.QFontMetrics( self.severe_font )
        self.label_height = self.label_metrics.height()
        self.label_height = self.severe_metrics.height()
        self.lpad = 0; self.rpad = 0
        self.tpad = 5; self.bpad = 0
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(QtCore.Qt.black)
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        x1 = self.brx / 8
        y1 = 1
        ## draw the header for the indices
        count = 0
        titles = ['PCL', 'CAPE', 'CINH', 'LCL', 'LI', 'LFC', 'EL']
        for title in titles:
            rect = QtCore.QRect(x1*count, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, title)
            count += 1
        qp.drawLine(0, self.label_height, self.brx, self.label_height)
    
    def resizeEvent(self, e):
        '''
        Handles when the window gets resized.
        '''
        self.initUI()

    def plotBackground(self):
        '''
        Handles drawing the text background.
        '''
        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the frame
        self.draw_frame(qp)
        qp.end()


class plotText(backgroundText):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.sfcparcel = prof.sfcpcl
        self.mlparcel = prof.mlpcl
        self.fcstpcl = prof.fcstpcl
        self.muparcel = prof.mupcl
        self.prof = prof;
        
        
        ## either get or calculate the indices, round to the nearest int, and
        ## convert them to strings.
        ## K Index
        self.k_idx = tab.utils.INT2STR( prof.k_idx )
        ## precipitable water
        self.pwat = tab.utils.FLOAT2STR( prof.pwat, 2 )
        ## 0-3km agl lapse rate
        self.lapserate_3km = tab.utils.FLOAT2STR( prof.lapserate_3km, 1 )
        ## 3-6km agl lapse rate
        self.lapserate_3_6km = tab.utils.FLOAT2STR( prof.lapserate_3_6km, 1 )
        ## 850-500mb lapse rate
        self.lapserate_850_500 = tab.utils.FLOAT2STR( prof.lapserate_850_500, 1 )
        ## 700-500mb lapse rate
        self.lapserate_700_500 = tab.utils.FLOAT2STR( prof.lapserate_700_500, 1 )
        ## convective temperature
        self.convT = tab.utils.INT2STR( prof.convT )
        ## sounding forecast surface temperature
        self.maxT = tab.utils.INT2STR( prof.maxT )
        #fzl = str(int(self.sfcparcel.hght0c))
        ## 100mb mean mixing ratio
        self.mean_mixr = tab.utils.FLOAT2STR( prof.mean_mixr, 1 )
        ## 150mb mean rh
        self.low_rh = tab.utils.INT2STR( prof.low_rh )
        self.mid_rh = tab.utils.INT2STR( prof.mid_rh )
        ## calculate the totals totals index
        self.totals_totals = tab.utils.INT2STR( prof.totals_totals )
        self.dcape = tab.utils.INT2STR( prof.dcape )
        self.drush = tab.utils.INT2STR( prof.drush )
        self.sigsevere = tab.utils.INT2STR( prof.sig_severe )
        self.mmp = tab.utils.FLOAT2STR( prof.mmp, 2 )
        self.esp = tab.utils.FLOAT2STR( prof.esp, 1 )
        self.wndg = tab.utils.FLOAT2STR( prof.wndg, 1 )
        self.tei = tab.utils.INT2STR( prof.tei )
        
        super(plotText, self).__init__()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotText, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotText, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()

    def plotData(self):
        '''
        Handles the drawing of the text on the frame.
        '''
        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the indices
        self.drawConvectiveIndices(qp)
        self.drawIndices(qp)
        self.drawSevere(qp)
        qp.end()
    
    def drawSevere(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## initialize a pen to draw with.
        pen = QtGui.QPen(QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine)
        qp.setFont(self.label_font)
        color_list = [QtGui.QColor('#A05030'), QtGui.QColor('#D0A020'),
             QtCore.Qt.yellow, QtGui.QColor("#FF4000"), QtCore.Qt.red, QtCore.Qt.magenta]
        ## needs to be coded.
        x1 = self.brx / 10
        y1 = self.bry / 17 * 12 + self.tpad
        ship = tab.utils.FLOAT2STR( self.prof.ship, 1 )
        stp_fixed = tab.utils.FLOAT2STR( self.prof.stp_fixed, 1 )
        stp_cin = tab.utils.FLOAT2STR( self.prof.stp_cin, 1 )
        right_scp = tab.utils.FLOAT2STR( self.prof.right_scp, 1 )
        
        labels = ['Supercell = ', 'STP (cin) = ', 'STP (fix) = ', 'Sig Hail = ']
        indices = [right_scp, stp_cin, stp_fixed, ship]
        for label, index in zip(labels,indices):
            rect = QtCore.QRect(x1*7, y1, x1*8, self.label_height)
            if float(index) < 1:
                pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
            elif float(index) < 2:
                pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
            elif float(index) < 5:
                pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
            elif float(index) < 10:
                pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
            elif float(index) < 20:
                pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
            else:
                pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, label + index)
            y1 += (self.label_height-1)
    
    def drawIndices(self, qp):
        '''
        Draw the non-parcel indices.
        --------
        qp: QtGui.QPainter object
        '''
        qp.setFont(self.label_font)
        ## make the initial x point relatice to the width of the frame.
        x1 = self.brx / 10
        rpad = 5
        tpad = 5

        ## Now we have all the data we could ever want. Time to start drawing
        ## them on the frame.
        ## This starts with the left column.
        
        #if self.prof.pwv_flag == -3:
        #    color = QtGui.QColor('#DA9167')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #elif self.prof.pwv_flag == -2:
        #    color = QtGui.QColor('#FFE1B7')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #elif self.prof.pwv_flag == -1:
        #    color = QtGui.QColor('#FFFFD5')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #elif self.prof.pwv_flag == 0:
        #    color = QtGui.QColor('#FFFFFF')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #elif self.prof.pwv_flag == 1:
        #    color = QtGui.QColor('#D6FFD6')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #elif self.prof.pwv_flag == 2:
        #    color = QtGui.QColor('#A4CDA4')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #else:
        #    color = QtGui.QColor('#008000')
        #    pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        #qp.setPen(pen)
        #qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'PW = ' + self.pwat + 'in')
        #pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        #qp.setPen(pen)
        
        y1 = self.bry / 17 * 6
        texts = ['PW = ', 'MeanW = ', 'LowRH = ', 'MidRH = ', 'DCAPE = ', 'DownT = ']
        indices = [self.pwat + 'in', self.mean_mixr + 'g/kg', self.low_rh + '%', self.mid_rh + '%', self.dcape, self.drush + 'F']
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(rpad, y1, x1*4, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            y1 += (self.label_height-2)
        
        y1 = self.bry / 17 * 12 + self.tpad
        texts = ['Sfc-3km AGL LR = ', '3-6km AGL LR = ', '850-500mb LR = ', '700-500mb LR = ']
        indices = [self.lapserate_3km + ' C/km', self.lapserate_3_6km + ' C/km', self.lapserate_850_500 + ' C/km', self.lapserate_700_500 + ' C/km']
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(rpad, y1, x1*8, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            y1 += (self.label_height-2)

        ## middle-left column
        y1 = self.bry / 17 * 6
        texts = ['K = ', 'TT = ', 'ConvT = ', 'maxT = ', 'ESP = ', 'MMP = ']
        indices = [self.k_idx, self.totals_totals, self.convT + 'F', self.maxT + 'F', self.esp, self.mmp]
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(x1*3.5, y1, x1*4, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            y1 += (self.label_height-2)

        ## middle-right column
        y1 = self.bry / 17 * 6
        texts = ['WNDG = ', 'TEI = ', '', '', '', 'SigSvr = ']
        indices = [self.wndg, self.tei, '', '', '', self.sigsevere + ' m3/s3']
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(x1*6, y1, x1*4, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            y1 += (self.label_height-2)
        qp.drawLine(0, y1+2, self.brx, y1+2)
        qp.drawLine(x1*7-5, y1+2, x1*7-5, self.bry )

    
    def drawConvectiveIndices(self, qp):
        '''
        This handles the drawing of the parcel indices.
        --------
        qp: QtGui.QPainter object
        '''
        ## initialize a white pen with thickness 2 and a solid line
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x pixel coordinate relative to the frame
        ## width.
        x1 = self.brx / 8
        y1 = self.bry / 17 + self.tpad
        ## get the indices rounded to the nearest int, conver to strings
        ## Start with the surface based parcel.
        sfc_bplus = tab.utils.INT2STR( self.sfcparcel.bplus )
        sfc_bminus = tab.utils.INT2STR( self.sfcparcel.bminus )
        sfc_lclhght = tab.utils.INT2STR( self.sfcparcel.lclhght )
        sfc_limax = tab.utils.INT2STR( self.sfcparcel.li5 )
        sfc_lfchght = tab.utils.INT2STR( self.sfcparcel.lfchght )
        sfc_elhght = tab.utils.INT2STR( self.sfcparcel.elhght )
        ## get the forecast surface parvel
        fcst_bplus = tab.utils.INT2STR( self.fcstpcl.bplus )
        fcst_bminus = tab.utils.INT2STR( self.fcstpcl.bminus )
        fcst_lclhght = tab.utils.INT2STR( self.fcstpcl.lclhght )
        fcst_limax = tab.utils.INT2STR( self.fcstpcl.li5 )
        fcst_lfchght = tab.utils.INT2STR( self.fcstpcl.lfchght )
        fcst_elhght = tab.utils.INT2STR( self.fcstpcl.elhght )
        ## Now get the mixed layer parcel indices
        ml_bplus = tab.utils.INT2STR( self.mlparcel.bplus )
        ml_bminus = tab.utils.INT2STR( self.mlparcel.bminus )
        ml_lclhght = tab.utils.INT2STR( self.mlparcel.lclhght )
        ml_limax = tab.utils.INT2STR( self.mlparcel.li5 )
        ## check and see if the lfc is there
        ml_lfchght = tab.utils.INT2STR( self.mlparcel.lfchght )
        ml_elhght = tab.utils.INT2STR( self.mlparcel.elhght )
        ## get the most unstable parcel indices
        mu_bplus = tab.utils.INT2STR( self.muparcel.bplus )
        mu_bminus = tab.utils.INT2STR( self.muparcel.bminus )
        mu_lclhght = tab.utils.INT2STR( self.muparcel.lclhght )
        mu_limax = tab.utils.INT2STR( self.muparcel.li5 )
        ## make sure the lfc is there
        mu_lfchght = tab.utils.INT2STR( self.muparcel.lfchght )
        mu_elhght = tab.utils.INT2STR( self.muparcel.elhght )

        ## Now that we have all the data, time to plot the text in their
        ## respective columns.
        
        ## PCL type
        texts = ['SFC', 'FCST', 'ML', 'MU']
        for text in texts:
            rect = QtCore.QRect(0, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height - 2)
        ## CAPE
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_bplus, fcst_bplus, ml_bplus, mu_bplus]
        for text in texts:
            rect = QtCore.QRect(x1*1, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        ## CINH
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_bminus, fcst_bminus, ml_bminus, mu_bminus]
        for text in texts:
            rect = QtCore.QRect(x1*2, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        ## LCL
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_lclhght, fcst_lclhght, ml_lclhght, mu_lclhght]
        for text in texts:
            rect = QtCore.QRect(x1*3, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        ## LI
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_limax, fcst_limax, ml_limax, mu_limax]
        for text in texts:
            rect = QtCore.QRect(x1*4, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        ## LFC
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_lfchght, fcst_lfchght, ml_lfchght, mu_lfchght]
        for text in texts:
            rect = QtCore.QRect(x1*5, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        ## EL
        y1 = self.bry / 17 + self.tpad
        texts = [sfc_elhght, fcst_elhght, ml_elhght, mu_elhght]
        for text in texts:
            rect = QtCore.QRect(x1*6, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            y1 += (self.label_height-2)
        qp.drawLine(0, y1+2, self.brx, y1+2)



