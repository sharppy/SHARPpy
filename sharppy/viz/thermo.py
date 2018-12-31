import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtCore import *
from qtpy.QtGui import *
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import datetime
import platform

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundText', 'plotText']

class backgroundText(QtWidgets.QFrame):
    '''
    Handles drawing the background frame onto a QPixmap.
    Inherits a QtWidgets.QFrame Object.
    '''
    def __init__(self, **kwargs):
        super(backgroundText, self).__init__()
        self.initUI()

    def initUI(self):
        '''
        Initializes frame variables such as padding,
        width, height, etc, as well as the QPixmap
        that contains the frame drawing.
        '''
        ## set the frame stylesheet
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        ## set the frame padding
        ## set the height/width variables
        self.lpad = 0; self.rpad = 0
        self.tpad = 5; self.bpad = 0
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## do a DPI check to make sure
        ## the text is sized properly!
        fsize = np.floor(.06 * self.hgt)
        self.tpad = np.floor(.03 * self.hgt)
        ## set the font, get the metrics and height of the font
        self.label_font = QtGui.QFont('Helvetica')
        self.label_font.setPixelSize(fsize)
        self.label_metrics = QtGui.QFontMetrics( self.label_font )
        self.label_height = self.label_metrics.xHeight() + self.tpad
        ## the self.ylast variable is used as a running sum for
        ## text placement.
        self.ylast = self.label_height
        ## initialize the QPixmap that will be drawn on.
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
        ## plot the background frame
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## set the horizontal grid to be the width of the frame
        ## divided into 8 spaces
        x1 = self.brx / 8
        y1 = 1
        ## draw the header and the indices using a loop.
        ## This loop is a 'horizontal' loop that will plot
        ## the text for a row, keeping the vertical placement constant.
        count = 0
        titles = ['PCL', 'CAPE', 'CINH', 'LCL', 'LI', 'LFC', 'EL']
        for title in titles:
            rect = QtCore.QRect(x1*count, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, title)
            count += 1
        vspace = self.label_height
        if platform.system() == "Windows":
            vspace += self.label_metrics.descent()
        qp.drawLine(0, vspace, self.brx, vspace)
        self.ylast = vspace
    
    def resizeEvent(self, e):
        '''
        Handles when the window gets resized.
        '''
        self.initUI()

    def plotBackground(self):
        '''
        Handles drawing the text background onto
        the QPixmap.
        '''
        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the frame
        self.draw_frame(qp)
        qp.end()


class plotText(backgroundText):
    updatepcl = Signal(tab.params.Parcel)

    '''
    Handles plotting the indices in the frame.
    Inherits a backgroundText Object that contains
    a QPixmap with the frame drawn on it. All drawing
    gets done on this QPixmap, and then the QPixmap
    gets rendered by the paintEvent function.
    '''
    def __init__(self, pcl_types):
        '''
        Initialize the data from a Profile object passed to 
        this class. It then takes the data it needs from the
        Profile object and converts them into strings that
        can be used to draw the text in the frame.
        
        Parameters
        ----------
        pcl_types :  
        '''
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.pw_units = 'in'
        self.temp_units = 'Fahrenheit'

        self.alert_colors = [
            QtGui.QColor('#775000'),
            QtGui.QColor('#996600'),
            QtGui.QColor('#ffffff'),
            QtGui.QColor('#ffff00'),
            QtGui.QColor('#ff0000'),
            QtGui.QColor('#e700df'),
        ]
        self.left_scp_color = QtGui.QColor('#00ffff')

        self.pcl_sel_color = QtGui.QColor('#00ffff')
        self.pcl_cin_hi_color = QtGui.QColor('#993333')
        self.pcl_cin_md_color = QtGui.QColor('#996600')
        self.pcl_cin_lo_color = QtGui.QColor('#00ff00')

        self.use_left = False

        ## get the parcels to be displayed in the GUI
        super(plotText, self).__init__()

        self.prof = None;
        self.pcl_types = pcl_types
        self.parcels = {}
        self.bounds = np.empty((4,2))
        self.setDefaultParcel()

        self.w = SelectParcels(self.pcl_types, self)

    def setDefaultParcel(self):
        idx = np.where(np.asarray(self.pcl_types) == "MU")[0]
        if len(idx) == 0:
            self.skewt_pcl = 0
        else:
            self.skewt_pcl = idx[0]

    def mouseDoubleClickEvent(self, e):
        self.w.show()

    def setParcels(self, prof):
        self.parcels["SFC"] = prof.sfcpcl # Set the surface parcel
        self.parcels["ML"] = prof.mlpcl
        self.parcels["FCST"] = prof.fcstpcl
        self.parcels["MU"] = prof.mupcl
        self.parcels["EFF"] = prof.effpcl
        self.parcels["USER"] = prof.usrpcl

    def setProf(self, prof):
        self.ylast = self.label_height
        self.setParcels(prof)
        self.prof = prof;

        ## either get or calculate the indices, round to the nearest int, and
        ## convert them to strings.
        ## K Index
        self.k_idx = tab.utils.INT2STR( prof.k_idx )
        ## precipitable water
        self.pwat = prof.pwat
        ## 0-3km agl lapse rate
        self.lapserate_3km = tab.utils.FLOAT2STR( prof.lapserate_3km, 1 )
        ## 3-6km agl lapse rate
        self.lapserate_3_6km = tab.utils.FLOAT2STR( prof.lapserate_3_6km, 1 )
        ## 850-500mb lapse rate
        self.lapserate_850_500 = tab.utils.FLOAT2STR( prof.lapserate_850_500, 1 )
        ## 700-500mb lapse rate
        self.lapserate_700_500 = tab.utils.FLOAT2STR( prof.lapserate_700_500, 1 )
        ## convective temperature
        self.convT = prof.convT
        ## sounding forecast surface temperature
        self.maxT = prof.maxT
        #fzl = str(int(self.sfcparcel.hght0c))
        ## 100mb mean mixing ratio
        self.mean_mixr = tab.utils.FLOAT2STR( prof.mean_mixr, 1 )
        ## 150mb mean rh
        self.low_rh = tab.utils.INT2STR( prof.low_rh )
        self.mid_rh = tab.utils.INT2STR( prof.mid_rh )
        ## calculate the totals totals index
        self.totals_totals = tab.utils.INT2STR( prof.totals_totals )
        self.dcape = tab.utils.INT2STR( prof.dcape )
        self.drush = prof.drush
        self.sigsevere = tab.utils.INT2STR( prof.sig_severe )
        self.mmp = tab.utils.FLOAT2STR( prof.mmp, 2 )
        self.esp = tab.utils.FLOAT2STR( prof.esp, 1 )
        self.wndg = tab.utils.FLOAT2STR( prof.wndg, 1 )
        self.tei = tab.utils.INT2STR( prof.tei )

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.pw_units = prefs['pw_units']
        self.temp_units = prefs['temp_units']
 
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        self.pwat_colors = [
            QtGui.QColor(prefs['pwat_m3_color']),
            QtGui.QColor(prefs['pwat_m2_color']),
            QtGui.QColor(prefs['pwat_m1_color']),
            self.fg_color,
            QtGui.QColor(prefs['pwat_p1_color']),
            QtGui.QColor(prefs['pwat_p2_color']),
            QtGui.QColor(prefs['pwat_p3_color']),
        ]

        self.alert_colors = [
            QtGui.QColor(prefs['alert_l1_color']),
            QtGui.QColor(prefs['alert_l2_color']),
            QtGui.QColor(prefs['alert_l3_color']),
            QtGui.QColor(prefs['alert_l4_color']),
            QtGui.QColor(prefs['alert_l5_color']),
            QtGui.QColor(prefs['alert_l6_color']),
        ]
        self.left_scp_color = QtGui.QColor(prefs['alert_lscp_color'])

        self.pcl_sel_color = QtGui.QColor(prefs['pcl_sel_color'])
        self.pcl_cin_hi_color = QtGui.QColor(prefs['pcl_cin_hi_color'])
        self.pcl_cin_md_color = QtGui.QColor(prefs['pcl_cin_md_color'])
        self.pcl_cin_lo_color = QtGui.QColor(prefs['pcl_cin_lo_color'])

        if update_gui:
            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'
        
        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        
        Parametes
        ---------
        e: an Event Object
        '''
        super(plotText, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles when the window gets painted.
        This renders the QPixmap that the backgroundText
        Object contians. For the actual drawing of the data,
        see the plotData function.
        
        Parametes
        ---------
        e: an Event Object
        
        '''
        super(plotText, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(1, 1, self.plotBitMap)
        qp.end()

    def plotData(self):
        '''
        Handles the drawing of the text onto the QPixmap.
        This is where the actual data gets plotted/drawn.
        '''
        if self.prof is None:
            return

        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the indices
        self.drawConvectiveIndices(qp)
        self.drawIndices(qp)
        self.drawSevere(qp)
        qp.end()

    def clearData(self):
        '''
        Handles the clearing of the pixmap
        in the frame.
        '''
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)
    
    def drawSevere(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen to draw with.
        pen = QtGui.QPen(QtCore.Qt.yellow, 1, QtCore.Qt.SolidLine)
        self.label_font.setBold(True)
        qp.setFont(self.label_font)
       
        color_list = self.alert_colors
        ## needs to be coded.
        x1 = self.brx / 10
        y1 = self.ylast + self.tpad

        ship = self.prof.ship
        ship_str = tab.utils.FLOAT2STR( ship, 1 )

        if self.use_left:
            stp_fixed = self.prof.left_stp_fixed
            stp_cin = self.prof.left_stp_cin
            scp = self.prof.left_scp
        else:
            stp_fixed = self.prof.right_stp_fixed
            stp_cin = self.prof.right_stp_cin
            scp = self.prof.right_scp

        stp_fixed_str = tab.utils.FLOAT2STR( stp_fixed, 1 )
        stp_cin_str = tab.utils.FLOAT2STR( stp_cin, 1 )
        scp_str = tab.utils.FLOAT2STR( scp, 1 )

        if self.prof.latitude < 0:
            stp_fixed = -stp_fixed
            stp_cin = -stp_cin
            scp = -scp

        # Coloring thresholds provided by Rich Thompson (SPC)
        labels = ['Supercell = ', 'STP (cin) = ', 'STP (fix) = ', 'SHIP = ']
        indices = [scp, stp_cin, stp_fixed, ship]
        index_strs = [scp_str, stp_cin_str, stp_fixed_str, ship_str]
        for label, index_str, index in zip(labels,index_strs,indices):
            rect = QtCore.QRect(x1*7, y1, x1*8, self.label_height)
            if index == '--':
                pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
            elif label == labels[0]: # STP uses a different color scale
                if index >= 19.95:
                    pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
                elif index >= 11.95:
                    pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
                elif index >= 1.95:
                    pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
                elif index >= .45:
                    pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
                elif index >= -.45:
                    pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
                elif index < -.45:
                    pen = QtGui.QPen(self.left_scp_color, 1, QtCore.Qt.SolidLine)
            elif label == labels[1]: # STP effective
                if index >= 8:
                    pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
                elif index >= 4:
                    pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
                elif index >= 2:
                    pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
                elif index >= 1:
                    pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
                elif index >= .5:
                    pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
                elif index < .5:
                    pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
            elif label == labels[2]: # STP fixed
                if index >= 7:
                    pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
                elif index >= 5:
                    pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
                elif index >= 2:
                    pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
                elif index >= 1:
                    pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
                elif index >= .5:
                    pen = QtGui.QPen(color_list[1], 1, QtCore.Qt.SolidLine)
                else:
                    pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
            elif label == labels[3]: # SHIP
                if index >= 5:
                    pen = QtGui.QPen(color_list[5], 1, QtCore.Qt.SolidLine)
                elif index >= 2:
                    pen = QtGui.QPen(color_list[4], 1, QtCore.Qt.SolidLine)
                elif index >= 1:
                    pen = QtGui.QPen(color_list[3], 1, QtCore.Qt.SolidLine)
                elif index >= .5:
                    pen = QtGui.QPen(color_list[2], 1, QtCore.Qt.SolidLine)
                else:
                    pen = QtGui.QPen(color_list[0], 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, label + index_str)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        self.label_font.setBold(False)

    def drawIndices(self, qp):
        '''
        Draws the non-parcel indices.
        
        Parameters
        ----------
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
        std_dev = [ u'(<3\u03C3)', u'(2-3\u03C3)', u'(1-2\u03C3)', '', u'(1-2\u03C3)', u'(2-3\u03C3)', u'(>3\u03C3)' ]
        color = self.pwat_colors[self.prof.pwv_flag + 3] 
        dist_string = std_dev[self.prof.pwv_flag + 3]
        if self.pw_units == 'cm':
            pw_display = tab.utils.IN2CM(self.pwat)
            pw_display = tab.utils.FLOAT2STR( pw_display, 1 )
        else:
            pw_display = self.pwat
            pw_display = tab.utils.FLOAT2STR( pw_display, 2 )

        ## draw the first column of text using a loop, keeping the horizontal
        ## placement constant.
        y1 = self.ylast + self.tpad

        if self.temp_units == 'Fahrenheit':
            t_units_disp = 'F'
            drush_disp = tab.utils.INT2STR( self.drush )
            convT_disp = tab.utils.INT2STR( self.convT )
            maxT_disp = tab.utils.INT2STR( self.maxT )
        elif self.temp_units == 'Celsius':
            t_units_disp = 'C'
            drush_disp = tab.utils.INT2STR( tab.thermo.ftoc(self.drush) )
            convT_disp = tab.utils.INT2STR( tab.thermo.ftoc(self.convT) )
            maxT_disp = tab.utils.INT2STR( tab.thermo.ftoc(self.maxT) )

        colors = [color, self.fg_color, self.fg_color, self.fg_color, self.fg_color, self.fg_color]
        texts = ['PW = ', 'MeanW = ', 'LowRH = ', 'MidRH = ', 'DCAPE = ', 'DownT = ']
        indices = [pw_display + self.pw_units + ' ' + dist_string, self.mean_mixr + 'g/kg', self.low_rh + '%', self.mid_rh + '%', self.dcape, drush_disp + t_units_disp]
        for text, index, c in zip(texts, indices, colors):
            rect = QtCore.QRect(rpad, y1, x1*4, self.label_height)
            pen = QtGui.QPen(c, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        ## middle-left column
        y1 = self.ylast + self.tpad
        texts = ['K = ', 'TT = ', 'ConvT = ', 'maxT = ', 'ESP = ', 'MMP = ']
        indices = [self.k_idx, self.totals_totals, convT_disp + t_units_disp, maxT_disp + t_units_disp, self.esp, self.mmp]
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(x1*3.5, y1, x1*4, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        ## middle-right column
        y1 = self.ylast + self.tpad
        texts = ['WNDG = ', 'TEI = ', '3CAPE = ', 'MBURST = ', '', 'SigSvr = ']
        indices = [self.wndg, self.tei, tab.utils.INT2STR(self.prof.mlpcl.b3km), tab.utils.INT2STR(self.prof.mburst), '', self.sigsevere + ' m3/s3']
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(x1*6, y1, x1*4, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
            self.ylast = y1
        qp.drawLine(0, y1+2, self.brx, y1+2)
        qp.drawLine(x1*7-5, y1+2, x1*7-5, self.bry )
        
        ## lapserate window
        y1 = self.ylast + self.tpad
        texts = ['Sfc-3km AGL LR = ', '3-6km AGL LR = ', '850-500mb LR = ', '700-500mb LR = ']
        indices = [self.lapserate_3km + ' C/km', self.lapserate_3_6km + ' C/km', self.lapserate_850_500 + ' C/km', self.lapserate_700_500 + ' C/km']
        for text, index in zip(texts, indices):
            rect = QtCore.QRect(rpad, y1, x1*8, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, text + index)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace


    def drawConvectiveIndices(self, qp):
        '''
        This handles the drawing of the parcel indices.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## initialize a white pen with thickness 2 and a solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## make the initial x pixel coordinate relative to the frame
        ## width.
        x1 = self.brx / 8
        y1 = self.ylast + self.tpad
        ## get the indices rounded to the nearest int, conver to strings
        ## Start with the surface based parcel.
        capes = np.empty(4, dtype="S10") # Only allow 4 parcels to be displayed
        cins = np.empty(4, dtype="S10")
        lcls = np.empty(4, dtype="S10")
        lis = np.empty(4, dtype="S10")
        lfcs = np.empty(4, dtype="S10")
        els = np.empty(4, dtype="S10")
        texts = self.pcl_types
        for i, key in enumerate(texts):
            parcel = self.parcels[key]
            capes[i] = tab.utils.INT2STR(parcel.bplus) # Append the CAPE value
            cins[i] = tab.utils.INT2STR(parcel.bminus)
            lcls[i] = tab.utils.INT2STR(parcel.lclhght)
            lis[i] = tab.utils.INT2STR(parcel.li5)
            lfcs[i] = tab.utils.INT2STR(parcel.lfchght)
            els[i] = tab.utils.INT2STR(parcel.elhght)
        ## Now that we have all the data, time to plot the text in their
        ## respective columns.
        
        ## PCL type
        pcl_index = 0
        for i, text in enumerate(texts):
            self.bounds[i,0] = y1
            if text == self.pcl_types[self.skewt_pcl]:
                pen = QtGui.QPen(self.pcl_sel_color, 1, QtCore.Qt.SolidLine)
                qp.setPen(pen)
                pcl_index = i
            else:
                pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
                qp.setPen(pen)
            rect = QtCore.QRect(0, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, text)
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
            self.bounds[i,1] = y1
        ## CAPE
        y1 = self.ylast + self.tpad
        for i, text in enumerate(capes):
            try:
                if pcl_index == i and int(text) >= 4000:
                    color = self.alert_colors[5]
                elif pcl_index == i and int(text) >= 3000:
                    color = self.alert_colors[4]
                elif pcl_index == i and int(text) >= 2000:
                    color = self.alert_colors[3]
                else:
                    color=self.fg_color
            except:
                color=self.fg_color
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRect(x1*1, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        ## CINH
        y1 = self.ylast + self.tpad
        for i, text in enumerate(cins):
            try:
                if int(capes[i]) > 0 and pcl_index == i and int(text) >= -50:
                    color = self.pcl_cin_lo_color 
                elif int(capes[i]) > 0 and pcl_index == i and int(text) >= -100:
                    color = self.pcl_cin_md_color
                elif int(capes[i]) > 0 and pcl_index == i and int(text) < -100:
                    color = self.pcl_cin_hi_color
                else:
                    color = self.fg_color
            except:
                color = self.fg_color
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRect(x1*2, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        ## LCL
        y1 = self.ylast + self.tpad
        for i, text in enumerate(lcls):
            try:
                if int(text) < 1000 and pcl_index == i and texts[i] == "ML":
                    color = self.pcl_cin_lo_color
                elif int(text) < 1500 and pcl_index == i and texts[i] == "ML":
                    color = self.pcl_cin_md_color
                elif int(text) < 2000 and pcl_index == i and texts[i] == "ML":
                    color = self.pcl_cin_hi_color
                else:
                    color = self.fg_color
            except:
                color=self.fg_color
            pen = QtGui.QPen(color, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            rect = QtCore.QRect(x1*3, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace

        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        ## LI
        y1 = self.ylast + self.tpad
        for text in lis:
            rect = QtCore.QRect(x1*4, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        ## LFC
        y1 = self.ylast + self.tpad
        for text in lfcs:
            rect = QtCore.QRect(x1*5, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
        ## EL
        y1 = self.ylast + self.tpad
        for text in els:
            rect = QtCore.QRect(x1*6, y1, x1*2, self.label_height)
            qp.drawText(rect, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter, bytes(text).decode('utf-8'))
            vspace = self.label_height
            if platform.system() == "Windows":
                vspace += self.label_metrics.descent()
            y1 += vspace
            self.ylast = y1
        qp.drawLine(0, y1+2, self.brx, y1+2)
        color=QtGui.QColor('#996633')
        pen = QtGui.QPen(color, .5, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(2, self.bounds[self.skewt_pcl,0]-1, x1*6 + x1*2 - 1, self.bounds[self.skewt_pcl,0]-1)
        qp.drawLine(2, self.bounds[self.skewt_pcl,0]-1, 2, self.bounds[self.skewt_pcl,1])
        qp.drawLine(2, self.bounds[self.skewt_pcl,1], x1*6 + x1*2 - 1, self.bounds[self.skewt_pcl,1])
        qp.drawLine(x1*6 + x1*2 -1 , self.bounds[self.skewt_pcl,0]-1, x1*6 + x1*2 -1, self.bounds[self.skewt_pcl,1])


    def mousePressEvent(self, e):
        pos = e.pos()
        for i, bound in enumerate(self.bounds):
            if bound[0] < pos.y() and bound[1] > pos.y():
                self.skewt_pcl = i
                self.ylast = self.label_height
                pcl_to_pass = self.parcels[self.pcl_types[self.skewt_pcl]]
                self.updatepcl.emit(pcl_to_pass)
                self.clearData()
                self.plotBackground()
                self.plotData()
                self.update()
                self.parentWidget().setFocus()
                break

class SelectParcels(QtWidgets.QWidget):
    def __init__(self, parcel_types, parent):
        QtWidgets.QWidget.__init__(self)
        self.thermo = parent
        self.parcel_types = parcel_types
        self.max_pcls = 4
        self.pcl_count = 0
        self.initUI()

    def initUI(self):

        self.sb = QtWidgets.QCheckBox('Surface-Based Parcel', self)
        self.sb.move(20, 20)
        if "SFC" in self.parcel_types:
            self.sb.toggle()
            self.pcl_count += 1
        self.sb.stateChanged.connect(self.changeParcel)

        self.ml = QtWidgets.QCheckBox('100 mb Mixed Layer Parcel', self)
        self.ml.move(20, 40)
        if "ML" in self.parcel_types:
            self.ml.toggle()
            self.pcl_count += 1
        self.ml.stateChanged.connect(self.changeParcel)

        self.fcst = QtWidgets.QCheckBox('Forecast Surface Parcel', self)
        self.fcst.move(20, 60)
        if "FCST" in self.parcel_types:
            self.fcst.toggle()
            self.pcl_count += 1
        self.fcst.stateChanged.connect(self.changeParcel)

        self.mu = QtWidgets.QCheckBox('Most Unstable Parcel', self)
        self.mu.move(20, 80)
        if "MU" in self.parcel_types:
            self.mu.toggle()
            self.pcl_count += 1
        self.mu.stateChanged.connect(self.changeParcel)

        self.eff = QtWidgets.QCheckBox('Effective Inflow Layer Parcel', self)
        self.eff.move(20, 100)
        if "EFF" in self.parcel_types:
            self.eff.toggle()
            self.pcl_count += 1
        self.eff.stateChanged.connect(self.changeParcel)

        self.usr = QtWidgets.QCheckBox('User Defined Parcel', self)
        self.usr.move(20, 120)
        if "USER" in self.parcel_types:
            self.usr.toggle()
            self.pcl_count += 1
        self.usr.stateChanged.connect(self.changeParcel)


        self.setGeometry(300, 300, 250, 180)
        self.setWindowTitle('Show Parcels')
        self.ok = QtWidgets.QPushButton('Ok', self)
        self.ok.move(20,150)
        self.ok.clicked.connect(self.okPushed)

        #cb.stateChanged.connect(self.changeTitle)
    #cb.stateChanged.connect(

    def changeParcel(self, state):
        if state == QtCore.Qt.Checked:
            self.pcl_count += 1
        else:
            self.pcl_count -= 1

    def okPushed(self):
        if self.pcl_count > self.max_pcls:
            msgBox = QMessageBox()
            msgBox.setText("You can only show 4 parcels at a time.\nUnselect some parcels.")
            msgBox.exec_()
        elif self.pcl_count != self.max_pcls:
            msgBox = QMessageBox()
            msgBox.setText("You need to select 4 parcels to show.  Select some more.")
            msgBox.exec_()
        else:
            self.parcel_types = []
            if self.sb.isChecked() is True:
                self.parcel_types.append('SFC')
            if self.ml.isChecked() is True:
                self.parcel_types.append('ML')
            if self.fcst.isChecked() is True:
                self.parcel_types.append('FCST')
            if self.mu.isChecked() is True:
                self.parcel_types.append('MU')
            if self.eff.isChecked() is True:
                self.parcel_types.append('EFF')
            if self.usr.isChecked() is True:
                self.parcel_types.append('USER')

            self.thermo.pcl_types = self.parcel_types
            self.thermo.skewt_pcl = 0
            self.thermo.ylast = self.thermo.label_height
            pcl_to_pass = self.thermo.parcels[self.thermo.pcl_types[self.thermo.skewt_pcl]]
            self.thermo.updatepcl.emit(pcl_to_pass)
            self.thermo.clearData()
            self.thermo.plotBackground()
            self.thermo.plotData()
            self.thermo.update()
            self.thermo.parentWidget().setFocus()
            self.hide()

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    #tester = plotText(['sfcpcl', 'mlpcl', 'mupcl'])
    tester = plotBackgroundText()
    #tester.setProf()
    tester.show()        
    app_frame.exec_()
