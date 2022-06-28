''' Wind Manipulation Routines '''
from __future__ import division
import numpy as np
import numpy.ma as ma
from sharppy.sharptab import interp, utils
from sharppy.sharptab.constants import *
import warnings

__all__ = ['mean_wind', 'mean_wind_npw', 'mean_wind_old', 'mean_wind_npw_old']
__all__ += ['sr_wind', 'sr_wind_npw', 'wind_shear', 'helicity', 'max_wind']
__all__ += ['non_parcel_bunkers_motion', 'corfidi_mcs_motion', 'mbe_vectors']
__all__ += ['non_parcel_bunkers_motion_experimental', 'critical_angle']

#warnings.warn("Future versions of the routines in the winds module may include options to use height values instead of pressure to specify layers (i.e. SRH, wind shear, etc.)")

def mean_wind(prof, pbot=850, ptop=250, dp=-1, stu=0, stv=0):
    '''
    Calculates a pressure-weighted mean wind through a layer. The default
    layer is 850 to 200 hPa.

    Parameters
    ----------
    prof: profile object
        Profile object
    pbot : number (optional; default 850 hPa)
        Pressure of the bottom level (hPa)
    ptop : number (optional; default 250 hPa)
        Pressure of the top level (hPa)
    dp : negative integer (optional; default -1)
        The pressure increment for the interpolated sounding
    stu : number (optional; default 0)
        U-component of storm-motion vector (kts)
    stv : number (optional; default 0)
        V-component of storm-motion vector (kts)

    Returns
    -------
    mnu : number
        U-component (kts)
    mnv : number
        V-component (kts)

    '''
    if dp > 0: dp = -dp
    if not utils.QC(pbot) or not utils.QC(ptop):
        return ma.masked, ma.masked
    if prof.wdir.count() == 0:
        return ma.masked, ma.masked

    ps = np.arange(pbot, ptop+dp, dp)
    u, v = interp.components(prof, ps)
    # u -= stu; v -= stv
    return ma.average(u, weights=ps)-stu, ma.average(v, weights=ps)-stv


def mean_wind_npw(prof, pbot=850., ptop=250., dp=-1, stu=0, stv=0):
    '''
    Calculates a non-pressure-weighted mean wind through a layer. The default
    layer is 850 to 200 hPa.

    Parameters
    ----------
    prof: profile object
        Profile object
    pbot : number (optional; default 850 hPa)
        Pressure of the bottom level (hPa)
    ptop : number (optional; default 250 hPa)
        Pressure of the top level (hPa)
    dp : negative integer (optional; default -1)
        The pressure increment for the interpolated sounding (mb)
    stu : number (optional; default 0)
        U-component of storm-motion vector (kts)
    stv : number (optional; default 0)
        V-component of storm-motion vector (kts)

    Returns
    -------
    mnu : number
        U-component (kts)
    mnv : number
        V-component (kts)

    '''
    if prof.wdir.count() == 0 or not utils.QC(ptop) or not utils.QC(pbot):
        return ma.masked, ma.masked

    if dp > 0: dp = -dp
    ps = np.arange(pbot, ptop+dp, dp)
    u, v = interp.components(prof, ps)
    # u -= stu; v -= stv
    return u.mean()-stu, v.mean()-stv


def sr_wind(prof, pbot=850, ptop=250, stu=0, stv=0, dp=-1):
    '''
    Calculates a pressure-weighted mean storm-relative wind through a layer.
    The default layer is 850 to 200 hPa. This is a thin wrapper around
    mean_wind().

    Parameters
    ----------
    prof: profile object
        Profile object
    pbot : number (optional; default 850 hPa)
        Pressure of the bottom level (hPa)
    ptop : number (optional; default 250 hPa)
        Pressure of the top level (hPa)
    stu : number (optional; default 0)
        U-component of storm-motion vector (kts)
    stv : number (optional; default 0)
        V-component of storm-motion vector  (kts)
    dp : negative integer (optional; default -1)
        The pressure increment for the interpolated sounding (mb)

    Returns
    -------
    mnu : number
        U-component (kts)
    mnv : number
        V-component (kts)

    '''
    return mean_wind(prof, pbot=pbot, ptop=ptop, dp=dp, stu=stu, stv=stv)


def sr_wind_npw(prof, pbot=850, ptop=250, stu=0, stv=0, dp=-1):
    '''
    Calculates a none-pressure-weighted mean storm-relative wind through a
    layer. The default layer is 850 to 200 hPa. This is a thin wrapper around
    mean_wind_npw().

    Parameters
    ----------
    prof: profile object
        Profile object
    pbot : number (optional; default 850 hPa)
        Pressure of the bottom level (hPa)
    ptop : number (optional; default 250 hPa)
        Pressure of the top level (hPa)
    stu : number (optional; default 0)
        U-component of storm-motion vector (kts)
    stv : number (optional; default 0)
        V-component of storm-motion vector (kts)
    dp : negative integer (optional; default -1)
        The pressure increment for the interpolated sounding (mb)

    Returns
    -------
    mnu : number
        U-component (kts)
    mnv : number
        V-component (kts)

    '''
    return mean_wind_npw(prof, pbot=pbot, ptop=ptop, dp=dp, stu=stu, stv=stv)


def wind_shear(prof, pbot=850, ptop=250):
    '''
    Calculates the shear between the wind at (pbot) and (ptop).

    Parameters
    ----------
    prof: profile object
        Profile object
    pbot : number (optional; default 850 hPa)
        Pressure of the bottom level (hPa)
    ptop : number (optional; default 250 hPa)
        Pressure of the top level (hPa)

    Returns
    -------
    shu : number
        U-component (kts)
    shv : number
        V-component (kts)

    '''
    if prof.wdir.count() == 0 or not utils.QC(ptop) or not utils.QC(pbot):
        return ma.masked, ma.masked

    ubot, vbot = interp.components(prof, pbot)
    utop, vtop = interp.components(prof, ptop)
    shu = utop - ubot
    shv = vtop - vbot
    return shu, shv

def non_parcel_bunkers_motion_experimental(prof):
    '''
        Compute the Bunkers Storm Motion for a Right Moving Supercell
        
        Parameters
        ----------
        prof : profile object
            Profile Object
        
        Returns
        -------
        rstu : number
            Right Storm Motion U-component (kts)
        rstv : number
            Right Storm Motion V-component (kts)
        lstu : number
            Left Storm Motion U-component (kts)
        lstv : number
            Left Storm Motion V-component (kts)
        
        '''
    if prof.wdir.count() == 0:
        return ma.masked, ma.masked, ma.masked, ma.masked

    d = utils.MS2KTS(7.5)     # Deviation value emperically derived as 7.5 m/s
    ## get the msl height of 500m, 5.5km, and 6.0km above the surface
    msl500m = interp.to_msl(prof, 500.)
    msl5500m = interp.to_msl(prof, 5500.)
    msl6000m = interp.to_msl(prof, 6000.)
    
    ## get the pressure of the surface, 500m, 5.5km, and 6.0km levels
    psfc = prof.pres[prof.sfc]
    p500m = interp.pres(prof, msl500m)
    p5500m = interp.pres(prof, msl5500m)
    p6000m = interp.pres(prof, msl6000m)
    
    ## sfc-500m Mean Wind
    mnu500m, mnv500m = mean_wind(prof, psfc, p500m)
    
    ## 5.5km-6.0km Mean Wind
    mnu5500m_6000m, mnv5500m_6000m = mean_wind(prof, p5500m, p6000m)
    
    # shear vector of the two mean winds
    shru = mnu5500m_6000m - mnu500m
    shrv = mnv5500m_6000m - mnv500m
    
    # SFC-6km Mean Wind
    mnu6, mnv6 = mean_wind(prof, psfc, p6000m)
    
    # Bunkers Right Motion
    tmp = d / utils.mag(shru, shrv)
    rstu = mnu6 + (tmp * shrv)
    rstv = mnv6 - (tmp * shru)
    lstu = mnu6 - (tmp * shrv)
    lstv = mnv6 + (tmp * shru)
    
    return rstu, rstv, lstu, lstv


def non_parcel_bunkers_motion(prof):
    '''
    Compute the Bunkers Storm Motion for a Right Moving Supercell

    Parameters
    ----------
    prof : profile object
        Profile Object

    Returns
    -------
    rstu : number
        Right Storm Motion U-component (kts)
    rstv : number
        Right Storm Motion V-component (kts)
    lstu : number
        Left Storm Motion U-component (kts)
    lstv : number
        Left Storm Motion V-component (kts)

    '''
    if prof.wdir.count() == 0:
        return ma.masked, ma.masked, ma.masked, ma.masked

    d = utils.MS2KTS(7.5)     # Deviation value emperically derived as 7.5 m/s
    msl6km = interp.to_msl(prof, 6000.)
    p6km = interp.pres(prof, msl6km)
    # SFC-6km Mean Wind
    mnu6, mnv6 = mean_wind_npw(prof, prof.pres[prof.sfc], p6km)
    # SFC-6km Shear Vector
    shru, shrv = wind_shear(prof, prof.pres[prof.sfc], p6km)

    # Bunkers Right Motion
    tmp = d / utils.mag(shru, shrv)
    rstu = mnu6 + (tmp * shrv)
    rstv = mnv6 - (tmp * shru)
    lstu = mnu6 - (tmp * shrv)
    lstv = mnv6 + (tmp * shru)

    return rstu, rstv, lstu, lstv


def helicity(prof, lower, upper, stu=0, stv=0, dp=-1, exact=True):
    '''
    Calculates the relative helicity (m2/s2) of a layer from lower to upper.
    If storm-motion vector is supplied, storm-relative helicity, both
    positve and negative, is returned.

    Parameters
    ----------
    prof : profile object
        Profile Object
    lower : number
        Bottom level of layer (m, AGL)
    upper : number
        Top level of layer (m, AGL)
    stu : number (optional; default = 0)
        U-component of storm-motion (kts)
    stv : number (optional; default = 0)
        V-component of storm-motion (kts)
    dp : negative integer (optional; default -1)
        The pressure increment for the interpolated sounding (mb)
    exact : bool (optional; default = True)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)

    Returns
    -------
    phel+nhel : number
        Combined Helicity (m2/s2)
    phel : number
        Positive Helicity (m2/s2)
    nhel : number
        Negative Helicity (m2/s2)

    '''
    if prof.wdir.count() == 0 or not utils.QC(lower) or not utils.QC(upper) or not utils.QC(stu) or not utils.QC(stv):
        return ma.masked, ma.masked, ma.masked

    if lower != upper:
        lower = interp.to_msl(prof, lower)
        upper = interp.to_msl(prof, upper)
        plower = interp.pres(prof, lower)
        pupper = interp.pres(prof, upper)
        if np.isnan(plower) or np.isnan(pupper) or \
            type(plower) == type(ma.masked) or type(pupper) == type(ma.masked):
            return np.ma.masked, np.ma.masked, np.ma.masked
        if exact:
            ind1 = np.where(plower >= prof.pres)[0].min()
            ind2 = np.where(pupper <= prof.pres)[0].max()
            u1, v1 = interp.components(prof, plower)
            u2, v2 = interp.components(prof, pupper)
            u = np.concatenate([[u1], prof.u[ind1:ind2+1].compressed(), [u2]])
            v = np.concatenate([[v1], prof.v[ind1:ind2+1].compressed(), [v2]])
        else:
            ps = np.arange(plower, pupper+dp, dp)
            u, v = interp.components(prof, ps)
        sru = utils.KTS2MS(u - stu)
        srv = utils.KTS2MS(v - stv)
        layers = (sru[1:] * srv[:-1]) - (sru[:-1] * srv[1:])
        phel = layers[layers > 0].sum()
        nhel = layers[layers < 0].sum()
    else:
        phel = nhel = 0

    return phel+nhel, phel, nhel


def max_wind(prof, lower, upper, all=False):
    '''
    Finds the maximum wind speed of the layer given by lower and upper levels.
    In the event of the maximum wind speed occurring at multiple levels, the
    lowest level it occurs is returned by default.

    Parameters
    ----------
    prof : profile object
        Profile Object
    lower : number
        Bottom level of layer (m, AGL)
    upper : number
        Top level of layer (m, AGL)
    all : Boolean
        Switch to change the output to sorted wind levels or maximum level.

    Returns
    -------
    p : number, numpy array
        Pressure level (hPa) of max wind speed
    maxu : number, numpy array
        Maximum Wind Speed U-component (kts)
    maxv : number, numpy array
        Maximum Wind Speed V-component (kts)

    '''
    if prof.wdir.count() == 0 or not utils.QC(lower) or not utils.QC(upper):
        return ma.masked, ma.masked, ma.masked

    lower = interp.to_msl(prof, lower)
    upper = interp.to_msl(prof, upper)
    plower = interp.pres(prof, lower)
    pupper = interp.pres(prof, upper)
    if np.ma.is_masked(plower) or np.ma.is_masked(pupper):
        warnings.warn("winds.max_wind() was unable to interpolate between height and pressure correctly.  This may be due to a data integrity issue.")
        return ma.masked, ma.masked, ma.masked
    #print(lower, upper, plower, pupper, prof.pres)
    ind1 = np.where((plower > prof.pres) | (np.isclose(plower, prof.pres)))[0][0]
    ind2 = np.where((pupper < prof.pres) | (np.isclose(pupper, prof.pres)))[0][-1]

    if len(prof.wspd[ind1:ind2+1]) == 0 or ind1 == ind2:
        maxu, maxv =  utils.vec2comp([prof.wdir[ind1]], [prof.wspd[ind1]])
        return maxu, maxv, prof.pres[ind1]

    arr = prof.wspd[ind1:ind2+1]
    inds = np.ma.argsort(arr)
    inds = inds[~arr[inds].mask][::-1]
    maxu, maxv =  utils.vec2comp(prof.wdir[ind1:ind2+1][inds], prof.wspd[ind1:ind2+1][inds])
    if all:
        return maxu, maxv, prof.pres[inds]
    else:
        return maxu[0], maxv[0], prof.pres[inds[0]]


def corfidi_mcs_motion(prof):
    '''
    Calculated the Meso-beta Elements (Corfidi) Vectors

    Parameters
    ----------
    prof : profile object
        Profile Object

    Returns
    -------
    upu : number
        U-component of the upshear vector (kts)
    upv : number
        V-component of the upshear vector (kts)
    dnu : number
        U-component of the downshear vector (kts)
    dnv : number
        V-component of the downshear vector (kts)

    '''
    if prof.wdir.count() == 0:
        return ma.masked, ma.masked, ma.masked, ma.masked
    # Compute the tropospheric (850hPa-300hPa) mean wind
    if prof.pres[ prof.sfc ] < 850:
         mnu1, mnv1 = mean_wind_npw(prof, pbot=prof.pres[prof.sfc], ptop=300.)
    else:
        mnu1, mnv1 = mean_wind_npw(prof, pbot=850., ptop=300.)

    # Compute the low-level (SFC-1500m) mean wind
    p_1p5km = interp.pres(prof, interp.to_msl(prof, 1500.))
    mnu2, mnv2 = mean_wind_npw(prof, prof.pres[prof.sfc], p_1p5km)

    # Compute the upshear vector
    upu = mnu1 - mnu2
    upv = mnv1 - mnv2

    # Compute the downshear vector
    dnu = mnu1 + upu
    dnv = mnv1 + upv

    return upu, upv, dnu, dnv


def mbe_vectors(prof):
    '''
    Thin wrapper around corfidi_mcs_motion()

    Parameters
    ----------
    prof : profile object
        Profile Object

    Returns
    -------
    upu : number
        U-component of the upshear vector (kts)
    upv : number
        V-component of the upshear vector (kts)
    dnu : number
        U-component of the downshear vector (kts)
    dnv : number
        V-component of the downshear vector (kts)

    '''
    return corfidi_mcs_motion(prof)

def critical_angle(prof, stu=0, stv=0):
    '''
    Calculates the critical angle (degrees) as specified by Esterheld and Giuliano (2008).
    If the critical angle is 90 degrees, this indicates that the lowest 500 meters of 
    the storm is experiencing pure streamwise vorticity.

    Parameters
    ----------
    prof : profile object
        Profile Object
    stu : number (optional; default = 0)
        U-component of storm-motion (kts)
    stv : number (optional; default = 0)
        V-component of storm-motion (kts)

    Returns
    -------
    angle : number
        Critical Angle (degrees)

    '''
    if prof.wdir.count() == 0:
        return ma.masked

    if not utils.QC(stu) or not utils.QC(stv):
        return ma.masked

    pres_500m = interp.pres(prof, interp.to_msl(prof, 500))
    u500, v500 = interp.components(prof, pres_500m)
    sfc_u, sfc_v = interp.components(prof, prof.pres[prof.sfc])

    vec1_u, vec1_v = u500 - sfc_u, v500 - sfc_v    
    vec2_u, vec2_v = stu - sfc_u, stv - sfc_v
    vec_1_mag = np.sqrt(np.power(vec1_u, 2) + np.power(vec1_v, 2))
    vec_2_mag = np.sqrt(np.power(vec2_u, 2) + np.power(vec2_v, 2))

    dot = vec1_u * vec2_u + vec1_v * vec2_v
    angle = np.degrees(np.arccos(dot / (vec_1_mag * vec_2_mag)))

    return angle
