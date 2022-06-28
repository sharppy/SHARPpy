
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class progress(QObject):
    _progress = Signal(int, int)
    _text = Signal(str)

    def __init__(self, *args, **kwargs):
        super(progress, self).__init__()
        self._func = None
        self._async = args[0]
        self._ret_val = None

    def __get__(self, obj, cls):
        return partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and hasattr(args[0], '__call__'):
            self._func = args[0]
            ret = self.doasync
        else:
            ret = self.doasync(*args, **kwargs)
        return ret

    def doasync(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

        self._kwargs['__prog__'] = self._progress
        self._kwargs['__text__'] = self._text

        self._progress_dialog = QProgressDialog()
        self._progress.connect(self.updateProgress)
        self._text.connect(self.updateText)
        self._progress_dialog.setMinimum(0)
        self._progress_dialog.setValue(0)

        self._progress_dialog.open()
        self._isfinished = False

        def finish(ret_val):
            self._isfinished = True
            self._progress_dialog.close()
            self._ret_val = ret_val

        self._async.post(self._func, finish, *self._args, **self._kwargs)

        while not self._isfinished:
            QCoreApplication.processEvents()

        return self._ret_val

    @Slot(int, int)
    def updateProgress(self, value, maximum):
        text = self._prog_text

        self._progress_dialog.setMaximum(maximum)
        self._progress_dialog.setValue(value)

        if maximum > 0:
            text += " (%d / %d)" % (value, maximum)
        self._progress_dialog.setLabelText(text)

    @Slot(str)
    def updateText(self, text):
        self._prog_text = text
        self._progress_dialog.setLabelText(text)
