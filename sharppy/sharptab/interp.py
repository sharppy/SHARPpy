''' Interpolation Routines '''
from __future__ import division
import numpy as np
import numpy.ma as ma
import numpy.testing as npt
from sharppy.sharptab import utils, thermo
from sharppy.sharptab.constants import *


__all__ = ['pres', 'hght', 'temp', 'dwpt', 'vtmp', 'components', 'vec']
__all__ += ['thetae', 'wetbulb', 'theta', 'mixratio']
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
    Pressure (hPa) at the given height : number, numpy array

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
    Height (m) at the given pressure : number, numpy array

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.hght[::-1])

def omeg(prof, p):
    '''
    Interpolates the given data to calculate a omega at a given pressure

    Parameters
    ----------
    prof : profile object
        Profile object
    p : number, numpy array
        Pressure (hPa) of the level for which temperature is desired

    Returns
    -------
    Omega (microbars/second) at the given pressure : number, numpy array

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.omeg[::-1])

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
    Temperature (C) at the given pressure : number, numpy array

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.tmpc[::-1])

def thetae(prof, p):
    '''
        Interpolates the given data to calculate theta-e at a given pressure
        
        Parameters
        ----------
        prof : profile object
        Profile object
        p : number, numpy array
        Pressure (hPa) of the level for which temperature is desired
        
        Returns
        -------
        Theta-E (C) at the given pressure : number, numpy array
        
        '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.thetae[::-1])

def mixratio(prof, p):
    '''
        Interpolates the given data to calculate water vapor mixing ratio at a given pressure
        
        Parameters
        ----------
        prof : profile object
        Profile object
        p : number, numpy array
        Pressure (hPa) of the level for which mixing ratio is desired
        
        Returns
        -------
        Water vapor mixing ratio (g/kg) at the given pressure : number, numpy array
        
        '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.wvmr[::-1])


def theta(prof, p):
    '''
        Interpolates the given data to calculate theta at a given pressure
        
        Parameters
        ----------
        prof : profile object
        Profile object
        p : number, numpy array
        Pressure (hPa) of the level for which potential temperature is desired
        
        Returns
        -------
        Theta (C) at the given pressure : number, numpy array
        
        '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.theta[::-1])

def wetbulb(prof, p):
    '''
        Interpolates the given data to calculate a wetbulb temperature at a given pressure
        
        Parameters
        ----------
        prof : profile object
        Profile object
        p : number, numpy array
        Pressure (hPa) of the level for which wetbulb temperature is desired
        
        Returns
        -------
        Wetbulb temperature (C) at the given pressure : number, numpy array
        
        '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.wetbulb[::-1])

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
    Dew point tmperature (C) at the given pressure : number, numpy array

    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.dwpc[::-1])


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
    Virtual tmperature (C) at the given pressure : number, numpy array

    '''
    return generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.vtmp[::-1])


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
    U and V components at the given pressure (kts) : number, numpy array
    '''
    # Note: numpy's interpoloation routine expects the interpoloation
    # routine to be in ascending order. Because pressure decreases in the
    # vertical, we must reverse the order of the two arrays to satisfy
    # this requirement.
    if prof.wdir.count() == 0:
        return ma.masked, ma.masked
    U = generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.u[::-1])
    V = generic_interp_pres(ma.log10(p), prof.logp[::-1], prof.v[::-1])
    return U, V


def vec(prof, p):
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
    Wind direction (degrees) and magnitude (kts) at the given pressure : number, numpy array
    '''
    U, V = components(prof, p)
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
    Converted height (m AGL) : number, numpy array

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
    Converted height (m MSL) : number, numpy array

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
    Value of the 'field' variable at the given height : number, numpy array

    '''
    if field.count() == 0 or hght.count() == 0:
        return ma.masked
    if ma.isMaskedArray(hght):
        # Multiplying by ones ensures that the result is an array, not a single value ... which 
        # happens sometimes ... >.<
        not_masked1 = ~hght.mask * np.ones(hght.shape, dtype=bool) 
    else:
        not_masked1 = np.ones(hght.shape)
    if ma.isMaskedArray(field):
        not_masked2 = ~field.mask * np.ones(field.shape, dtype=bool)
    else:
        not_masked2 = np.ones(field.shape)
    not_masked = not_masked1 * not_masked2

    field_intrp = np.interp(h, hght[not_masked], field[not_masked],
                         left=ma.masked, right=ma.masked)
 
    if hasattr(h, 'shape') and h.shape == tuple():
        h = h[()]

    if type(h) != type(ma.masked) and np.all(~np.isnan(h)):
        # Bug fix for Numpy v1.10: returns nan on the boundary.
        field_intrp = ma.where(np.isclose(h, hght[not_masked][0]), field[not_masked][0], field_intrp)
        field_intrp = ma.where(np.isclose(h, hght[not_masked][-1]), field[not_masked][-1], field_intrp)

    # Another bug fix: np.interp() returns masked values as nan. We want ma.masked, dangit!
    field_intrp = ma.where(np.isnan(field_intrp), ma.masked, field_intrp)

    # ma.where() returns a 0-d array when the arguments are floats, which confuses subsequent code.
    if hasattr(field_intrp, 'shape') and field_intrp.shape == tuple():
        field_intrp = field_intrp[()]

    if log:
        return 10 ** field_intrp
    else:
        return field_intrp

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
    Value of the 'field' variable at the given pressure : number, numpy array

    '''
    if field.count() == 0 or pres.count() == 0:
        return ma.masked
    if ma.isMaskedArray(pres):
        not_masked1 = ~pres.mask * np.ones(pres.shape, dtype=bool)
    else:
        not_masked1 = np.ones(pres.shape, dtype=bool)
        not_masked1[:] = True
    if ma.isMaskedArray(field):
        not_masked2 = ~field.mask * np.ones(pres.shape, dtype=bool)
    else:
        not_masked2 = np.ones(field.shape, dtype=bool)
        not_masked2[:] = True
    not_masked = not_masked1 * not_masked2

    field_intrp = np.interp(p, pres[not_masked], field[not_masked], left=ma.masked,
                 right=ma.masked)

    if hasattr(p, 'shape') and p.shape == tuple():
        p = p[()]

    if type(p) != type(ma.masked) and np.all(~np.isnan(p)):
        # Bug fix for Numpy v1.10: returns nan on the boundary.
        field_intrp = ma.where(np.isclose(p, pres[not_masked][0]), field[not_masked][0], field_intrp)
        field_intrp = ma.where(np.isclose(p, pres[not_masked][-1]), field[not_masked][-1], field_intrp)

    # Another bug fix: np.interp() returns masked values as nan. We want ma.masked, dangit!
    field_intrp = ma.where(np.isnan(field_intrp), ma.masked, field_intrp)

    # ma.where() returns a 0-d array when the arguments are floats, which confuses subsequent code.
    if hasattr(field_intrp, 'shape') and field_intrp.shape == tuple():
        field_intrp = field_intrp[()]

    return field_intrp
