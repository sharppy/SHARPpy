''' Frequently used functions '''
from __future__ import division
import numpy as np
import numpy.ma as ma
from sharppy.sharptab.constants import MISSING, TOL

__all__ = ['INT2STR','FLOAT2STR','MS2KTS', 'KTS2MS', 'MS2MPH']
__all__ += ['MPH2MS', 'MPH2KTS', 'KTS2MPH', 'M2FT', 'FT2M']
__all__ += ['IN2CM', 'CM2IN']
__all__ += ['vec2comp', 'comp2vec', 'mag', 'QC']

def INT2STR(val):
    '''
    Convert a value (float or int) into an integer string
    by rounding to the nearest integer and returning the 
    string. Used to handle case where value is nan or 
    masked.
    
    Parameters
    ----------
    val: float or int
    
    Returns
    -------
    Val rounded to the nearest int and converted to a string.
    
    '''
    if np.isnan(val):
        return '--'
    try:
        return str( int( np.round( val, 0 ) ) )
    except:
        return str(val)


def FLOAT2STR(val, precision):
    '''
    Convert a value (float or int) into a float string to the 
    decimal place of a specified precision. Used to handle the
    case where the value is nan or masked.
    
    Parameters
    ----------
    val: float or int
    precision: int
        used to specify the precision of the resulting rounded value
    
    Returns
    -------
    val rounded to the nearest specified decimal place and converted
    to a string.
    '''
    try:
        new_val = str( np.round( val, precision ) )
    except:
        new_val = str( val )

    if new_val.strip() == 'nan':
        return '--'
    else:
        return new_val

def MS2KTS(val):
    '''
    Convert meters per second to knots

    Parameters
    ----------
    val : float, numpy_array
        Speed (m/s)

    Returns
    -------
    Val converted to knots (float)

    '''
    return val * 1.94384449


def KTS2MS(val):
    '''
    Convert knots to meters per second

    Parameters
    ----------
    val : float, numpy_array
        Speed (kts)

    Returns
    -------
        Val converted to meters per second (float)

    '''
    return val * 0.514444


def MS2MPH(val):
    '''
    Convert meters per second to miles per hour

    Parameters
    ----------
    val : float, numpy_array
        Speed (m/s)

    Returns
    -------
    Val converted to miles per hour (float)

    '''
    return val * 2.23694


def MPH2MS(val):
    '''
    Convert miles per hour to meters per second

    Parameters
    ----------
    val : float, numpy_array
        Speed (mph)

    Returns
    -------
    Val converted to meters per second (float)

    '''
    return val * 0.44704


def MPH2KTS(val):
    '''
    Convert miles per hour to knots

    Parameters
    ----------
    val : float, numpy_array
        Speed (mph)

    Returns
    -------
    Val converted to knots (float)

    '''
    return val * 0.868976


def KTS2MPH(val):
    '''
    Convert knots to miles per hour

    Parameters
    ----------
    val : float, numpy_array
        Speed (kts)

    Returns
    -------
    Val converted to miles per hour (float)

    '''
    return val * 1.15078


def M2FT(val):
    '''
    Convert meters to feet

    Parameters
    ----------
    val : float, numpy_array
        Distance (m)

    Returns
    -------
        Val converted to feet (float)

    '''
    return val * 3.2808399


def FT2M(val):
    '''
    Convert feet to meters

    Parameters
    ----------
    val : float, numpy_array
        Distance (ft)

    Returns
    -------
        Val converted to meters (float)

    '''
    return val * 0.3048

def IN2CM(val):
    '''
    Convert inches to centimeters

    Parameters
    ----------
    val : float, numpy_array
          Distance (inches)

    Returns
    -------
        Val converted to centimeters (float)
    '''
    return val * 2.54

def CM2IN(val):
    '''
    Convert centimeters to inches

    Parameters
    ----------
    val : float, numpy_array
          Distance (centimeters)

    Returns
    -------
        Val converted to inches (float)
    '''
    return val / 2.54

def _vec2comp(wdir, wspd):
    '''
    Underlying function that converts a vector to its components

    Parameters
    ----------
    wdir : number, masked_array
        Angle in meteorological degrees
    wspd : number, masked_array
        Magnitudes of wind vector

    Returns
    -------
    u : number, masked_array (same as input)
        U-component of the wind
    v : number, masked_array (same as input)
        V-component of the wind

    '''
    u = wspd * ma.sin(np.radians(wdir)) * -1
    v = wspd * ma.cos(np.radians(wdir)) * -1
    return u, v


def vec2comp(wdir, wspd, missing=MISSING):
    '''
    Convert direction and magnitude into U, V components

    Parameters
    ----------
    wdir : number, array_like
        Angle in meteorological degrees
    wspd : number, array_like
        Magnitudes of wind vector (input units == output units)
    missing : number (optional)
        Optional missing parameter. If not given, assume default missing
        value from sharppy.sharptab.constants.MISSING

    Returns
    -------
    u : number, array_like (same as input)
        U-component of the wind (units are the same as those of input speed)
    v : number, array_like (same as input)
        V-component of the wind (units are the same as those of input speed)

    '''
    if not QC(wdir) or not QC(wspd):
        return ma.masked, ma.masked

    wdir = ma.asanyarray(wdir).astype(np.float64)
    wspd = ma.asanyarray(wspd).astype(np.float64)
    wdir.set_fill_value(missing)
    wspd.set_fill_value(missing)
    assert wdir.shape == wspd.shape, 'wdir and wspd have different shapes'
    if wdir.shape:
        wdir[wdir == missing] = ma.masked
        wspd[wspd == missing] = ma.masked
        wdir[wspd.mask] = ma.masked
        wspd[wdir.mask] = ma.masked
        u, v = _vec2comp(wdir, wspd)
        u[np.fabs(u) < TOL] = 0.
        v[np.fabs(v) < TOL] = 0.
    else:
        if wdir == missing:
            wdir = ma.masked
            wspd = ma.masked
        elif wspd == missing:
            wdir = ma.masked
            wspd = ma.masked
        u, v = _vec2comp(wdir, wspd)
        if ma.fabs(u) < TOL:
            u = 0.
        if ma.fabs(v) < TOL:
            v = 0.
    return u, v


def comp2vec(u, v, missing=MISSING):
    '''
    Convert U, V components into direction and magnitude

    Parameters
    ----------
    u : number, array_like
        U-component of the wind
    v : number, array_like
        V-component of the wind
    missing : number (optional)
        Optional missing parameter. If not given, assume default missing
        value from sharppy.sharptab.constants.MISSING

    Returns
    -------
    wdir : number, array_like (same as input)
        Angle in meteorological degrees
    wspd : number, array_like (same as input)
        Magnitudes of wind vector (input units == output units)

    '''
    if not QC(u) or not QC(v):
        return ma.masked, ma.masked

    u = ma.asanyarray(u).astype(np.float64)
    v = ma.asanyarray(v).astype(np.float64)
    u.set_fill_value(missing)
    v.set_fill_value(missing)
    wdir = np.degrees(np.arctan2(-u, -v))

    if wdir.shape:
        u[u == missing] = ma.masked
        v[v == missing] = ma.masked
        wdir[u.mask] = ma.masked
        wdir[v.mask] = ma.masked
        wdir[wdir < 0] += 360
        wdir[np.fabs(wdir) < TOL] = 0.
    else:
        if u == missing or v == missing:
            return ma.masked, ma.masked
        if wdir < 0:
            wdir += 360
        if np.fabs(wdir) < TOL:
            wdir = 0.
    return wdir, mag(u, v)


def mag(u, v, missing=MISSING):
    '''
    Compute the magnitude of a vector from its components

    Parameters
    ----------
    u : number, array_like
        U-component of the wind
    v : number, array_like
        V-component of the wind
    missing : number (optional)
        Optional missing parameter. If not given, assume default missing
        value from sharppy.sharptab.constants.MISSING

    Returns
    -------
    mag : number, array_like
        The magnitude of the vector (units are the same as input)

    '''
    if not QC(u) or not QC(v):
        return ma.masked

    u = np.ma.asanyarray(u).astype(np.float64)
    v = np.ma.asanyarray(v).astype(np.float64)
    u.set_fill_value(missing)
    v.set_fill_value(missing)
    if u.shape:
        u[u == missing] = ma.masked
        v[v == missing] = ma.masked
    else:
        if u == missing or v == missing:
            return ma.masked
    return ma.sqrt(u**2 + v**2)

def QC(val):
    '''
        Tests if a value is masked.
        
        '''
    if type(val) == type(ma.masked): return False
    return True


