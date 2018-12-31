import numpy as np
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
import sharppy.sharptab.utils as utils
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundWinds', 'plotWinds']

class backgroundWinds(QtWidgets.QFrame):
    '''
    Handles the plotting of the frame boarders and ticks.
    Draws the frame onto a QPixmap.
    '''
    def __init__(self):
        super(backgroundWinds, self).__init__()
        self.initUI()


    def initUI(self):
        '''
        Initializes the frame attributes and QPixmap.
        '''
        ## initialize plot window variables,
        ## such as width, height, padding, and
        ## min/max axes variables
        self.lpad = 0; self.rpad = 0
        self.tpad = 0; self.bpad = 20
        self.wid = self.size().width() - self.rpad
        self.hgt = self.size().height() - self.bpad
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## minimum/maximum height (km) and wind values.
        ## used in converting to pixel units
        self.hmax = 16.; self.hmin = 0.
        self.smax = 80.; self.smin = 0.
        self.font_ratio = 0.0512
        self.label_font = QtGui.QFont('Helvetica', round(self.size().height() * self.font_ratio))
        ## initialize the QPixmap
        self.plotBitMap = QtGui.QPixmap(self.width(), self.height())
        self.plotBitMap.fill(self.bg_color)
        self.plotBackground()

    def resizeEvent(self, e):
        '''
        Handles the event the window is resized.
        '''
        self.initUI()
    
    def plotBackground(self):
        '''
        This paints the frame background onto the QPixmap.
        '''
        ## initialize a QPainter object for drawing
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the background frame
        self.draw_frame(qp)
        ## draw the ticks for the plot.
        ## height is in km.
        for h in [2,4,6,8,10,12,14]:
            self.draw_height(h, qp)
        for s in range(0,100,10):
            self.draw_speed(s, qp)
        qp.end()

    def draw_frame(self, qp):
        '''
        Draws the background frame.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## initialize a new pen with white color, thickness of 2, solid line.
        pen = QtGui.QPen(self.fg_color, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        qp.drawText(15, 5, 45, 35,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter,
            'SR Wind\nv.\nHeight')
        ## draw the frame borders
        qp.drawLine(self.tlx, self.tly, self.brx, self.tly)
        qp.drawLine(self.brx, self.tly, self.brx, self.bry)
        qp.drawLine(self.brx, self.bry, self.tlx, self.bry)
        qp.drawLine(self.tlx, self.bry, self.tlx, self.tly)
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        zero = self.speed_to_pix(15.)
        qp.drawLine( zero, self.bry, zero, self.tly)
        lower = self.hgt_to_pix(8.)
        upper = self.hgt_to_pix(16.)
        classic1 = self.speed_to_pix(40.)
        classic2 = self.speed_to_pix(70.)
        pen = QtGui.QPen(self.clsc_color, 1, QtCore.Qt.DashLine)
        qp.setPen(pen)
        qp.drawLine( classic1, lower, classic1, upper )
        qp.drawLine( classic2, lower, classic2, upper )
        qp.drawText(classic1-5, 2, 50, 50,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter,
            'Classic\nSupercell')
        ## draw the plot description text

    def draw_height(self, h, qp):
        '''
        Draw background height ticks in km.
        
        Parameters
        ----------
        h: height in km
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with color white, thickness 1, solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert the height value to pixel coordinates
        y1 = self.hgt_to_pix(h)
        ## length of tick to be drawn
        offset = 5
        ## draw the tick and then label the tick with the value
        qp.drawLine(self.lpad, y1, self.lpad+offset, y1)
        qp.drawLine(self.brx+self.rpad-offset, y1,
            self.brx+self.rpad, y1)
        qp.drawText(0, y1-20, 20, 40,
            QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,
            utils.INT2STR(h))

    def draw_speed(self, s, qp):
        '''
        Draw background speed ticks.
        
        Parameters
        ----------
        s: windpeed
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with white color, thickness 1, solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.setFont(self.label_font)
        ## convert wind speed values to pixel values
        x1 = self.speed_to_pix(s)
        ## length of tick to be drawn
        offset = 5
        qp.drawLine(x1, 0, x1, 0+offset)
        qp.drawLine(x1, self.bry+self.tpad-offset,
            x1, self.bry+self.rpad)

    def hgt_to_pix(self, h):
        '''
        Function to convert a height value (km) to a Y pixel.
        
        Parameters
        ----------
        h: height in km
        
        '''
        scl1 = self.hmax - self.hmin
        scl2 = self.hmin + h
        return (self.bry - 2) - (scl2 / scl1) * (self.bry - self.tpad)

    def speed_to_pix(self, s):
        '''
        Function to convert a wind speed value to a X pixel.
        
        Parameters
        ----------
        s: speed in kts
        '''
        scl1 = self.smax - self.smin
        scl2 = self.smax - s
        return self.bry - (scl2 / scl1) * (self.bry - self.rpad)

class plotWinds(backgroundWinds):
    '''
    Draws the storm relative winds vs. height.
    Inherits from the backgroundWinds class that 
    contains the QPixmap with the background frame
    drawn on it.
    '''
    def __init__(self):
        '''
        Initializes the data from the Profile object
        used to draw the profile.
        
        Parameters
        ----------
        prof: a Profile object
        
        '''
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.clsc_color = QtGui.QColor('#b1019a')
        self.trace_color = QtGui.QColor('#ff0000')
        self.m0_2_color = QtGui.QColor('#8b0000')
        self.m4_6_color = QtGui.QColor('#6495ed')
        self.m9_11_color = QtGui.QColor('#9400d3')

        self.use_left = False

        super(plotWinds, self).__init__()
        ## make the data accessable to the functions
        self.prof = None

    def setProf(self, prof):
        self.prof = prof

        self.u = prof.u; self.v = prof.v
        ## calculate the storm relative wind from the bunkers motion function
        self.srwind = prof.srwind

        if self.use_left:
            self.srw_0_2km = utils.comp2vec(self.prof.left_srw_0_2km[0], self.prof.left_srw_0_2km[1])[1]
            self.srw_4_6km = utils.comp2vec(self.prof.left_srw_4_6km[0], self.prof.left_srw_4_6km[1])[1]
            self.srw_9_11km = utils.comp2vec(self.prof.left_srw_9_11km[0], self.prof.left_srw_9_11km[1])[1]
            ## get only the left mover u and v components
            self.sru = self.u - self.srwind[2]
            self.srv = self.v - self.srwind[3]
        else:
            self.srw_0_2km = utils.comp2vec(self.prof.right_srw_0_2km[0], self.prof.right_srw_0_2km[1])[1]
            self.srw_4_6km = utils.comp2vec(self.prof.right_srw_4_6km[0], self.prof.right_srw_4_6km[1])[1]
            self.srw_9_11km = utils.comp2vec(self.prof.right_srw_9_11km[0], self.prof.right_srw_9_11km[1])[1]
            ## get only the right mover u and v components
            self.sru = self.u - self.srwind[0]
            self.srv = self.v - self.srwind[1]

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])
        self.clsc_color = QtGui.QColor(prefs['srw_clsc_color'])
        self.trace_color = QtGui.QColor(prefs['srw_trace_color'])
        self.m0_2_color = QtGui.QColor(prefs['srw_0_2_color'])
        self.m4_6_color = QtGui.QColor(prefs['srw_4_6_color'])
        self.m9_11_color = QtGui.QColor(prefs['srw_9_11_color'])

        if update_gui:
            if self.use_left:
                self.srw_0_2km = utils.comp2vec(self.prof.left_srw_0_2km[0], self.prof.left_srw_0_2km[1])[1]
                self.srw_4_6km = utils.comp2vec(self.prof.left_srw_4_6km[0], self.prof.left_srw_4_6km[1])[1]
                self.srw_9_11km = utils.comp2vec(self.prof.left_srw_9_11km[0], self.prof.left_srw_9_11km[1])[1]
                ## get only the left mover u and v components
                self.sru = self.u - self.srwind[2]
                self.srv = self.v - self.srwind[3]
            else:
                self.srw_0_2km = utils.comp2vec(self.prof.right_srw_0_2km[0], self.prof.right_srw_0_2km[1])[1]
                self.srw_4_6km = utils.comp2vec(self.prof.right_srw_4_6km[0], self.prof.right_srw_4_6km[1])[1]
                self.srw_9_11km = utils.comp2vec(self.prof.right_srw_9_11km[0], self.prof.right_srw_9_11km[1])[1]
                ## get only the right mover u and v components
                self.sru = self.u - self.srwind[0]
                self.srv = self.v - self.srwind[1]

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()

    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        if self.use_left:
            self.srw_0_2km = utils.comp2vec(self.prof.left_srw_0_2km[0], self.prof.left_srw_0_2km[1])[1]
            self.srw_4_6km = utils.comp2vec(self.prof.left_srw_4_6km[0], self.prof.left_srw_4_6km[1])[1]
            self.srw_9_11km = utils.comp2vec(self.prof.left_srw_9_11km[0], self.prof.left_srw_9_11km[1])[1]
            ## get only the left mover u and v components
            self.sru = self.u - self.srwind[2]
            self.srv = self.v - self.srwind[3]
        else:
            self.srw_0_2km = utils.comp2vec(self.prof.right_srw_0_2km[0], self.prof.right_srw_0_2km[1])[1]
            self.srw_4_6km = utils.comp2vec(self.prof.right_srw_4_6km[0], self.prof.right_srw_4_6km[1])[1]
            self.srw_9_11km = utils.comp2vec(self.prof.right_srw_9_11km[0], self.prof.right_srw_9_11km[1])[1]
            ## get only the right mover u and v components
            self.sru = self.u - self.srwind[0]
            self.srv = self.v - self.srwind[1]

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotWinds, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles the painting of the QPixmap onto
        the QWidget.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotWinds, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self.plotBitMap)
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
        Handles painting the plot data onto the
        QPixmap.
        '''
        if self.prof is None:
            return

        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        qp.setRenderHint(qp.Antialiasing)
        qp.setRenderHint(qp.TextAntialiasing)
        ## draw the wind profile
        self.draw_profile(qp)
        qp.end()

    def draw_profile(self, qp):
        '''
        Draws the storm relative wind profile.
        
        Parameters
        ----------
        qp: QtGui.QPainter object
        
        '''
        ## initialize a pen with a red color, thickness of 1, solid line
        if self.prof.wdir.count() == 0:
            return
        pen = QtGui.QPen(self.trace_color, 1)
        pen.setStyle(QtCore.Qt.SolidLine)
  
        ## if there are missing values, get the mask
        try:
            mask = np.maximum(self.sru.mask, self.srv.mask)
            sru = self.sru[~mask]
            srv = self.srv[~mask]
            hgt = self.prof.hght[~mask]
        ## otherwise the data is fine
        except:
            sru = self.sru
            srv = self.srv
            hgt = self.prof.hght

        if len(sru) == 0 or len(srv) == 0 or len(hgt) == 0:
            return

        max_hght_idx = len(hgt) - 1
        while type(hgt[max_hght_idx]) == type(np.ma.masked):
            max_hght_idx -= 1

        interp_hght = np.arange(self.prof.hght[self.prof.sfc], min(hgt[max_hght_idx], self.hmax * 1000.), 10)
        interp_sru = np.interp(interp_hght, hgt[:(max_hght_idx + 1)], sru[:(max_hght_idx + 1)])
        interp_srv = np.interp(interp_hght, hgt[:(max_hght_idx + 1)], srv[:(max_hght_idx + 1)])
        sr_spd = np.hypot(interp_sru, interp_srv)

        qp.setPen(pen)
        for i in range(interp_hght.shape[0] - 1):
            spd1 = sr_spd[i]; spd2 = sr_spd[i+1]
            if utils.QC(spd1) and utils.QC(spd2):
                hgt1 = (interp_hght[i] - interp_hght[0]) / 1000; hgt2 = (interp_hght[i+1] - interp_hght[0]) / 1000
                ## convert the wind speeds to x pixels
                x1 = self.speed_to_pix(spd1); x2 = self.speed_to_pix(spd2)
                ## convert the height values to y pixels
                y1 = self.hgt_to_pix(hgt1); y2 = self.hgt_to_pix(hgt2)
                ## draw a line between the two points
                qp.drawLine(x1, y1, x2, y2)

        if utils.QC(self.srw_0_2km):       
            # Plot the 0-2 km mean SRW
            pen = QtGui.QPen(self.m0_2_color, 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_0_2km); x2 = self.speed_to_pix(self.srw_0_2km)
            y1 = self.hgt_to_pix(0.0); y2 = self.hgt_to_pix(2.0)
            qp.drawLine(x1, y1, x2, y2)

        if utils.QC(self.srw_4_6km):
            # Plot the 4-6 km mean SRW
            pen = QtGui.QPen(self.m4_6_color, 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_4_6km); x2 = self.speed_to_pix(self.srw_4_6km)
            y1 = self.hgt_to_pix(4.0); y2 = self.hgt_to_pix(6.0)
            qp.drawLine(x1, y1, x2, y2)
                    
        if utils.QC(self.srw_9_11km):
            # Plot the 9-11 km mean SRW
            pen = QtGui.QPen(self.m9_11_color, 2)
            pen.setStyle(QtCore.Qt.SolidLine)
            qp.setPen(pen)
            x1 = self.speed_to_pix(self.srw_9_11km); x2 = self.speed_to_pix(self.srw_9_11km)
            y1 = self.hgt_to_pix(9.0); y2 = self.hgt_to_pix(11.0)
            qp.drawLine(x1, y1, x2, y2)

if __name__ == '__main__':
    app_frame = QtGui.QApplication([])    
    tester = plotWinds()
    tester.show()    
    app_frame.exec_()
