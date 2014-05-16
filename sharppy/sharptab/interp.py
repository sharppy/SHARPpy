''' Interpolation Routines '''
from __future__ import division
import numpy as np
import numpy.ma as ma
import numpy.testing as npt
from sharppy.sharptab import utils, thermo
from sharppy.sharptab.constants import *


__all__ = ['pres', 'hght', 'temp', 'dwpt', 'vtmp', 'components', 'vec']
__all__ += ['to_agl', 'to_msl']


def pres(prof, h):
    '''
    Interpolates the given data to calculate a pressure at a given height

    Parameters
    ----------
    prof : profile object
        Profile object
    h : number, numpy array
        Height (m) of the level for which pressure is desired

    Returns
    -------
    Pressure (hPa) at the given height

    '''
    return generic_interp_hght(h, prof.hght, prof.logp, log=True)


def hght(prof, p):
    '''
    Interpolates the given data to calculate a height at a given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of the level for which height is desired

    Returns
    -------
    Height (m) at the given pressure

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(np.log10(p), prof.logp[::-1], prof.hght[::-1])


def temp(prof, p):
    '''
    Interpolates the given data to calculate a temperature at a given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of the level for which temperature is desired

    Returns
    -------
    Temperature (C) at the given pressure

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(np.log10(p), prof.logp[::-1], prof.tmpc[::-1])


def dwpt(prof, p):
    '''
    Interpolates the given data to calculate a dew point temperature
    at a given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of the level for which dew point temperature is desired

    Returns
    -------
    Dew point tmperature (C) at the given pressure

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(np.log10(p), prof.logp[::-1], prof.dwpc[::-1])


def vtmp(prof, p):
    '''
    Interpolates the given data to calculate a virtual temperature
    at a given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of the level for which virtual temperature is desired

    Returns
    -------
    Virtual tmperature (C) at the given pressure

    '''
    t = temp(prof, p)
    td = dwpt(prof, p)
    try:
        vt = [thermo.virtemp(pp, tt, tdtd) for pp,tt,tdtd in zip(p, t, td)]
        return ma.asarray(vt)
    except TypeError:
        return thermo.virtemp(p, t, td)


def components(prof, p):
    '''
    Interpolates the given data to calculate the U and V components at a
    given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of a level

    Returns
    -------
    U and V components at the given pressure
    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    U = generic_interp_pres(np.log10(p), prof.logp[::-1], prof.u[::-1])
    V = generic_interp_pres(np.log10(p), prof.logp[::-1], prof.v[::-1])
    return U, V


def vec(p, prof):
    '''
    Interpolates the given data to calculate the wind direction and speed
    at a given pressure

    Parameters
    ----------
    p : number, numpy array
        Pressure (hPa) of a level
    prof : profile object
        Profile object

    Returns
    -------
    Wind direction and magnitude at the given pressure
    '''
    U, V = components(p, prof)
    return utils.comp2vec(U, V)


def to_agl(prof, h):
    '''
    Convert a height from mean sea-level (MSL) to above ground-level (AGL)

    Parameters
    ----------
    h : number, numpy array
        Height of a level
    prof : profile object
        Profile object

    Returns
    -------
    Converted height

    '''
    return h - prof.hght[prof.sfc]


def to_msl(prof, h):
    '''
    Convert a height from above ground-level (AGL) to mean sea-level (MSL)

    Parameters
    ----------
    h : number, numpy array
        Height of a level
    prof : profile object
        Profile object

    Returns
    -------
    Converted height

    '''
    return h + prof.hght[prof.sfc]


def generic_interp_hght(h, hght, field, log=False):
    '''
    Generic interpolation routine

    Parameters
    ----------
    h : number, numpy array
        Height (m) of the level for which pressure is desired
    hght : numpy array
        The array of heights
    field : numpy array
        The variable which is being interpolated
    log : bool
        Flag to determine whether the 'field' variable is in log10 space

    Returns
    -------
    Value of the 'field' variable at the given height

    '''
    if ma.isMaskedArray(hght):
        not_masked1 = ~hght.mask
    else:
        not_masked1 = np.ones(hght.shape)
    if ma.isMaskedArray(field):
        not_masked2 = ~field.mask
    else:
        not_masked2 = np.ones(field.shape)
    not_masked = not_masked1 * not_masked2
    if log:
        return 10**np.interp(h, hght[not_masked], field[not_masked],
                             left=ma.masked, right=ma.masked)
    else:
        return np.interp(h, hght[not_masked], field[not_masked],
                         left=ma.masked, right=ma.masked)


def generic_interp_pres(p, pres, field):
    '''
    Generic interpolation routine

    Parameters
    ----------
    p : number, numpy array
        Pressure (hPa) of the level for which the field variable is desired
    pres : numpy array
        The array of pressure
    field : numpy array
        The variable which is being interpolated
    log : bool
        Flag to determine whether the 'field' variable is in log10 space

    Returns
    -------
    Value of the 'field' variable at the given pressure

    '''
    if ma.isMaskedArray(pres):
        not_masked1 = ~pres.mask
    else:
        not_masked1 = np.ones(pres.shape)
    if ma.isMaskedArray(field):
        not_masked2 = ~field.mask
    else:
        not_masked2 = np.ones(field.shape)
    not_masked = not_masked1 * not_masked2
    return np.interp(p, pres[not_masked], field[not_masked], left=ma.masked,
                     right=ma.masked)










