from PySide import QtGui
import sys

# A short utility to use PySide to detect the screen resolution
# (for use in testing the SHARPpy GUI)

app = QtGui.QApplication(sys.argv)
screen_rect = app.desktop().screenGeometry()
width, height = screen_rect.width(), screen_rect.height()
print("Screen Resolution:", str(width) + 'x' + str(height))
