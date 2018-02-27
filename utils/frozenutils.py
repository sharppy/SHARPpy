import sys, os
import platform

import multiprocessing
try:
    import multiprocessing.forking as forking
except ImportError:
    if platform.system() == "Windows":
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking

_env_frozen = 'frozen'
_env_frozen_path = '_MEIPASS'
_env_mp_frozen_path = _env_frozen_path + '2'

def isFrozen():
    return getattr(sys, _env_frozen, False)
    
def frozenPath():
    return getattr(sys, _env_frozen_path, None)

def freezeSupport():
    if platform.system() == "Windows" and isFrozen():
        multiprocessing.freeze_support()

class _Popen(forking.Popen):
    def __init__(self, *args, **kw):
        if isFrozen():
            # We have to set original _MEIPASS2 value from sys._MEIPASS
            # to get --onefile mode working.
            # Last character is stripped in C-loader. We have to add
            # '/' or '\\' at the end.
            os.putenv(_env_mp_frozen_path, frozenPath() + os.sep)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, 'frozen'):
                # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                # available. In those cases we cannot delete the variable
                # but only set it to the empty string. The bootloader
                # can handle this case.
                if hasattr(os, 'unsetenv'):
                    os.unsetenv(_env_mp_frozen_path)
                else:
                    os.putenv(_env_mp_frozen_path, '')


class Process(multiprocessing.Process):
    _Popen = _Popen

Queue = multiprocessing.Queue
