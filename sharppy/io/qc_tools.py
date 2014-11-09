import numpy as np
from sharppy.sharptab import *

__all__ = ['raiseError', 'numMasked', 'isPRESValid', 'isHGHTValid', 'isWSPDValid']
__all__ += ['isDWPCValid', 'isTMPCValid']

def raiseError(string, errorType):
    raise errorType, string

def numMasked(arr):
    return arr.count(), arr.shape[0]

def areProfileArrayLengthEqual(prof):
    if not (len(prof.pres) == len(prof.hght) == len(prof.tmpc) == len(prof.dwpc) ==\
            len(prof.wdir) == len(prof.wspd) == len(prof.u) == len(prof.v)):
        raiseError("Arrays passed to the Profile object have unequal lengths.", AssertionError)
 
def isPRESValid(pres):
    idx = np.ma.argsort(pres)[::-1]
    idx2 = np.ma.where(pres <= 0)[0]
    num_ok, total = numMasked(pres)
    if pres.all() == pres[idx].all() and len(idx2) == 0 and num_ok > 0:
        return True
    else:
        return False

def isHGHTValid(hght):
    '''
        isWDIRValid

        This function checks to see if valid wind direction (deg)
        values are within the wdir array that is passed to the 
        Profile object

        Parameters
        ----------
        wdir: the wind direction array (degrees)

        Returns
        -------
        True/False: True if the wind direction array is > 0 in size and
                    if the wind directions are between 0 and 360.
    '''
    idx = np.ma.argsort(hght)
    idx2 = np.ma.where(hght < 0)[0]
    num_ok, total = numMasked(hght)
    if hght.all() == hght[idx].all() and len(idx2) == 0 and num_ok > 0:
        return True
    else:
        return False

def isWDIRValid(wdir):
    '''
        isWDIRValid

        This function checks to see if valid wind direction (deg)
        values are within the wdir array that is passed to the 
        Profile object

        Parameters
        ----------
        wdir: the wind direction array (degrees)

        Returns
        -------
        True/False: True if the wind direction array is > 0 in size and
                    if the wind directions are between 0 and 360.
    '''
    idx = np.ma.where((wdir >= 360) | (wdir < 0))[0]
    if len(idx) == 0:
        return True
    else:
        return False

def isWSPDValid(wspd):
    '''
        isWSPDValid

        This function checks to see if valid wind speed (knots)
        values are within the wspd array that is passed to the 
        Profile object

        Parameters
        ----------
        wspd: the wind speed array (knots)

        Returns
        -------
        True/False: True if the wind speeds in the wspd array are all >= 0.
    '''
    idx = np.ma.where(wspd < 0)[0]
    if len(idx) == 0:
        return True
    else:
        return False

def isTMPCValid(tmpc):
    '''
        isTMPCValid

        This function checks to see if valid temperature (Celsius)
        values are within the tmpc array that is passed to the 
        Profile object

        Parameters
        ----------
        tmpc: the temperature array (Celsius)

        Returns
        -------
        True/False: True if the values in the temperature array are all above absolute zero.
    '''
    idx = np.ma.where(thermo.ctok(tmpc) <= 0)[0]
    if len(idx) == 0:
        return True
    else:
        return False

def isDWPCValid(dwpc):
    '''
        isDWPCValid

        This function checks to see if valid dewpoint (Celsius)
        values are within the dwpc array that is passed to the 
        Profile object

        Parameters
        ----------
        dwpc: the dewpoint array (Celsius)

        Returns
        -------
        True/False: True if the values in the dewpoint array are all above absolute zero.
    '''
    idx = np.ma.where(thermo.ctok(dwpc) <= 0)[0]
    if len(idx) == 0:
        return True
    else:
        return False


