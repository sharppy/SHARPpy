import sys, os
import numpy as np
import warnings
import utils.frozenutils as frozenutils

HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")

if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    debug = True
    sys.path.insert(0, os.path.normpath(os.getcwd() + "/.."))
else:
    debug = False
    np.seterr(all='ignore')
    warnings.simplefilter('ignore')

if frozenutils.isFrozen():
    if not os.path.exists(HOME_DIR):
        os.makedirs(HOME_DIR)

    outfile = open(os.path.join(HOME_DIR, 'sharppy-out.txt'), 'w')

    sys.stdout = outfile
    sys.stderr = outfile

from sharppy._sharppy_version import __version__, __version_name__, __upstream_version_name__, __upstream_version__

from PySide.QtCore import *
from PySide.QtGui import *
import datetime as date
from functools import partial
from os.path import expanduser, dirname, join, splitext, abspath, exists
from os import getcwd
import ConfigParser
import traceback
from sharppy.sharpget.gui import SHARPGetGUI

class crasher(object):
    def __init__(self, **kwargs):
        self._exit = kwargs.get('exit', False)

    def __get__(self, obj, cls):
        return partial(self.__call__, obj)

    def __call__(self, func):
        def doCrasher(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except:
                ret = None
                msg = "Well, this is embarrassing.\nSHARPGet broke. If it keeps happening, send the detailed information to the developers."
                data = "SHARPGet v%s %s\n" % (__version__, __version_name__) + \
                       "Crash time: %s\n" % str(date.datetime.now()) + \
                       traceback.format_exc()

                if frozenutils.isFrozen():
                    msg1, msg2 = msg.split("\n")

                    msgbox = QMessageBox()
                    msgbox.setText(msg1)
                    msgbox.setInformativeText(msg2)
                    msgbox.setDetailedText(data)
                    msgbox.setIcon(QMessageBox.Critical)
                    msgbox.exec_()
                else:
                    print
                    print msg
                    print
                    print "Detailed Information:"
                    print data

                if self._exit:
                    sys.exit(1)
            return ret
        return doCrasher

class Main(QMainWindow):
    
    HOME_DIR = os.path.join(os.path.expanduser("~"), ".sharppy")
    cfg_file_name = os.path.join(HOME_DIR,'sharppy.ini')

    def __init__(self):
        """
        Initializes the window and reads in the configuration from the file.
        """
        super(Main, self).__init__()

        ## All of these variables get set/reset by the various menus in the GUI
        self.config = ConfigParser.RawConfigParser()
        self.config.read(Main.cfg_file_name)
        if not self.config.has_section('paths'):
            self.config.add_section('paths')

        self.resize(750, 545)

        self.__initUI()

    def __initUI(self):
        """
        Puts the user inteface together
        """
        self.sharpget_gui = SHARPGetGUI(self.config)
        self.setCentralWidget(self.sharpget_gui)
        self.createMenuBar()
        
        ## set the window title
        window_title = 'SHARPget'
        self.setWindowTitle(window_title)
        icon = abspath(join(dirname(__file__), 'icons/SHARPget_imet.png'))
        self.setWindowIcon(QIcon(icon))
        self.show()
        self.raise_()

    def createMenuBar(self):
        """
        Creates the menu bar
        """
        bar = self.menuBar()
        filemenu = bar.addMenu("File")

        exit = QAction("Exit", self, shortcut=QKeySequence("Ctrl+Q"))
        exit.triggered.connect(self.exitApp)        
        filemenu.addAction(exit)

        helpmenu = bar.addMenu("Help")

        about = QAction("About", self)
        about.triggered.connect(self.aboutbox)

        helpmenu.addAction(about)

    def exitApp(self):
        self.close()

    def aboutbox(self):
        """
        Creates and shows the "about" box.
        """
        cur_year = date.datetime.utcnow().year
        msgBox = QMessageBox()
        str = """
        SHARPget v{0:s} {1:s}
        Sounding download and archive utility

        Developed by Nickolai Reimer WFO Billings

        Built on SHARPpy
        Sounding and Hodograph Analysis and Research
        Program for Python

        (C) 2014-{4:d} by Patrick Marsh, John Hart,
        Kelton Halbert, Greg Blumberg, and Tim Supinie.

        Website: http://sharppy.github.io/SHARPpy/
        Contact: sharppy.project@gmail.com
        Contribute: https://github.com/sharppy/SHARPpy/
        
        """.format(__version__, __version_name__, __upstream_version_name__, __upstream_version__, cur_year)
        msgBox.setText(str)
        msgBox.exec_()

    def keyPressEvent(self, e):
        """
        Handles key press events sent to the picker window.
        """
        if e.matches(QKeySequence.Quit):
            self.exitApp()

    def closeEvent(self, e):
        """
        Handles close events (gets called when the window closes).
        """
        self.config.write(open(Main.cfg_file_name, 'w'))

def main():
    @crasher(exit=True)
    def createWindow():
        return Main()

    # Create an application
    app = QApplication([])
    win = createWindow()
    app.setWindowIcon(win.windowIcon())
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
