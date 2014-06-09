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
        self.label_font = QtGui.QFont('Helvetica')
        self.label_font.setPointSize(8)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.label_height = self.label_metrics.height()
        self.severe_font = QtGui.QFont('Helvetica')
        self.severe_font.setPointSize(10)
        self.severe_metrics = QtGui.QFontMetrics( self.severe_font )
        self.severe_height = self.severe_metrics.height()
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
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 8
        y1 = self.bry / 17
        ## draw the header for the indices
        rect0 = QtCore.QRect(x1*0, 1, x1*2, self.label_height)
        rect1 = QtCore.QRect(x1*1, 1, x1*2, self.label_height)
        rect2 = QtCore.QRect(x1*2, 1, x1*2, self.label_height)
        rect3 = QtCore.QRect(x1*3, 1, x1*2, self.label_height)
        rect4 = QtCore.QRect(x1*4, 1, x1*2, self.label_height)
        rect5 = QtCore.QRect(x1*5, 1, x1*2, self.label_height)
        rect6 = QtCore.QRect(x1*6, 1, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'PCL')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'CAPE')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'CINH')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'LCL')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'LI')
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'LFC')
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'EL')
        ## draw lines seperating the indices
        qp.drawLine( 0, y1, self.brx, y1 )
        qp.drawLine( 0, y1*5+self.tpad, self.brx, y1*5+self.tpad )
        qp.drawLine( 0, y1*13-self.tpad, x1*4.5, y1*13-self.tpad )
        qp.drawLine( x1*4.5, self.bry, x1*4.5, y1*10  )
        qp.drawLine( x1*4.5, y1*10, self.brx, y1*10  )
    
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
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
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
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
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
        qp.setFont(self.severe_font)
        color_list = [QtGui.QColor('#A05030'), QtGui.QColor('#D0A020'),
             QtCore.Qt.yellow, QtGui.QColor("#FF4000"), QtCore.Qt.red, QtCore.Qt.magenta]
        ## needs to be coded.
        x1 = self.brx / 10
        y1 = self.bry / 17
        ship = tab.utils.FLOAT2STR( self.prof.ship, 1 )
        stp_fixed = tab.utils.FLOAT2STR( self.prof.stp_fixed, 1 )
        stp_cin = tab.utils.FLOAT2STR( self.prof.stp_cin, 1 )
        right_scp = tab.utils.FLOAT2STR( self.prof.right_scp, 1 )
        left_scp = tab.utils.FLOAT2STR( self.prof.left_scp, 1 )
        rect0 = QtCore.QRect(x1*6, y1*10.00+(self.tpad), x1*8, self.severe_height)
        rect1 = QtCore.QRect(x1*6, y1*11.25+(self.tpad), x1*8, self.severe_height)
        rect2 = QtCore.QRect(x1*6, y1*12.50+(self.tpad), x1*8, self.severe_height)
        rect3 = QtCore.QRect(x1*6, y1*13.75+(self.tpad), x1*8, self.severe_height)
        rect4 = QtCore.QRect(x1*6, y1*15.00+(self.tpad), x1*8, self.severe_height)
        
        if float(right_scp) < 1:
            pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
        elif float(right_scp) < 2:
            pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
        elif float(right_scp) < 5:
            pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
        elif float(right_scp) < 10:
            pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
        elif float(right_scp) < 20:
            pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Supercell = ' + right_scp)
        if float(left_scp) < 0.5:
            pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
        elif float(left_scp) < 1:
            pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
        elif float(left_scp) < 15:
            pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
        elif float(left_scp) < 20:
            pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
        elif float(left_scp) < 30:
            pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Left Supercell = ' + left_scp)
        
        if float(stp_cin) < 0.5:
            pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
        elif float(stp_cin) < 2:
            pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
        elif float(stp_cin) < 3.5:
            pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
        elif float(stp_cin) < 5:
            pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
        elif float(stp_cin) < 7:
            pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'STP (cin) = ' + stp_cin)
        
        if float(stp_fixed) < 1:
            pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
        elif float(stp_fixed) < 2:
            pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
        elif float(stp_fixed) < 4:
            pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
        elif float(stp_fixed) < 6:
            pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
        elif float(stp_fixed) < 10:
            pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'STP (fix) = ' + stp_fixed)
       
        # These thresholds are based off of the 10, 25, 50, 75, 90th percentiles of the SARS SHIP column
        if float(ship) < 0.3:
            pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
        elif float(ship) < 6:
            pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
        elif float(ship) < 1.1:
            pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
        elif float(ship) < 1.9:
            pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
        elif float(ship) < 2.7:
            pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
        else:
            pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Sig Hail = ' + ship)
    
    def drawIndices(self, qp):
        '''
        Draw the non-parcel indices.
        --------
        qp: QtGui.QPainter object
        '''
        qp.setFont(self.label_font)
        ## make the initial x point relatice to the width of the frame.
        x1 = self.brx / 10
        y1 = self.bry / 17
        rpad = 5
        tpad = 5

        ## Now we have all the data we could ever want. Time to start drawing
        ## them on the frame.
        ## This starts with the left column.
        
        rect0 = QtCore.QRect(rpad, y1*5+self.tpad*2, x1*4, self.label_height)
        rect1 = QtCore.QRect(rpad, y1*6+self.tpad*2, x1*4, self.label_height)
        rect2 = QtCore.QRect(rpad, y1*7+self.tpad*2, x1*4, self.label_height)
        rect3 = QtCore.QRect(rpad, y1*8+self.tpad*2, x1*4, self.label_height)
        rect4 = QtCore.QRect(rpad, y1*9+self.tpad*2, x1*8, self.label_height+self.tpad)
        rect5 = QtCore.QRect(rpad, y1*10+self.tpad*2, x1*8, self.label_height+self.tpad)
        rect6 = QtCore.QRect(rpad, y1*13, x1*8, self.label_height)
        rect7 = QtCore.QRect(rpad, y1*14, x1*8, self.label_height)
        rect8 = QtCore.QRect(rpad, y1*15, x1*8, self.label_height)
        rect9 = QtCore.QRect(rpad, y1*16, x1*8, self.label_height+self.tpad)
        if self.prof.pwv_flag == -3:
            color = QtGui.QColor('#DA9167')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        elif self.prof.pwv_flag == -2:
            color = QtGui.QColor('#FFE1B7')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        elif self.prof.pwv_flag == -1:
            color = QtGui.QColor('#FFFFD5')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        elif self.prof.pwv_flag == 0:
            color = QtGui.QColor('#FFFFFF')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        elif self.prof.pwv_flag == 1:
            color = QtGui.QColor('#D6FFD6')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        elif self.prof.pwv_flag == 2:
            color = QtGui.QColor('#A4CDA4')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        else:
            color = QtGui.QColor('#008000')
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'PW = ' + self.pwat + 'in')
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'MeanW = ' + self.mean_mixr + 'g/kg')
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'LowRH = ' + self.low_rh + '%')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'MidRH = ' + self.mid_rh + '%')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'DCAPE = ' + self.dcape)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'DownT = ' + self.drush + 'F')
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'Sfc-3km AGL LR = ' + self.lapserate_3km + ' C/km')
        qp.drawText(rect7, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, '3-6km AGL LR = ' + self.lapserate_3_6km + ' C/km')
        qp.drawText(rect8, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, '850-500mb LR = ' + self.lapserate_850_500 + ' C/km')
        qp.drawText(rect9, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, '700-500mb LR = ' + self.lapserate_700_500 + ' C/km')
        ## middle-left column
        rect0 = QtCore.QRect(x1*3.5, y1*5+self.tpad*2, x1*4, self.label_height)
        rect1 = QtCore.QRect(x1*3.5, y1*6+self.tpad*2, x1*4, self.label_height)
        rect2 = QtCore.QRect(x1*3.5, y1*7+self.tpad*2, x1*4, self.label_height)
        rect3 = QtCore.QRect(x1*3.5, y1*8+self.tpad*2, x1*4, self.label_height)
        rect4 = QtCore.QRect(x1*3.5, y1*9+self.tpad*2, x1*4, self.label_height)
        rect5 = QtCore.QRect(x1*3.5, y1*10+self.tpad*2, x1*4, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'K = ' + self.k_idx)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'TT = ' + self.totals_totals)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'ConvT = ' + self.convT + 'F')
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'maxT = ' + self.maxT + 'F')
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'ESP = ' + self.esp)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'MMP = ' + self.mmp)
        ## middle-right column
        rect0 = QtCore.QRect(x1*6, y1*5+self.tpad*2, x1*4, self.label_height)
        rect1 = QtCore.QRect(x1*6, y1*6+self.tpad*2, x1*4, self.label_height)
        rect2 = QtCore.QRect(x1*6, y1*8+self.tpad*2, x1*4, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'WNDG = ' + self.wndg)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'TEI = ' + self.tei)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, 'SigSvr = ' + self.sigsevere + ' m3/s3')

    
    def drawConvectiveIndices(self, qp):
        '''
        This handles the drawing of the parcel indices.
        --------
        qp: QtGui.QPainter object
        '''
        ## initialize a white pen with thickness 2 and a solid line
        pen = QtGui.QPen(QtCore.Qt.white, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x pixel coordinate relative to the frame
        ## width.
        x1 = self.brx / 8
        y1 = self.bry / 17
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

        ## Start by plotting the surface parcel
        rect0 = QtCore.QRect(x1*0, y1+self.tpad, x1*2, self.label_height)
        rect1 = QtCore.QRect(x1*1, y1+self.tpad, x1*2, self.label_height)
        rect2 = QtCore.QRect(x1*2, y1+self.tpad, x1*2, self.label_height)
        rect3 = QtCore.QRect(x1*3, y1+self.tpad, x1*2, self.label_height)
        rect4 = QtCore.QRect(x1*4, y1+self.tpad, x1*2, self.label_height)
        rect5 = QtCore.QRect(x1*5, y1+self.tpad, x1*2, self.label_height)
        rect6 = QtCore.QRect(x1*6, y1+self.tpad, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'SFC')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_bplus)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_bminus)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_lclhght)
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_limax)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_lfchght)
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, sfc_elhght)
        ## plot forcast surface parcel
        rect0 = QtCore.QRect(x1*0, y1*2+self.tpad, x1*2, self.label_height)
        rect1 = QtCore.QRect(x1*1, y1*2+self.tpad, x1*2, self.label_height)
        rect2 = QtCore.QRect(x1*2, y1*2+self.tpad, x1*2, self.label_height)
        rect3 = QtCore.QRect(x1*3, y1*2+self.tpad, x1*2, self.label_height)
        rect4 = QtCore.QRect(x1*4, y1*2+self.tpad, x1*2, self.label_height)
        rect5 = QtCore.QRect(x1*5, y1*2+self.tpad, x1*2, self.label_height)
        rect6 = QtCore.QRect(x1*6, y1*2+self.tpad, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'FCST')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_bplus)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_bminus)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_lclhght)
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_limax)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_lfchght)
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, fcst_elhght)
        ## plot ML Parcel
        rect0 = QtCore.QRect(x1*0, y1*3+self.tpad, x1*2, self.label_height)
        rect1 = QtCore.QRect(x1*1, y1*3+self.tpad, x1*2, self.label_height)
        rect2 = QtCore.QRect(x1*2, y1*3+self.tpad, x1*2, self.label_height)
        rect3 = QtCore.QRect(x1*3, y1*3+self.tpad, x1*2, self.label_height)
        rect4 = QtCore.QRect(x1*4, y1*3+self.tpad, x1*2, self.label_height)
        rect5 = QtCore.QRect(x1*5, y1*3+self.tpad, x1*2, self.label_height)
        rect6 = QtCore.QRect(x1*6, y1*3+self.tpad, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'ML')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_bplus)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_bminus)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_lclhght)
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_limax)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_lfchght)
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, ml_elhght)
        ## plot MU parcel
        rect0 = QtCore.QRect(x1*0, y1*4+self.tpad, x1*2, self.label_height)
        rect1 = QtCore.QRect(x1*1, y1*4+self.tpad, x1*2, self.label_height)
        rect2 = QtCore.QRect(x1*2, y1*4+self.tpad, x1*2, self.label_height)
        rect3 = QtCore.QRect(x1*3, y1*4+self.tpad, x1*2, self.label_height)
        rect4 = QtCore.QRect(x1*4, y1*4+self.tpad, x1*2, self.label_height)
        rect5 = QtCore.QRect(x1*5, y1*4+self.tpad, x1*2, self.label_height)
        rect6 = QtCore.QRect(x1*6, y1*4+self.tpad, x1*2, self.label_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, 'MU')
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_bplus)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_bminus)
        qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_lclhght)
        qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_limax)
        qp.drawText(rect5, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_lfchght)
        qp.drawText(rect6, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, mu_elhght)
