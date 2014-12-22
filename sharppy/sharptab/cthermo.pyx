from __future__ import division
cimport cython
cimport numpy as np
import numpy as np

cdef double ZEROCNK, ROCP

ZEROCNK = 273.15
ROCP = 0.28571426

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef double wobf(double t):
    '''
    Implementation of the Wobus Function for computing the moist adiabats.

    Parameters
    ----------
    t : number, numpy array
    Temperature (C)

    Returns
    -------
    Correction to theta (C) for calculation of saturated potential temperature.

    '''

    cdef double npol, ppol

    t = t - 20.

    if t <= 0:
        npol = 1. + t * (-8.841660499999999e-3 + t * ( 1.4714143e-4 + t * (-9.671989000000001e-7 + t * (-3.2607217e-8 + t * (-3.8598073e-10)))))
        npol = 15.13 / ((npol**4))
        return npol
    else:
        ppol = t * (4.9618922e-07 + t * (-6.1059365e-09 + t * (3.9401551e-11 + t * (-1.2588129e-13 + t * (1.6688280e-16)))))
        ppol = 1 + t * (3.6182989e-03 + t * (-1.3603273e-05 + ppol))
        ppol = (29.93 / (ppol**4)) + (0.96 * t) - 14.8
        return ppol

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef double satlift(double p, double thetam):
    '''
    Returns the temperature (C) of a saturated parcel (thm) when lifted to a
    new pressure level (hPa)

    Parameters
    ----------
    p : number
    Pressure to which parcel is raised (hPa)
    thetam : number
    Saturated Potential Temperature of parcel (C)

    Returns
    -------
    Temperature (C) of saturated parcel at new level

    '''

    cdef double eor, pwrp, t1, t2, e1, e2, rate

    if np.fabs(p - 1000.) - 0.001 <= 0: return thetam
    eor = 999
    while np.fabs(eor) - 0.1 > 0:
        if eor == 999:                  # First Pass
            pwrp = ((p / 1000.)**ROCP)
            t1 = (thetam + ZEROCNK) * pwrp - ZEROCNK
            e1 = wobf(t1) - wobf(thetam)
            rate = 1
        else:                           # Successive Passes
            rate = (t2 - t1) / (e2 - e1)
            t1 = t2
            e1 = e2
        t2 = t1 - (e1 * rate)
        e2 = (t2 + ZEROCNK) / pwrp - ZEROCNK
        e2 += wobf(t2) - wobf(e2) - thetam
        eor = e2 * rate
    return t2 - eor

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef double wetlift(double thta, double t, double p2):
    '''
    Lifts a parcel moist adiabatically to its new level.

    Parameters
    -----------
    p : number
    Pressure of initial parcel (hPa)
    t : number
    Temperature of initial parcel (C)
    p2 : number
    Pressure of final level (hPa)

    Returns
    -------
    Temperature (C)

    '''
    cdef double c1, c2, thetam

    c1 = wobf(thta)
    c2 = wobf(t)
    thetam = thta - c1 + c2
    return satlift(p2, thetam)
