import numpy as np
import os
from qtpy import QtGui, QtCore, QtWidgets
import sharppy.sharptab as tab
from sharppy.sharptab.constants import *
import sharppy.databases.sars as sars
import platform

from datetime import datetime

## routine written by Kelton Halbert
## keltonhalbert@ou.edu

__all__ = ['backgroundAnalogues', 'plotAnalogues']

class backgroundAnalogues(QtWidgets.QFrame):
    '''
    Handles drawing the background frame for the
    SARS window.
    '''
    def __init__(self):
        ''' Calls the initUI function to initialize
            the background frame. Inherits from the
            QtWidgets.QFrame Object.
        '''
        super(backgroundAnalogues, self).__init__()
        self.initUI()

    def initUI(self):
        '''
        Initializes the frame.
        
        The frame is drawn on a QPixmap, 
        and is not rendered visible in this function.
        '''
        ## set the frame stylesheet
        self.setStyleSheet("QFrame {"
            "  background-color: rgb(0, 0, 0);"
            "  border-width: 1px;"
            "  border-style: solid;"
            "  border-color: #3399CC;}")
        ## Set the padding constants
        self.lpad = 3; self.rpad = 5
        self.tpad = 5; self.bpad = 5



        ## set the window metrics (height, width)
        self.wid = self.size().width()
        self.hgt = self.size().height()
        self.tlx = self.rpad; self.tly = self.tpad
        self.brx = self.wid; self.bry = self.hgt

        fsize1 = np.floor(.09 * self.hgt)
        fsize2 = np.floor(.07 * self.hgt)
        fsize3 = np.floor(.06 * self.hgt)

        self.tpad = np.floor(.03 * self.hgt)

        ## set various fonts
        self.title_font = QtGui.QFont('Helvetica', fsize1)
        self.plot_font = QtGui.QFont('Helvetica', fsize2)
        self.match_font = QtGui.QFont('Helvetica', fsize3)
        ## get the metrics on the fonts. This is used to get their size.
        self.title_metrics = QtGui.QFontMetrics( self.title_font )
        self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
        self.match_metrics = QtGui.QFontMetrics( self.match_font )
        ## get the height of each font. This is so that we can do propper font aligning
        ## when drawing text

        if platform.system() == "Windows":
            fsize1 -= self.title_metrics.descent()
            fsize2 -= self.plot_metrics.descent()
            fsize3 -= self.match_metrics.descent()

            self.title_font = QtGui.QFont('Helvetica', fsize1)
            self.plot_font = QtGui.QFont('Helvetica', fsize2)
            self.match_font = QtGui.QFont('Helvetica', fsize3)
            ## get the metrics on the fonts. This is used to get their size.
            self.title_metrics = QtGui.QFontMetrics( self.title_font )
            self.plot_metrics = QtGui.QFontMetrics( self.plot_font )
            self.match_metrics = QtGui.QFontMetrics( self.match_font )
		
        self.title_height = self.title_metrics.xHeight() + self.tpad
        self.plot_height = self.plot_metrics.xHeight() + self.tpad
        self.match_height = self.match_metrics.xHeight() + self.tpad
        ## this variable gets set and used by other functions for knowing
        ## where in pixel space the last line of text ends
        self.ylast = self.tpad
        self.text_start = 0
        ## placement of supercell vs hail
        self.divide = (self.brx / 6)*3+10
        self.selectRect = None

        ## The widget will be drawn on a QPixmap
        self.plotBitMap = QtGui.QPixmap(self.width()-2, self.height()-2)
        self.plotBitMap.fill(self.bg_color)
        ## plot the background
        self.plotBackground()
    
    def draw_frame(self, qp):
        '''
        Draws the background frame and the text headers.
        '''
        ## initialize a white pen with thickness 1 and a solid line
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        
        ## make the initial x value relative to the width of the frame
        x1 = self.brx / 6
        self.ylast = self.tpad

        ## use the larger title font to plot the title, and then
        ## add to self.ylast the height of the font + padding
        qp.setFont(self.title_font)
        rect0 = QtCore.QRect(0, self.ylast, self.brx, self.title_height)
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
        ## Add to the running sum once more for future text
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
        
        This draws onto a QPixmap.
        '''
        ## initialize a QPainter objext
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the frame
        self.draw_frame(qp)
        qp.end()


class plotAnalogues(backgroundAnalogues):
    updatematch = QtCore.Signal(str)
    '''
    Handles the non-background plotting
    of the SARS window. This inherits a
    backgroundAnalogues Object that
    takes care of drawing the frame
    background onto a QPixmap. This will
    inherit that QPixmap and continue 
    drawing on it, finally rendering the
    QPixmap via the function paintEvent.
    '''
    def __init__(self):
        '''
        Initializes the data needed for drawing the
        data onto the QPixmap. 
        
        Parameters
        ----------
        prof: a Profile object
        self.view.setDataSource(self.data_sources[self.model], self.run)
        
        '''
        ## get the surfce based, most unstable, and mixed layer
        ## parcels to use for indices, as well as the sounding
        ## profile itself.
        self.bg_color = QtGui.QColor('#000000')
        self.fg_color = QtGui.QColor('#ffffff')
        self.use_left = False
        super(plotAnalogues, self).__init__()
        self.prof = None 

    def setProf(self, prof):
        self.prof = prof

        if self.use_left:
            self.hail_matches = prof.left_matches
            self.sup_matches = prof.left_supercell_matches
        else:
            self.hail_matches = prof.right_matches
            self.sup_matches = prof.right_supercell_matches

        self.ybounds_hail = np.empty((len(self.hail_matches[0]),2))
        self.ybounds_sup = np.empty((len(self.sup_matches[0]),2))

        self.ylast = self.tpad
        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()


    def setPreferences(self, update_gui=True, **prefs):
        self.bg_color = QtGui.QColor(prefs['bg_color'])
        self.fg_color = QtGui.QColor(prefs['fg_color'])

        if update_gui:
            if self.use_left:
                self.hail_matches = self.prof.left_matches
                self.sup_matches = self.prof.left_supercell_matches
            else:
                self.hail_matches = self.prof.right_matches
                self.sup_matches = self.prof.right_supercell_matches

            self.ybounds_hail = np.empty((len(self.hail_matches[0]),2))
            self.ybounds_sup = np.empty((len(self.sup_matches[0]),2))

            self.clearData()
            self.plotBackground()
            self.plotData()
            self.update()


    def setDeviant(self, deviant):
        self.use_left = deviant == 'left'

        if self.use_left:
            self.hail_matches = self.prof.left_matches
            self.sup_matches = self.prof.left_supercell_matches
        else:
            self.hail_matches = self.prof.right_matches
            self.sup_matches = self.prof.right_supercell_matches

        self.ybounds_hail = np.empty((len(self.hail_matches[0]),2))
        self.ybounds_sup = np.empty((len(self.sup_matches[0]),2))

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
        super(plotAnalogues, self).resizeEvent(e)
        ## if the window is resized, replot the data
        ## in the QPixmap.
        self.plotData()
    
    def paintEvent(self, e):
        '''
        Handles drawing the QPixmap onto the
        widget.
        
        Parameters
        ----------
        e: an Event object
        
        '''
        super(plotAnalogues, self).paintEvent(e)
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
        Handles the drawing of the SARS
        matches onto the QPixmap.
        '''
        if self.prof is None:
            return

        ## initialize a QPainter object
        qp = QtGui.QPainter()
        qp.begin(self.plotBitMap)
        ## draw the matches
        self.drawSARS(qp, type='HAIL')
        self.drawSARS(qp, type='TOR')
        qp.end()
    
    def drawSARS(self, qp, **kwargs):
        '''
        This draws the SARS matches.
        
        Parameters
        ----------
        qp: a QtGui.QPainter Object
        type: A string for the type of 
            SARS matches. 'HAIL' for 
            hail matches and 'TOR' for 
            supercell matches.
        '''
        x1 = self.brx / 6
        ## get the type of matches, and determine
        ## which side of the frame the matches will
        ## be plotted in.
        type = kwargs.get('type', 'HAIL')
        if type == 'TOR':
            self.matches = self.sup_matches
            sigstr = 'TOR'
            ## this is the horizontal placement
            ## of the text in the frame. Valid
            ## integers are from 0-6.
            place = 1
            ## the quality match date [0] and the type/size
            ## [1] palcement are set in this tuple.
            place2 = (self.lpad, (self.brx/2.) - x1 * 3./4. + 2)
            self.ybounds = self.ybounds_sup
        else:
            self.matches = self.hail_matches
            sigstr = 'SIG'
            ## this is the horizontal placement
            ## of the text in the frame. Valid
            ## integers are from 0-6.
            place = 4
            ## the quality match date [0] and the type/size
            ## [1] palcement are set in this tuple.
            place2 = (x1*3+7, x1*5.5-5)
            self.ybounds = self.ybounds_hail

        ## if there are no matches, leave the function to prevent crashing
        pen = QtGui.QPen(self.fg_color, 1, QtCore.Qt.SolidLine)
        if self.matches[0].size == 0:
            pen.setColor(self.fg_color)
            qp.setPen(pen)
            qp.setFont(self.match_font)
            ## draw the text 2/5 from the top
            rect2 = QtCore.QRect(x1*place, self.bry * (2./5.), x1, self.match_height)
            qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                'No Quality Matches')

        else:
            ## set the pen, font
            qp.setPen(pen)
            qp.setFont(self.plot_font)
            ## self.ylast has to be this way in order to plot relative to the bottom
            self.ylast = (self.bry - self.bpad*3)
            
            ## get various data to be plotted
            sig_prob = tab.utils.INT2STR( np.around( self.matches[-1]*100 ) )
            sig_str = 'SARS: ' + sig_prob + '% ' + sigstr
            num_matches = tab.utils.INT2STR( self.matches[-3] )
            match_str = '(' + num_matches + ' loose matches)'
            
            ## if there are more than 0 loose matches, draw
            ## draw the match statistics
            if self.matches[-3] > 0:
                qp.setFont(self.match_font)
                ## set the color of the font
                if self.matches[-1]*100. >= 50.:
                    pen.setColor(QtCore.Qt.magenta)
                    qp.setPen(pen)
                else:
                    pen.setColor(self.fg_color)
                    qp.setPen(pen)
                ## draw the text
                rect0 = QtCore.QRect(x1*place, self.ylast, x1, self.match_height)
                qp.drawText(rect0, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                            sig_str)
                ## since we start at the bottom and move up, subtract the height instead of add
                self.ylast -= (self.match_height + self.bpad)
                
                rect1 = QtCore.QRect(x1*place, self.ylast, x1, self.match_height)
                qp.drawText(rect1, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    match_str)
            ## If not, don't do anything
            else:
                pass
            
            ## if there are no quality matches, let the gui know
            if len(self.matches[0]) == 0:
                pen.setColor(self.fg_color)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## draw the text 2/5 from the top
                rect2 = QtCore.QRect(x1*place, self.bry * (2./5.), x1, self.match_height)
                qp.drawText(rect2, QtCore.Qt.TextDontClip | QtCore.Qt.AlignCenter,
                    'No Quality Matches')
            ## if there are more than 0 quality matches...
            else:
                pen.setColor(self.fg_color)
                qp.setPen(pen)
                qp.setFont(self.match_font)
                ## start the vertical sum at the reference point
                self.ylast = self.text_start
                idx  = 0
                ## loop through each of the matches
                i = 0
                for m in self.matches[0]:
                    mdate, mloc = m.split(".")
                    mdate = datetime.strptime(mdate, "%y%m%d%H").strftime("%d %b %y %HZ")
                    match_str = "%s (%s)" % (mdate, mloc)
                    ## these are the rectangles that matches will plot inside of
                    rect3 = QtCore.QRect(place2[0], self.ylast, x1, self.match_height)
                    rect4 = QtCore.QRect(place2[1], self.ylast, x1, self.match_height)
                    self.ybounds[i, 0] = self.ylast
                    self.ybounds[i, 1] = self.ylast + self.match_height
                    ## size or type is used for setting the color
                    size = self.matches[1][idx]
                    if type == 'TOR':
                        size_str = size[:-3]
                        if size.startswith('SIG'):
                            pen.setColor(QtGui.QColor(RED))
                            qp.setPen(pen)
                        elif size.startswith('WEAK'):
                            pen.setColor(QtGui.QColor(LBLUE))
                            qp.setPen(pen)
                        elif size.startswith('NON'):
                            pen.setColor(QtGui.QColor(LBROWN))
                            qp.setPen(pen)
                    else:
                        size_str = str( format(size, '.2f' ) )
                        if size >= 2.0:
                            pen.setColor(QtGui.QColor(RED))
                            qp.setPen(pen)
                        else:
                            pen.setColor(QtGui.QColor(LBLUE))
                            qp.setPen(pen)
                    ## draw the text
                    qp.drawText(rect3, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, match_str )
                    qp.drawText(rect4, QtCore.Qt.TextDontClip | QtCore.Qt.AlignLeft, size_str )
                    ## is there is a selected match, draw the bounds
                    if self.selectRect is not None:
                        pen.setColor(QtGui.QColor(LBLUE))
                        qp.setPen(pen)
                        topLeft = self.selectRect.topLeft()
                        topRight = self.selectRect.topRight()
                        bottomLeft = self.selectRect.bottomLeft()
                        bottomRight = self.selectRect.bottomRight()
                        qp.drawLine(topLeft, topRight)
                        qp.drawLine(bottomLeft, bottomRight)
                    idx += 1
                    i += 1
                    ## add to the running vertical sum
                    vspace = self.match_height
                    if platform.system() == "Windows":
                        vspace += self.match_metrics.descent()
                    self.ylast += vspace
            self.ylast = self.tpad

    def mousePressEvent(self, e):
        if self.prof is None or (len(self.sup_matches[0]) == 0 and len(self.hail_matches[0]) == 0):
            return

        pos = e.pos()
        ## is this a supercell match?
        if pos.x() < (self.brx / 2.):
            ## loop over supercells
            for i, bound in enumerate(self.ybounds_sup):
                if bound[0] < pos.y() and bound[1] > pos.y():
                    filematch = sars.getSounding(self.sup_matches[0][i], "supercell")
                    print(filematch)
                    self.updatematch.emit(filematch)
                    ## set the rectangle used for showing
                    ## a selected match
                    self.selectRect = QtCore.QRect(0, self.ybounds_sup[i, 0],
                                    self.brx / 2.,
                                    self.ybounds_sup[i, 1] - self.ybounds_sup[i, 0])
                    break
        ## is this a hail match?
        elif pos.x() > (self.brx / 2.):
            ## loop over hail
            for i, bound in enumerate(self.ybounds_hail):
                if bound[0] < pos.y() and bound[1] > pos.y():
                    filematch = sars.getSounding(self.hail_matches[0][i], "hail")
                    print(filematch)
                    self.updatematch.emit(filematch)
                    ## set the rectangle used for showing
                    ## a selected match
                    self.selectRect = QtCore.QRect(self.brx / 2., self.ybounds_hail[i, 0],
                                    self.brx / 2.,
                                    self.ybounds_hail[i, 1] - self.ybounds_hail[i, 0])
                    break
        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()
        #logging.debug("Calling plotAnaloges.parentWidget().setFocus()")
        self.parentWidget().setFocus()

    def setSelection(self, filematch):
        """
            Load in the SARS analog you've clicked.
        """
        match_name = os.path.basename(filematch)
#        print("\n\nSETSELECION:", match_name, filematch, self.sup_matches[0], self.hail_matches[0])
        sup_matches = [sars.getSounding(f, 'supercell').split('/')[-1] for f in self.sup_matches[0]] 
        hail_matches = [sars.getSounding(f, 'hail').split('/')[-1] for f in self.hail_matches[0]]
#        print(sup_matches, hail_matches) 
        if match_name in sup_matches:
            idx = np.where(np.asarray(sup_matches, dtype=str) == match_name)[0][0]
            lbx = 0.
            ybounds = self.ybounds_sup
        if match_name in hail_matches:
            idx = np.where(np.asarray(hail_matches, dtype=str) == match_name)[0][0]
            lbx = self.brx / 2.
            ybounds = self.ybounds_hail

        self.selectRect = QtCore.QRect(lbx, ybounds[idx, 0],
                        self.brx / 2., ybounds[idx, 1] - ybounds[idx, 0])
        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()
        self.parentWidget().setFocus()

    def clearSelection(self):
        self.selectRect = None

        self.clearData()
        self.plotBackground()
        self.plotData()
        self.update()
        #print(self.parent, self.parentWidget())
        #self.setParent(self.parent)
        self.parentWidget().setFocus()


if __name__ == '__main__':
    app_frame = QtGui.QApplication([])        
    #tester = plotText(['sfcpcl', 'mlpcl', 'mupcl'])
    tester = plotAnalogues()
    #tester.setProf()
    tester.show()        
    app_frame.exec_()
