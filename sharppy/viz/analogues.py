import numpy as np
import os
from PySide import QtGui, QtCore
import sharppy.sharptab as tab
from sharppy.databases.sars import sars_hail
from sharppy.sharptab.constants import *

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundAnalogues', 'plotAnalogues']

class backgroundAnalogues(QtGui.QFrame):
    '''
    Handles drawing the background frame.
    '''
    def __init__(self):
        super(backgroundAnalogues, self).__init__()
        self.initUI()

    def initUI(self):
        ## initialize fram variables such as size,
        ## padding, etc.
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        ## Set the padding constants
        self.lpad = 5; self.rpad = 5
        self.tpad = 5; self.bpad = 5
        ## take care of dynamically sizing the text based on DPI
        if self.physicalDpiX() > 75:
            fsize = 8
        else:
            fsize = 10
        ## set various fonts
        self.title_font = QtGui.QFont('Helvetica', fsize + 4)
        self.plot_font = QtGui.QFont('Helvetica', fsize + 2)
        self.match_font = QtGui.QFont('Helvetica', fsize)
        ## get the metrics on the fonts. This is used to get their size.
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.match_metrics = QtGui.QFontMetrics( self.match_font )
        ## get the height of each font. This is so that we can do propper font aligning
        ## when drawing text
        self.title_height = self.title_metrics.xHeight() + self.tpad
        self.plot_height = self.plot_metrics.xHeight() + self.tpad
        self.match_height = self.match_metrics.xHeight() + self.tpad
        ## this variable gets set and used by other functions for knowing
        ## where in pixel space the last line of text ends
        self.ylast = self.tpad
        self.text_start = 0
        ## set the window metrics
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt
        ## The widget will be drawn on a QPixmap
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(QtCore.Qt.black)
        ## plot the background
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers for indices.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 6
        
        ## use the larger title font to plot the title, and then
        ## add to self.ylast the height of the font + padding
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(0, self.tpad, self.brx, self.title_height)
        qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SARS - Sounding Analogue System')
        self.ylast += (self.title_height + self.tpad)
        
        ## draw some lines to seperate the hail and supercell windows,
        ## then add to the running sum for vertical placement
        qp.drawLine(0, self.ylast, self.brx, self.ylast)
        qp.drawLine(self.brx/2, self.ylast, self.brx/2, self.bry)
        self.ylast += self.tpad
        
        ## plot the text for the hail and supercell windows using the running
        ## ylast sum
        qp.setFont(self.plot_font)
        rect1 = QtCore.QRect(x1*1, self.ylast, x1, self.plot_height)
        qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SUPERCELL')
            
        rect2 = QtCore.QRect(x1*4, self.ylast, x1, self.plot_height)
        qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
            'SGFNT HAIL')
        ## Add to the tunning sum once more for future text
        self.ylast += (self.title_height)
        ## the hail and supercell windows both need to have a vertical starting reference
        self.text_start = self.ylast
    

    
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


class plotAnalogues(backgroundAnalogues):
    '''
    Handles plotting the indices in the frame.
    '''
    def __init__(self, prof):
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.prof = prof
        self.hail_matches = prof.matches
        self.sup_matches = prof.supercell_matches
        super(plotAnalogues, self).__init__()

    def resizeEvent(self, e):
        '''
        Handles when the window is resized.
        '''
        super(plotAnalogues, self).resizeEvent(e)
        self.plotData()
    
    def paintEvent(self, e):
        super(plotAnalogues, self).paintEvent(e)
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
        self.drawSARS_hail(qp)
        self.drawSARS_tor(qp)
        qp.end()
    
    def drawSARS_hail(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## if there are no matches, leave the function to prevent crashing
        if self.hail_matches is np.ma.masked:
            return
        else:
            ## set the pen, font, and starting text positions
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setFont(self.plot_font)
            x1 = self.brx / 6
            y1 = self.bry / 19
            ## self.ylast has to be this way in order to plot relative to the bottom
            self.ylast = (self.bry - self.bpad*3)
            
            ## get various data to be plotted
            sig_hail_prob = tab.utils.INT2STR( np.around( self.hail_matches[-1]*100 ) )
            sig_hail_str = 'SARS: ' + sig_hail_prob + '% SIG'
            num_matches = tab.utils.INT2STR( self.hail_matches[-3] )
            match_str = '(' + num_matches + ' loose matches)'
            
            ## if there are more than 0 loose matches, draw
            ## draw the match statistics
            if self.hail_matches[-3] > 0:
                qp.setFont(self.match_font)
                ## set the color of the font
                if self.hail_matches[-1]*100. >= 50.:
                    pen.setColor(QtCore.Qt.magenta)
                    qp.setPen(pen)
                else:
                    pen.setColor(QtCore.Qt.white)
                    qp.setPen(pen)
                ## draw the text
                rect0 = QtCore.QRect(x1*4, self.ylast, x1, self.match_height)
                qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                            sig_hail_str)
                ## since we start at the bottom and move up, subtract the height instead of add
                self.ylast -= (self.match_height + self.bpad)
                
                rect1 = QtCore.QRect(x1*4, self.ylast, x1, self.match_height)
                qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    match_str)
            ## If not, don't do anything
            else:
                pass
            
            ## if there are no quality matches, let the gui know
            if len(self.hail_matches[0]) == 0:
                pen.setColor(QtCore.Qt.white)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## draw the text 2/5 from the top
                rect2 = QtCore.QRect(x1*4, self.bry * (2./5.), x1, self.match_height)
                qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    'No Quality Matches')
            ## if there are more than 0 quality matches...
            else:
                pen.setColor(QtCore.Qt.white)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## start the vertical sum at the reference point
                self.ylast = self.text_start
                idx  = 0
                ## loop through each of the matches
                for m in self.hail_matches[0]:
                    ## these are the rectangles that matches will plot inside of
                    rect3 = QtCore.QRect(x1*3+10, self.ylast, x1, self.match_height)
                    rect4 = QtCore.QRect(x1*5.5-5, self.ylast, x1, self.match_height)
                    ## hail size used for setting the color
                    size = self.hail_matches[1][idx]
                    if size >= 2.0:
                        pen.setColor(QtGui.QColor('#E60000'))
                        qp.setPen(pen)
                    else:
                        pen.setColor(QtGui.QColor('#06B5FF'))
                        qp.setPen(pen)
                    ## draw the text
                    qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, m )
                    qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, str( format(size, '.2f' ) ) )
                    idx += 1
                    ## add to the running vertical sum
                    self.ylast += (self.match_height)

    def drawSARS_tor(self, qp):
        '''
        This handles the severe indices, such as STP, sig hail, etc.
        ---------
        qp: QtGui.QPainter object
        '''
        ## if there are no matches, leave the function to prevent crashing
        if self.sup_matches is np.ma.masked:
            return
        else:
            ## set the pen, font, and starting text positions
            pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.setFont(self.plot_font)
            x1 = self.brx / 6
            y1 = self.bry / 19
            ## self.ylast has to be this way in order to plot relative to the bottom
            self.ylast = (self.bry - self.bpad*3)
            
            ## get various data to be plotted
            sig_tor_prob = tab.utils.INT2STR( np.around( self.sup_matches[-1]*100 ) )
            sig_tor_str = 'SARS: ' + sig_tor_prob + '% SIG'
            num_matches = tab.utils.INT2STR( self.sup_matches[-3] )
            match_str = '(' + num_matches + ' loose matches)'
            
            ## if there are more than 0 loose matches, draw
            ## draw the match statistics
            if self.sup_matches[-3] > 0:
                qp.setFont(self.match_font)
                ## set the color of the font
                if self.sup_matches[-1]*100. >= 50.:
                    pen.setColor(QtCore.Qt.magenta)
                    qp.setPen(pen)
                else:
                    pen.setColor(QtCore.Qt.white)
                    qp.setPen(pen)
                ## draw the text
                rect0 = QtCore.QRect(x1*1, self.ylast, x1, self.match_height)
                qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    sig_tor_str)
                ## since we start at the bottom and move up, subtract the height instead of add
                self.ylast -= (self.match_height + self.bpad)
                    
                rect1 = QtCore.QRect(x1*1, self.ylast, x1, self.match_height)
                qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    match_str)
            ## If not, don't do anything
            else:
                pass
            
            ## if there are no quality matches, let the gui know
            if len(self.sup_matches[0]) == 0:
                pen.setColor(QtCore.Qt.white)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## draw the text 2/5 from the top
                rect2 = QtCore.QRect(x1*1, self.bry * (2./5.), x1, self.match_height)
                qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    'No Quality Matches')
            ## if there are more than 0 quality matches...
            else:
                pen.setColor(QtCore.Qt.white)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## start the vertical sum at the reference point
                self.ylast = self.text_start
                idx  = 0
                ## loop through each of the matches
                for m in self.sup_matches[0]:
                    ## these are the rectangles that matches will plot inside of
                    rect3 = QtCore.QRect(self.lpad, self.ylast, x1, self.match_height)
                    rect4 = QtCore.QRect(self.lpad + x1 + 30, self.ylast, x1, self.match_height)
                    ## hail size used for setting the color
                    type = self.sup_matches[1][idx]
                    if type == 'SIGTOR':
                        pen.setColor(QtGui.QColor('#E60000'))
                        qp.setPen(pen)
                    elif type == 'WEAKTOR':
                        pen.setColor(QtGui.QColor('#06B5FF'))
                        qp.setPen(pen)
                    else:
                        pen.setColor(QtGui.QColor('#06B5FF'))
                        qp.setPen(pen)
                    ## draw the text
                    qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, m )
                    qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, type )
                    idx += 1
                    ## add to the running vertical sum
                    self.ylast += (self.match_height)







