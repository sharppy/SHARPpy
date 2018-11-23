import numpy as np
from sharppy.sharptab import thermo

__all__ = ['raiseError', 'numMasked', 'isPRESValid', 'isHGHTValid', 'isWSPDValid']
__all__ += ['isDWPCValid', 'isTMPCValid']

# Data quality exception error
class DataQualityException(Exception):
    pass

def raiseError(string, errorType):
    '''
        raiseError

        This function will raise an exception specified by the errorType variable.

        Parameters
        ----------
        string : str
            the string to be printed out to the user when the exception is thrown

        errorType : Exception
            the type of exception.

        Returns
        -------
        None

    '''
    raise Exception(errorType, string)

def numMasked(arr):
    '''
        numMasked

        This function returns the number of unmasked array elements as well as the
        length of the array.

        Parameters
        ----------
        arr : masked numpy array
            The maksed numpy array

        Returns
        -------
        count : number
            the number of unmasked array elements
        length : number
            the length of the unmasked array

    '''
    return arr.count(), arr.shape[0]

def areProfileArrayLengthEqual(prof):
    '''
        areProfileArrayLengthEqual

        This function checks to see if all of the arrays passed to a Profile object
        have the same length.  If they don't have the same length, then this function
        raises an AssertionError exception.

        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        None

    '''

    if not (len(prof.pres) == len(prof.hght) == len(prof.tmpc) == len(prof.dwpc) ==\
            len(prof.wdir) == len(prof.wspd) == len(prof.u) == len(prof.v) == len(prof.omeg)):
        raiseError("Arrays passed to the Profile object have unequal lengths.", DataQualityException)
 
def isPRESValid(pres):
    '''
        isPRESValid

        This function checks to see if valid pressure (mb)
        values are within the pres array that is passed to the 
        Profile object

        True If:
            1.) pressure array length is > 1
            2.) pressure array is not filled with masked values
            3.) if the pressure array is decreasing with the index
                and there are no repeat values.

        Parameters
        ----------
        pres : array
            pressure array (mb)

        Returns
        -------
        value : bool

    '''
    idx_diff = np.ma.diff(pres)
    neg_pres = np.ma.where(pres <= 0)[0]
    num_ok, total = numMasked(pres)
    if np.all(idx_diff < 0) and len(neg_pres) == 0 and num_ok > 1:
        return True
    else:
        return False

def isHGHTValid(hght):
    '''
        isHGHTValid

        This function checks to see if valid height (m)
        values are within the hght array that is passed to the 
        Profile object

        True/False: True If:
             1.) height array length is > 0
             2.) height array is not filled with masked values
             3.) if the height array is increasing with the index
                 and there are no repeat values.

        Parameters
        ----------
        hght : array
            height array (m)

        Returns
        -------
        value : bool

    '''
    num_ok, total = numMasked(hght)

    try:
        hght = hght[~hght.mask]
    except:
        pass

    idx_diff = np.ma.diff(hght)

    if np.all(idx_diff > 0) and num_ok > 1:
        return True
    else:
        return False

def isWDIRValid(wdir):
    '''
        isWDIRValid

        This function checks to see if valid wind direction (deg)
        values are within the wdir array that is passed to the 
        Profile object

        True if the wind direction array is > 0 in size and
        if the wind directions are between 0 and 360.

        Parameters
        ----------
        wdir : array
            wind direction array (degrees)

        Returns
        -------
        value : bool
    '''
    idx = np.ma.where((wdir > 360) | (wdir < 0))[0]
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


