''' Thermodynamic Library '''
from __future__ import division
import numpy as np
import numpy.ma as ma
from sharppy.sharptab.utils import *
from sharppy.sharptab.constants import *

__all__ = ['drylift', 'thalvl', 'lcltemp', 'theta', 'wobf']
__all__ += ['satlift', 'wetlift', 'lifted', 'vappres', 'mixratio']
__all__ += ['temp_at_mixrat', 'wetbulb', 'thetaw', 'thetae']
__all__ += ['virtemp', 'relh']
__all__ += ['ftoc', 'ctof', 'ctok', 'ktoc', 'ftok', 'ktof']


# Constants Used
c1 = 0.0498646455 ; c2 = 2.4082965 ; c3 = 7.07475
c4 = 38.9114 ; c5 = 0.0915 ; c6 = 1.2035
eps = 0.62197

def drylift(p, t, td):
    '''
    Lifts a parcel to the LCL and returns its new level and temperature.

    Parameters
    ----------
    p : number, numpy array
        Pressure of initial parcel in hPa
    t : number, numpy array
        Temperature of inital parcel in C
    td : number, numpy array
        Dew Point of initial parcel in C

    Returns
    -------
    p2 : number, numpy array
        LCL pressure in hPa
    t2 : number, numpy array
        LCL Temperature in C

    '''
    t2 = lcltemp(t, td)
    p2 = thalvl(theta(p, t, 1000.), t2)
    return p2, t2


def lcltemp(t, td):
    '''
    Returns the temperature (C) of a parcel when raised to its LCL.

    Parameters
    ----------
    t : number, numpy array
        Temperature of the parcel (C)
    td : number, numpy array
        Dewpoint temperature of the parcel (C)

    Returns
    -------
    Temperature (C) of the parcel at it's LCL.

    '''
    s = t - td
    dlt = s * (1.2185 + 0.001278 * t + s * (-0.00219 + 1.173e-5 * s -
        0.0000052 * t))
    return t - dlt


def thalvl(theta, t):
    '''
    Returns the level (hPa) of a parcel.

    Parameters
    ----------
    theta : number, numpy array
        Potential temperature of the parcel (C)
    t : number, numpy array
        Temperature of the parcel (C)

    Returns
    -------
    Pressure Level (hPa [float]) of the parcel
    '''

    t = t + ZEROCNK
    theta = theta + ZEROCNK
    return 1000. / (np.power((theta / t),(1./ROCP)))


def theta(p, t, p2=1000.):
    '''
    Returns the potential temperature (C) of a parcel.

    Parameters
    ----------
    p : number, numpy array
        The pressure of the parcel (hPa)
    t : number, numpy array
        Temperature of the parcel (C)
    p2 : number, numpy array (default 1000.)
        Reference pressure level (hPa)

    Returns
    -------
    Potential temperature (C)

    '''
    return ((t + ZEROCNK) * np.power((p2 / p),ROCP)) - ZEROCNK


def thetaw(p, t, td):
    '''
    Returns the wetbulb potential temperature (C) of a parcel.

    Parameters
    ----------
    p : number
        The pressure of the parcel (hPa)
    t : number
        Temperature of the parcel (C)
    td : number
        Dew point of parcel (C)

    Returns
    -------
    Wetbulb potential temperature (C)

    '''
    p2, t2 = drylift(p, t, td)
    return wetlift(p2, t2, 1000.)


def thetae(p, t, td):
    '''
    Returns the equivalent potential temperature (C) of a parcel.

    Parameters
    ----------
    p : number
        The pressure of the parcel (hPa)
    t : number
        Temperature of the parcel (C)
    td : number
        Dew point of parcel (C)

    Returns
    -------
    Equivalent potential temperature (C)

    '''
    p2, t2 = drylift(p, t, td)
    return theta(100., wetlift(p2, t2, 100.), 1000.)


def virtemp(p, t, td):
    '''
    Returns the virtual temperature (C) of a parcel.  If 
    td is masked, then it returns the temperature passed to the 
    function.

    Parameters
    ----------
    p : number
        The pressure of the parcel (hPa)
    t : number
        Temperature of the parcel (C)
    td : number
        Dew point of parcel (C)

    Returns
    -------
    Virtual temperature (C)

    '''
    
    tk = t + ZEROCNK
    w = 0.001 * mixratio(p, td)
    vt = (tk * (1. + w / eps) / (1. + w)) - ZEROCNK
    if not QC(vt):
        return t
    else:
        return vt

def relh(p, t, td):
    '''
    Returns the virtual temperature (C) of a parcel.

    Parameters
    ----------
    p : number
        The pressure of the parcel (hPa)
    t : number
        Temperature of the parcel (C)
    td : number
        Dew point of parcel (C)

    Returns
    -------
    Relative humidity (%) of a parcel

    '''
    return 100. * vappres(td)/vappres(t) #$mixratio(p, td) / mixratio(p, t)

def temp_at_vappres(e):
    '''
    Returns the temperature (C) given a vapor pressure value (hPa).
    
    Parameters
    ----------
    e : number
        The vapor pressure of a parcel (hPa)

    Returns
    -------
    Temperature (C) of a parcel.
    '''
    L = (2.5*10.**6)
    R_v = 461.5
    T_o = 273.15
    e_so = 6.11
    a = (L/R_v)
    b = (1./T_o)
    return ktoc(np.power( (-1.) * ((1./a)*np.log(e/e_so) - b), -1))

def wobf(t):
    '''
    Implementation of the Wobus Function for computing the moist adiabats.

    .. caution::
        The Wobus function has been found to have a slight
        pressure dependency (Davies-Jones 2008).  This dependency
        is not included in this implementation.  

    Parameters
    ----------
    t : number, numpy array
        Temperature (C)

    Returns
    -------
    Correction to theta (C) for calculation of saturated potential temperature.

    '''
    t = t - 20
    try:
        # If t is a scalar
        if t is np.ma.masked:
            return t
        if t <= 0:
            npol = 1. + t * (-8.841660499999999e-3 + t * ( 1.4714143e-4 + t * (-9.671989000000001e-7 + t * (-3.2607217e-8 + t * (-3.8598073e-10)))))
            npol = 15.13 / (np.power(npol,4))
            return npol
        else:
            ppol = t * (4.9618922e-07 + t * (-6.1059365e-09 + t * (3.9401551e-11 + t * (-1.2588129e-13 + t * (1.6688280e-16)))))
            ppol = 1 + t * (3.6182989e-03 + t * (-1.3603273e-05 + ppol))
            ppol = (29.93 / np.power(ppol,4)) + (0.96 * t) - 14.8
            return ppol
    except ValueError:
        # If t is an array
        npol = 1. + t * (-8.841660499999999e-3 + t * ( 1.4714143e-4 + t * (-9.671989000000001e-7 + t * (-3.2607217e-8 + t * (-3.8598073e-10)))))
        npol = 15.13 / (np.power(npol,4))
        ppol = t * (4.9618922e-07 + t * (-6.1059365e-09 + t * (3.9401551e-11 + t * (-1.2588129e-13 + t * (1.6688280e-16)))))
        ppol = 1 + t * (3.6182989e-03 + t * (-1.3603273e-05 + ppol))
        ppol = (29.93 / np.power(ppol,4)) + (0.96 * t) - 14.8
        correction = np.zeros(t.shape, dtype=np.float64)
        correction[t <= 0] = npol[t <= 0]
        correction[t > 0] = ppol[t > 0]
        return correction



def satlift(p, thetam, conv=0.1):
    '''
    Returns the temperature (C) of a saturated parcel (thm) when lifted to a
    new pressure level (hPa)

    .. caution::
        Testing of the SHARPpy parcel lifting routines has revealed that the
        convergence criteria used the SHARP version (and implemented here) may cause 
        drifting the pseudoadiabat to occasionally "drift" when high-resolution 
        radiosonde data is used.  While a stricter convergence criteria (e.g. 0.01) has shown
        to resolve this problem, it creates a noticable departure from the SPC CAPE values and therefore
        may decalibrate the other SHARPpy functions (e.g. SARS).

    Parameters
    ----------
    p : number
        Pressure to which parcel is raised (hPa)
    thetam : number
        Saturated Potential Temperature of parcel (C)
    conv : number
        Convergence criteria for satlift() (C)

    Returns
    -------
    Temperature (C) of saturated parcel at new level

    '''
    try:
        # If p and thetam are scalars
        if np.fabs(p - 1000.) - 0.001 <= 0: 
            return thetam
        eor = 999
        while np.fabs(eor) - conv > 0:
            if eor == 999:                  # First Pass
                pwrp = np.power((p / 1000.),ROCP)
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
    except ValueError:
        # If p and thetam are arrays
        short = np.fabs(p - 1000.) - 0.001 <= 0
        lft = np.where(short, thetam, 0)
        if np.all(short):
            return lft

        eor = 999
        first_pass = True
        while np.fabs(np.min(eor)) - conv > 0:
            if first_pass:                  # First Pass
                pwrp = np.power((p[~short] / 1000.),ROCP)
                t1 = (thetam[~short] + ZEROCNK) * pwrp - ZEROCNK
                e1 = wobf(t1) - wobf(thetam[~short])
                rate = 1
                first_pass = False
            else:                           # Successive Passes
                rate = (t2 - t1) / (e2 - e1)
                t1 = t2
                e1 = e2
            t2 = t1 - (e1 * rate)
            e2 = (t2 + ZEROCNK) / pwrp - ZEROCNK
            e2 += wobf(t2) - wobf(e2) - thetam[~short]
            eor = e2 * rate
        lft[~short] = t2 - eor
        return lft


def wetlift(p, t, p2):
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
    #if p == p2:
    #    return t
    thta = theta(p, t, 1000.)
    if thta is np.ma.masked or p2 is np.ma.masked:
        return np.ma.masked
    thetam = thta - wobf(thta) + wobf(t)
    return satlift(p2, thetam)



def lifted(p, t, td, lev):
    '''
    Calculate temperature (C) of parcel (defined by p, t, td) lifted
    to the specified pressure level.

    Parameters
    ----------
    p : number
        Pressure of initial parcel in hPa
    t : number
        Temperature of initial parcel in C
    td : number
        Dew Point of initial parcel in C
    lev : number
        Pressure to which parcel is lifted in hPa

    Returns
    -------
    Temperature (C) of lifted parcel

    '''
    p2, t2 = drylift(p, t, td)
    return wetlift(p2, t2, lev)


def vappres(t):
    '''
    Returns the vapor pressure of dry air at given temperature

    Parameters
    ------
    t : number, numpy array
        Temperature of the parcel (C)

    Returns
    -------
    Vapor Pressure of dry air

    '''
    pol = t * (1.1112018e-17 + (t * -3.0994571e-20))
    pol = t * (2.1874425e-13 + (t * (-1.789232e-15 + pol)))
    pol = t * (4.3884180e-09 + (t * (-2.988388e-11 + pol)))
    pol = t * (7.8736169e-05 + (t * (-6.111796e-07 + pol)))
    pol = 0.99999683 + (t * (-9.082695e-03 + pol))
    return 6.1078 / pol**8


def mixratio(p, t):
    '''
    Returns the mixing ratio (g/kg) of a parcel

    Parameters
    ----------
    p : number, numpy array
        Pressure of the parcel (hPa)
    t : number, numpy array
        Temperature of the parcel (hPa)

    Returns
    -------
    Mixing Ratio (g/kg) of the given parcel

    '''
    x = 0.02 * (t - 12.5 + (7500. / p))
    wfw = 1. + (0.0000045 * p) + (0.0014 * x * x)
    fwesw = wfw * vappres(t)
    return 621.97 * (fwesw / (p - fwesw))


def temp_at_mixrat(w, p):
    '''
    Returns the temperature (C) of air at the given mixing ratio (g/kg) and
    pressure (hPa)

    Parameters
    ----------
    w : number, numpy array
        Mixing Ratio (g/kg)
    p : number, numpy array
        Pressure (hPa)

    Returns
    -------
    Temperature (C) of air at given mixing ratio and pressure
    '''
    x = np.log10(w * p / (622. + w))
    x = (np.power(10.,((c1 * x) + c2)) - c3 + (c4 * np.power((np.power(10,(c5 * x)) - c6),2))) - ZEROCNK
    return x


def wetbulb(p, t, td):
    '''
    Calculates the wetbulb temperature (C) for the given parcel

    Parameters
    ----------
    p : number
        Pressure of parcel (hPa)
    t : number
        Temperature of parcel (C)
    td : number
        Dew Point of parcel (C)

    Returns
    -------
    Wetbulb temperature (C)
    '''
    p2, t2 = drylift(p, t, td)
    return wetlift(p2, t2, p)


def ctof(t):
    '''
    Convert temperature from Celsius to Fahrenheit

    Parameters
    ----------
    t : number, numpy array
        The temperature in Celsius

    Returns
    -------
    Temperature in Fahrenheit (number or numpy array)

    '''
    return (1.8 * t) + 32.


def ftoc(t):
    '''
    Convert temperature from Fahrenheit to Celsius

    Parameters
    ----------
    t : number, numpy array
        The temperature in Fahrenheit

    Returns
    -------
    Temperature in Celsius (number or numpy array)

    '''
    return (t - 32.) * (5. / 9.)


def ktoc(t):
    '''
    Convert temperature from Kelvin to Celsius

    Parameters
    ----------
    t : number, numpy array
        The temperature in Kelvin

    Returns
    -------
    Temperature in Celsius (number or numpy array)

    '''
    return t - ZEROCNK


def ctok(t):
    '''
    Convert temperature from Celsius to Kelvin

    Parameters
    ----------
    t : number, numpy array
        The temperature in Celsius

    Returns
    -------
    Temperature in Kelvin (number or numpy array)

    '''
    return t + ZEROCNK


def ktof(t):
    '''
    Convert temperature from Kelvin to Fahrenheit

    Parameters
    ----------
    t : number, numpy array
        The temperature in Kelvin

    Returns
    -------
    Temperature in Fahrenheit (number or numpy array)

    '''
    return ctof(ktoc(t))


def ftok(t):
    '''
    Convert temperature from Fahrenheit to Kelvin

    Parameters
    ----------
    t : number, numpy array
        The temperature in Fahrenheit

    Returns
    -------
    Temperature in Kelvin (number or numpy array)

    '''
    return ctok(ftoc(t))
