from qtpy.QtCore import *
from qtpy.QtGui import *

try:
    import Queue
except ImportError:
    import queue as Queue
import logging
import hashlib
from datetime import datetime
import traceback

class AsyncThreads(QObject):
    """
    AsyncThreads: A class to generate threads for whenever something can't run in the main process.
    """
    def __init__(self, max_threads, debug=False):
        super(AsyncThreads, self).__init__()
        self.threads = {}
        self.callbacks = {}
        self.debug = debug

        self.max_threads = max_threads
        self.running = 0
        self.queue = Queue.PriorityQueue(0)
        return

    def post(self, func, callback, *args, **kwargs):
        """
        Post a thread to be run.
        func:   The function to run in a separate thread
        callback:   The function to run once func() is done. It will be passed the output from func() as a single tuple.
        background [optional]: Boolean specifying whether to run in the background. Background processes are started only
            if there are no higher-priority processes to run. The default value is False.
        *args, **kwargs: Arguments to func()
        """
        thd_id = self._genThreadId()

        background = kwargs.get('background', False)
        if 'background' in kwargs:
            del kwargs['background']

        thd = self._threadFactory(func, thd_id, *args, **kwargs)
        thd.finished.connect(self.finish)

        priority = 1 if background else 0
        self.queue.put((priority, thd_id))

        self.threads[thd_id] = thd
        if callback is None:
            callback = lambda x: x
        self.callbacks[thd_id] = callback

        if not background or self.running < self.max_threads:
            self.startNext()
        return thd_id

    def isFinished(self, thread_id):
        """
        Returns a boolean specifying whether the thread corresponding to thread_id is finished.
        """
        return not (thread_id in self.threads)

    def join(self, thread_id):
        """
        Waits until the thread corresponding to thread_id is finished.
        """
        while not self.isFinished(thread_id):
            QCoreApplication.processEvents()

    def clearQueue(self):
        """
        Clears the queue of processes waiting to be started and kills any threads currently running.
        """
        self.queue = Queue.PriorityQueue(0)
        for thd_id, thd in self.threads.items():
            if thd.isRunning():
                thd.terminate()

        self.threads = {}
        self.callbacks = {}

    def startNext(self):
        try:
            prio, thd_id = self.queue.get(block=False)
        except Queue.Empty:
            return

        self.threads[thd_id].start()
        self.running += 1

    @Slot(str, tuple)
    def finish(self, thread_id, ret_val):
        thd = self.threads[thread_id]
        callback = self.callbacks[thread_id]

        callback(ret_val)

        del self.threads[thread_id]
        del self.callbacks[thread_id]

        self.running -= 1
        if self.running < self.max_threads:
            # Might not be the case if we just started a high-priority thread
            self.startNext()

    def _genThreadId(self):
        time_stamp = datetime.utcnow().isoformat()
        return hashlib.md5(time_stamp.encode('utf-8')).hexdigest()

    def _threadFactory(self, func, thread_id, *args, **kwargs):

        class AsyncThread(QThread):
            finished = Signal(str, tuple)

            def __init__(self, debug=False):
                super(AsyncThread, self).__init__()
                self.debug = debug            

            def run(self):
                try:
                    ret_val = func(*args, **kwargs)
                except Exception as e:
                    logging.exception(e)
                    if self.debug:
                        print(traceback.format_exc())
                    ret_val = e
                if type(ret_val) != tuple:
                    ret_val = (ret_val, )

                self.finished.emit(thread_id, ret_val)

        return AsyncThread(debug=self.debug)
