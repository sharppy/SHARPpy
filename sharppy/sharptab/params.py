''' Thermodynamic Parameter Routines '''
from __future__ import division
import numpy as np
import numpy.ma as ma
from sharppy.sharptab import interp, utils, thermo, winds
from sharppy.sharptab.constants import *


__all__ = ['DefineParcel', 'Parcel', 'inferred_temp_advection']
__all__ += ['k_index', 't_totals', 'c_totals', 'v_totals', 'precip_water']
__all__ += ['temp_lvl', 'max_temp', 'mean_mixratio', 'mean_theta', 'mean_relh']
__all__ += ['lapse_rate', 'most_unstable_level', 'parcelx', 'bulk_rich']
__all__ += ['bunkers_storm_motion', 'effective_inflow_layer']
__all__ += ['convective_temp']


class DefineParcel(object):
    '''
        Create a parcel from a supplied profile object.
        
        Parameters
        ----------
        prof : profile object
        Profile object
        
        Optional Keywords
        flag : int (default = 1)
        Parcel Selection
        1: Observed Surface Parcel
        2: Forecast Surface Parcel
        3: Most Unstable Parcel
        4: Mean Mixed Layer Parcel
        5: User Defined Parcel
        6: Mean Effective Layer Parcel
        
        Optional Keywords (Depending on Parcel Selected)
        Parcel (flag) == 1: Observed Surface Parcel
        None
        Parcel (flag) == 2: Forecast Surface Parcel
        pres : number (default = 100 hPa)
        Depth over which to mix the boundary layer; only changes
        temperature; does not affect moisture
        Parcel (flag) == 3: Most Unstable Parcel
        pres : number (default = 400 hPa)
        Depth over which to look for the the most unstable parcel
        starting from the surface pressure
        Parcel (flag) == 4: Mixed Layer Parcel
        pres : number (default = 100 hPa)
        Depth over which to mix the surface parcel
        Parcel (flag) == 5: User Defined Parcel
        pres : number (default = SFC - 100 hPa)
        Pressure of the parcel to lift
        tmpc : number (default = Temperature at the provided pressure)
        Temperature of the parcel to lift
        dwpc : number (default = Dew Point at the provided pressure)
        Dew Point of the parcel to lift
        Parcel (flag) == 6: Effective Inflow Layer
        ecape : number (default = 100)
        The minimum amount of CAPE a parcel needs to be considered
        part of the inflow layer
        ecinh : number (default = -250)
        The maximum amount of CINH allowed for a parcel to be
        considered as part of the inflow layer
        
        '''
    def __init__(self, prof, flag, **kwargs):
        self.flag = flag
        if flag == 1:
            self.presval = prof.pres[prof.sfc]
            self.__sfc(prof)
        elif flag == 2:
            self.presval = kwargs.get('pres', 100)
            self.__fcst(prof, **kwargs)
        elif flag == 3:
            self.presval = kwargs.get('pres', 300)
            self.__mu(prof, **kwargs)
        elif flag == 4:
            self.presval = kwargs.get('pres', 100)
            self.__ml(prof, **kwargs)
        elif flag == 5:
            self.presval = kwargs.get('pres', prof.pres[prof.sfc] - 100)
            self.__user(prof, **kwargs)
        elif flag == 6:
            self.presval = kwargs.get('pres', 100)
            self.__effective(prof, **kwargs)
        else:
            print 'Defaulting to Surface Parcel'
            self.presval = kwargs.get('pres', prof.gSndg[prof.sfc])
            self.__sfc(prof)
    
    
    def __sfc(self, prof):
        '''
            Create a parcel using surface conditions
            
            '''
        self.desc = 'Surface Parcel'
        self.pres = prof.pres[prof.sfc]
        self.tmpc = prof.tmpc[prof.sfc]
        self.dwpc = prof.dwpc[prof.sfc]
    
    
    def __fcst(self, prof, **kwargs):
        '''
            Create a parcel using forecast conditions.
            
            '''
        self.desc = 'Forecast Surface Parcel'
        self.tmpc = max_temp(prof)
        self.pres = prof.pres[prof.sfc]
        self.dwpc = thermo.temp_at_mixrat(mean_mixratio(prof), self.pres)
    
    
    def __mu(self, prof, **kwargs):
        '''
            Create the most unstable parcel within the lowest XXX hPa, where
            XXX is supplied. Default XXX is 400 hPa.
            
            '''
        self.desc = 'Most Unstable Parcel in Lowest %.2f hPa' % self.presval
        pbot = prof.pres[prof.sfc]
        ptop = pbot - self.presval
        self.pres = most_unstable_level(prof, pbot=pbot, ptop=ptop)
        self.tmpc = interp.temp(prof, self.pres)
        self.dwpc = interp.dwpt(prof, self.pres)
    
    
    def __ml(self, prof, **kwargs):
        '''
            Create a mixed-layer parcel with mixing within the lowest XXX hPa,
            where XXX is supplied. Default is 100 hPa.
            
            '''
        self.desc = '%.2f hPa Mixed Layer Parcel' % self.presval
        pbot = prof.pres[prof.sfc]
        ptop = pbot - self.presval
        self.pres = pbot
        mtheta = mean_theta(prof, pbot, ptop)
        self.tmpc = thermo.theta(1000., mtheta, self.pres)
        mmr = mean_mixratio(prof, pbot, ptop)
        self.dwpc = thermo.temp_at_mixrat(mmr, self.pres)
    
    
    def __user(self, prof, **kwargs):
        '''
            Create a user defined parcel.
            
            '''
        self.desc = '%.2f hPa Parcel' % self.presval
        self.pres = self.presval
        self.tmpc = kwargs.get('tmpc', interp.temp(prof, self.pres))
        self.dwpc = kwargs.get('dwpc', interp.dwpt(prof, self.pres))
    
    
    def __effective(self, prof, **kwargs):
        '''
            Create the mean-effective layer parcel.
            
            '''
        ecape = kwargs.get('ecape', 100)
        ecinh = kwargs.get('ecinh', -250)
        pbot, ptop = effective_inflow_layer(prof, ecape, ecinh)
        if utils.QC(pbot) and pbot > 0:
            self.desc = '%.2f hPa Mean Effective Layer Centered at %.2f' % ( pbot-ptop, (pbot+ptop)/2.)
            mtha = mean_theta(prof, pbot, ptop)
            mmr = mean_mixratio(prof, pbot, ptop)
            self.pres = (pbot+ptop)/2.
            self.tmpc = thermo.theta(1000., mtha, self.pres)
            self.dwpc = thermo.temp_at_mixrat(mmr, self.pres)
        else:
            self.desc = 'Defaulting to Surface Layer'
            self.pres = prof.pres[prof.sfc]
            self.tmpc = prof.tmpc[prof.sfc]
            self.dwpc = prof.dwpc[prof.sfc]
        if utils.QC(pbot): self.pbot = pbot
        else: self.pbot = ma.masked
        if utils.QC(ptop): self.ptop = ptop
        else: self.pbot = ma.masked


class Parcel(object):
    '''
        Initialize the parcel variables
        
        Parameters
        ----------
        pbot : number
        Lower-bound (pressure; hPa) that the parcel is lifted
        ptop : number
        Upper-bound (pressure; hPa) that the parcel is lifted
        pres : number
        Pressure of the parcel to lift (hPa)
        tmpc : number
        Temperature of the parcel to lift (C)
        dwpc : number
        Dew Point of the parcel to lift (C)
        
        '''
    def __init__(self, **kwargs):
        self.pres = ma.masked
        self.tmpc = ma.masked
        self.dwpc = ma.masked
        self.ptrace = ma.masked
        self.ttrace = ma.masked
        self.blayer = ma.masked
        self.tlayer = ma.masked
        self.entrain = 0.
        self.lclpres = ma.masked
        self.lclhght = ma.masked
        self.lfcpres = ma.masked
        self.lfchght = ma.masked
        self.elpres = ma.masked
        self.elhght = ma.masked
        self.mplpres = ma.masked
        self.mplhght = ma.masked
        self.bplus = ma.masked
        self.bminus = ma.masked
        self.bfzl = ma.masked
        self.b3km = ma.masked
        self.b6km = ma.masked
        self.p0c = ma.masked
        self.pm10c = ma.masked
        self.pm20c = ma.masked
        self.pm30c = ma.masked
        self.hght0c = ma.masked
        self.hghtm10c = ma.masked
        self.hghtm20c = ma.masked
        self.hghtm30c = ma.masked
        self.wm10c = ma.masked
        self.wm20c = ma.masked
        self.wm30c = ma.masked
        self.li5 = ma.masked
        self.li3 = ma.masked
        self.brnshear = ma.masked
        self.brnu = ma.masked
        self.brnv = ma.masked
        self.brn = ma.masked
        self.limax = ma.masked
        self.limaxpres = ma.masked
        self.cap = ma.masked
        self.cappres = ma.masked
        for kw in kwargs: setattr(self, kw, kwargs.get(kw))

def ship(mucape, mumr, lr75, h5_temp, shr06):
    '''
    Calculate the Sig Hail Parameter (SHIP)
    
    Parameters
    ----------
    mucape : Most unstable CAPE from parcel class (MUCAPE)
    mumr : Most unstable parcel mixing ratio (g/kg)
    lr75 : 700-500 mb lapse rate (C/km)
    h5_temp : 500 mb temperature (C)
    shr06 : 0-6 km shear (m/s)
    
    Returns
    -------
    ship : significant hail parameter (unitless)
    '''
    ship = -1. * (mucape * mumr * lr75 * h5_temp * shr06) / 44000000.
    return ship

def stp_cin(mlcape, esrh, ebwd, mllcl, mlcinh):
    
    '''
        
    Calculate the Significant Tornado Parameter (w/CIN)

    Parameters
    ----------
    mlcape : Mixed-layer CAPE from the parcel class (J/kg)
    esrh : effective storm relative helicity (m2/s2)
    ebwd : effective bulk wind difference (m/s)
    mllcl : mixed-layer lifted condensation level (m)
    mlcinh : mixed-layer convective inhibition (J/kg)
    
    Returns
    -------
    stp_cin : significant tornado parameter (unitless)
    '''
    cape_term = mlcape / 1500.
    eshr_term = esrh / 150.
    
    if ebwd < 12.:
        ebwd_term = 0.
    elif ebwd > 30.:
        ebwd_term = 1.5
    else:
        ebwd_term = ebwd / 12.

    if mllcl < 1000.:
        lcl_term = 1.0
    else:
        lcl_term = ((2000. - mllcl) / 1000.)

    if mlcinh > -50:
        cinh_term = 1.0
    else:
        cinh_term = ((mlcinh + 200.) / 150.)

    stp_cin = cape_term * eshr_term * ebwd_term * lcl_term * cinh_term
    return stp_cin



def stp_fixed(sbcape, sblcl, srh01, bwd6):
    
    '''
        
    Calculate the Significant Tornado Parameter (fixed layer)
    
    Parameters
    ----------
    sbcape : Surface based CAPE from the parcel class (J/kg)
    sblcl : Surface based lifted condensation level (LCL) (m)
    srh01 : Surface to 1 km storm relative helicity (m2/s2)
    bwd6 : Bulk wind difference between 0 to 6 km (m/s)
    
    Returns
    -------
    stp_fixed : signifcant tornado parameter (fixed-layer)
    '''
    # Calculate CAPE term
    cape_term = sbcape / 1500.
    
    # Calculate SBLCL term
    if sblcl < 1000.: # less than 1000. meters
        lcl_term = 1.0
    elif sblcl > 2000.: # greater than 2000. meters
        lcl_term = 0.0
    else:
        lcl_term = ((2000.-sblcl)/1000.)

    # Calculate 6BWD term
    if bwd6 > 30.: # greater than 30 m/s
        bwd6_term = 1.5
    elif bwd6 < 12.5:
        bwd6_term = 0.0
    else:
        bwd6_term = bwd6/20.

    srh_term = srh01/150.

    stp_fixed = cape_term * lcl_term * srh_term * bwd6_term
    return stp_fixed



def scp(mucape, srh, ebwd):
    
    '''
    Calculates the Supercell Composite Parameter
    
    Parameters
    ----------
    mucape : Most Unstable CAPE from the parcel class (J/kg)
    srh : the effective SRH from the winds.helicity function (m2/s2)
    ebwd : effective bulk wind difference (m/s)
    
    Returns
    -------
    scp : supercell composite parameter
    '''
    if ebwd > 20:
        ebwd = 20.
    elif ebwd < 10:
        ebwd = 0.
    
    muCAPE_term = mucape / 1000.
    esrh_term = srh / 50.
    ebwd_term = ebwd / 20.

    scp = muCAPE_term * esrh_term * ebwd_term
    return scp


def k_index(prof):
    '''
        Calculates the K-Index from a profile object
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        kind : number
        K-Index
        
        '''
    t8 = interp.temp(prof, 850.)
    t7 = interp.temp(prof, 700.)
    t5 = interp.temp(prof, 500.)
    td7 = interp.dwpt(prof, 700.)
    td8 = interp.dwpt(prof, 850.)
    return t8 - t5 + td8 - (t7 - td7)


def t_totals(prof):
    '''
        Calculates the Total Totals Index from a profile object
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        t_totals : number
        Total Totals Index
        
        '''
    return c_totals(prof) + v_totals(prof)


def c_totals(prof):
    '''
        Calculates the Cross Totals Index from a profile object
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        c_totals : number
        Cross Totals Index
        
        '''
    return interp.dwpt(prof, 850.) - interp.temp(prof, 500.)


def v_totals(prof):
    '''
        Calculates the Vertical Totals Index from a profile object
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        v_totals : number
        Vertical Totals Index
        
        '''
    return interp.temp(prof, 850.) - interp.temp(prof, 500.)


def precip_water(prof, pbot=None, ptop=400, dp=-1, exact=False):
    '''
        Calculates the precipitable water from a profile object within the
        specified layer. The default layer (lower=-1 & upper=-1) is defined to
        be surface to 400 hPa.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        
        Returns
        -------
        pwat : number,
        Precipitable Water (in)
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        dwpt1 = interp.dwpt(prof, pbot)
        dwpt2 = interp.dwpt(prof, ptop)
        mask = ~prof.dwpc.mask[ind1:ind2+1] * ~prof.pres.mask[ind1:ind2+1]
        dwpt = np.concatenate([[dwpt1], prof.dwpc[ind1:ind2+1][mask], [dwpt2]])
        p = np.concatenate([[pbot], prof.pres[ind1:ind2+1][mask], [ptop]])
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp)
        dwpt = interp.dwpt(prof, p)
    w = thermo.mixratio(p, dwpt)
    return (((w[:-1]+w[1:])/2 * (p[:-1]-p[1:])) * 0.00040173).sum()


def inferred_temp_adv(prof, lat=None):
    # Calculates the inferred temperature advection from the surface pressure and up every 100 mb.
    # The units returned are in C/hr, however this function doesn't compare well to SPC in terms of
    # magnitude of the results.  The direction and relative magnitude I think I've got right.
    # My calculations seem to be consistently less than those seen on the SPC website.
    #
    # Need to get actual code from John Hart...however SPC values seem a little high for typical synoptic
    # scale geostrophic temperature advection (10 Kelvin/day is typical?)
    #
    # I'm pretty sure my units are correct...
    
    #
    # I'm using equation 4.1.139 from Bluestein's Synoptic book (Volume 1)
    #
    
    if lat != None:
        omega = (2. * np.pi) / (86164.)
        f = 2. * omega * np.sin(np.radians(lat)) # Units: (s**-1)
        multiplier = (f / 9.81) * (np.pi / 180.) # Units: (s**-1 / (m/s**2)) * (radians/degrees)
    else:
        # If you can't pass the latitude of the profile point, use this calculation (approximate)
        multiplier = ((10.**-4) / 9.81) * (np.pi / 180.) # Units: (s**-1 / (m/s**2)) * (radians/degrees))
    
    pressures = np.arange(prof.pres[prof.get_sfc()], 100, -100) # Units: mb
    temps = thermo.ctok(interp.temp(prof, pressures))
    heights = interp.hght(prof, pressures)
    temp_adv = np.empty(len(pressures) - 1)
    dirs = interp.vec(prof, pressures)[0]
    pressure_bounds = np.empty((len(pressures) - 1, 2))
    for i in range(1, len(pressures)):
        bottom_pres = pressures[i-1]
        top_pres = pressures[i]
        # Get the temperatures from both levels (in Kelvin)
        btemp = temps[i-1]
        ttemp = temps[i]
        # Get the two heights of the top and bottom layer
        bhght = heights[i-1] # Units: meters
        thght = heights[i] # Units: meters
        bottom_wdir = dirs[i-1] # Meteorological degrees (degrees from north)
        top_wdir = dirs[i] # same units as top_wdir
        
        # Calculate the average temperature
        print ttemp, btemp
        avg_temp = (ttemp + btemp) * 2.
        
        # Calculate the mean wind between the two levels (this is assumed to be geostrophic)
        mean_u, mean_v = winds.mean_wind(prof, pbot=bottom_pres, ptop=top_pres)
        mean_wdir, mean_wspd = utils.comp2vec(mean_u, mean_v) # Wind speed is in knots here
        mean_wspd = utils.KTS2MS(mean_wspd) # Convert this geostrophic wind speed to m/s
        
        # Here we calculate the change in wind direction with height (thanks to Andrew Mackenzie for help with this)
        # The sign of d_theta will dictate whether or not it is warm or cold advection
        mod = 180 - bottom_wdir
        top_wdir = top_wdir + mod
        
        if top_wdir < 0:
            top_wdir = top_wdir + 360
        elif top_wdir >= 360:
            top_wdir = top_wdir - 360
        d_theta = top_wdir - 180.
        
        # Here we calculate t_adv (which is -V_g * del(T) or the local change in temperature term)
        # K/s  s * rad/m * deg   m^2/s^2          K        degrees / m
        t_adv = multiplier * np.power(mean_wspd,2) * avg_temp * (d_theta / (thght - bhght)) # Units: Kelvin / seconds
        
        # Append the pressure bounds so the person knows the pressure
        pressure_bounds[i-1, :] = bottom_pres, top_pres
        temp_adv[i-1] = t_adv*60.*60. # Converts Kelvin/seconds to Kelvin/hour (or Celsius/hour)

    return temp_adv, pressure_bounds


def temp_lvl(prof, temp):
    '''
        Calculates the level (hPa) of the first occurrence of the specified
        temperature.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        temp : number
        Temperature being searched (C)
        
        Returns
        -------
        First Level of the temperature (hPa)
        
        '''
    difft = prof.tmpc - temp
    ind1 = ma.where(difft >= 0)[0]
    ind2 = ma.where(difft <= 0)[0]
    if len(ind1) == 0 or len(ind2) == 0:
        return ma.masked
    inds = np.intersect1d(ind1, ind2)
    if len(inds) > 0:
        return prof.pres[inds][0]
    diff1 = ind1[1:] - ind1[:-1]
    ind = np.where(diff1 > 1)[0] + 1
    try:
        ind = ind.min()
    except:
        ind = ind1[-1]
    return np.exp(np.interp(temp, [prof.tmpc[ind+1], prof.tmpc[ind]],
                            [prof.logp[ind+1], prof.logp[ind]]))


def max_temp(prof, mixlayer=100):
    '''
        Calculates a maximum temperature forecast based on the depth of the mixing
        layer and low-level temperatures
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        mixlayer : number (optional; default = 100)
        Top of layer over which to "mix" (hPa)
        
        Returns
        -------
        mtemp : number
        Forecast Maximum Temperature
        
        '''
    mixlayer = prof.pres[prof.sfc] - mixlayer
    temp = thermo.ctok(interp.temp(prof, mixlayer))
    return thermo.ktoc(temp * (prof.pres[prof.sfc] / mixlayer)**ROCP) + 2


def mean_relh(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Calculates the mean relative humidity from a profile object within the
        specified layer.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        
        Returns
        -------
        Mean Mixing Ratio
        
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 100.
    if not utils.QC(interp.temp(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.temp(prof, ptop)): return ma.masked
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        dwpt1 = interp.dwpt(prof, pbot)
        dwpt2 = interp.dwpt(prof, ptop)
        mask = ~prof.dwpc.mask[ind1:ind2+1] * ~prof.pres.mask[ind1:ind2+1]
        dwpt = np.concatenate([[dwpt1], prof.dwpc[ind1:ind2+1][mask],
                               [dwpt2]])
        p = np.concatenate([[pbot], prof.pres[ind1:ind2+1][mask], [ptop]])
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp)
        tmp = interp.temp(prof, p)
        dwpt = interp.dwpt(prof, p)
    rh = thermo.relh(p, tmp, dwpt)
    return ma.average(rh, weights=p)



def mean_mixratio(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Calculates the mean mixing ratio from a profile object within the
        specified layer.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        
        Returns
        -------
        Mean Mixing Ratio
        
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 100.
    if not utils.QC(interp.temp(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.temp(prof, ptop)): return ma.masked
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        dwpt1 = interp.dwpt(prof, pbot)
        dwpt2 = interp.dwpt(prof, ptop)
        mask = ~prof.dwpc.mask[ind1:ind2+1] * ~prof.pres.mask[ind1:ind2+1]
        dwpt = np.concatenate([[dwpt1], prof.dwpc[ind1:ind2+1][mask],
                               [dwpt2]])
        p = np.concatenate([[pbot], prof.pres[ind1:ind2+1][mask], [ptop]])
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp)
        dwpt = interp.dwpt(prof, p)
    w = thermo.mixratio(p, dwpt)
    return ma.average(w, weights=p)


def mean_theta(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Calculates the mean theta from a profile object within the
        specified layer.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        
        Returns
        -------
        Mean Theta
        
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 100.
    if not utils.QC(interp.temp(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.temp(prof, ptop)): return ma.masked
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        theta1 = thermo.theta(interp.pres(prof, pbot), interp.temp(prof, pbot))
        theta2 = thermo.theta(interp.pres(prof, ptop), interp.temp(prof, ptop))
        theta = thermo.theta(prof.pres[ind1:ind2+1], prof.tmpc[ind1:ind2+1])
        mask = ~theta.mask
        theta = np.concatenate([[theta1], theta[mask], [theta2]])
        p = np.concatenate([[pbot], prof.pres[ind1:ind2+1][mask], [ptop]])
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp)
        temp = interp.temp(prof, p)
        theta = thermo.theta(p, temp)
    return ma.average(theta, weights=p)


def lapse_rate(prof, lower, upper, pres=True):
    '''
        Calculates the lapse rate (C/km) from a profile object
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        lower : number
        Lower Bound of lapse rate
        upper : number
        Upper Bound of lapse rate
        pres : bool (optional; default = True)
        Flag to determine if lower/upper are pressure [True]
        or height [False]
        
        Returns
        -------
        lapse rate  (float [C/km])
        '''
    if pres:
        p1 = lower
        p2 = upper
        z1 = interp.hght(prof, lower)
        z2 = interp.hght(prof, upper)
    else:
        z1 = interp.to_msl(prof, lower)
        z2 = interp.to_msl(prof, upper)
        p1 = interp.pres(prof, z1)
        p2 = interp.pres(prof, z2)
    tv1 = interp.vtmp(prof, p1)
    tv2 = interp.vtmp(prof, p2)
    return (tv2 - tv1) / (z2 - z1) * -1000.


def most_unstable_level(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Finds the most unstable level between the lower and upper levels.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        
        Returns
        -------
        Pressure level of most unstable level (hPa)
        
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 400
    if not utils.QC(interp.temp(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.temp(prof, ptop)): return ma.masked
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        t1 = interp.temp(prof, pbot)
        t2 = interp.temp(prof, ptop)
        d1 = interp.dwpt(prof, pbot)
        d2 = interp.dwpt(prof, ptop)
        t = prof.tmpc[ind1:ind2+1]
        d = prof.dwpc[ind1:ind2+1]
        p = prof.pres[ind1:ind2+1]
        mask = ~t.mask * ~d.mask * ~p.mask
        t = np.concatenate([[t1], t[mask], [t2]])
        d = np.concatenate([[d1], d[mask], [d2]])
        p = np.concatenate([[pbot], p[mask], [ptop]])
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp)
        t = interp.temp(prof, p)
        d = interp.dwpt(prof, p)
    p2, t2 = thermo.drylift(p, t, d)
    mt = thermo.wetlift(p2, t2, 1000.)
    ind = np.where(np.fabs(mt - mt.max()) < TOL)[0]
    return p[ind[0]]

def cape(prof, pbot=None, ptop=None, dp=-1, **kwargs):
    '''        
        Lifts the specified parcel, calculates various levels and parameters from
        the profile object. B+/B- are calculated based on the specified layer. 
        
        This is a convenience function for effective_inflow_layer and convective_temp, 
        as well as any function that needs to lift a parcel in an iterative process.
        This function is a stripped back version of the parcelx function, that only
        handles bplus and bminus. The intention is to reduce the computation time in
        the iterative functions by reducing the calculations needed.
        
        For full parcel objects, use the parcelx function.
        
        !! All calculations use the virtual temperature correction unless noted. !!
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        pres : number (optional)
        Pressure of parcel to lift (hPa)
        tmpc : number (optional)
        Temperature of parcel to lift (C)
        dwpc : number (optional)
        Dew Point of parcel to lift (C)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        flag : number (optional; default = 5)
        Flag to determine what kind of parcel to create; See DefineParcel for
        flag values
        lplvals : lifting parcel layer object (optional)
        Contains the necessary parameters to describe a lifting parcel
        
        Returns
        -------
        pcl : parcel object
        Parcel Object
    
    '''
    flag = kwargs.get('flag', 5)
    pcl = Parcel(pbot=pbot, ptop=ptop)
    pcl.lplvals = kwargs.get('lplvals', DefineParcel(prof, flag))
    if prof.pres.compressed().shape[0] < 1: return pcl
    
    # Variables
    pres = kwargs.get('pres', pcl.lplvals.pres)
    tmpc = kwargs.get('tmpc', pcl.lplvals.tmpc)
    dwpc = kwargs.get('dwpc', pcl.lplvals.dwpc)
    pcl.pres = pres
    pcl.tmpc = tmpc
    pcl.dwpc = dwpc
    totp = 0.
    totn = 0.
    tote = 0.
    cinh_old = 0.
    
    # See if default layer is specified
    if not pbot:
        pbot = prof.pres[prof.sfc]
        pcl.blayer = pbot
        pcl.pbot = pbot
    if not ptop:
        ptop = prof.pres[prof.pres.shape[0]-1]
        pcl.tlayer = ptop
        pcl.ptop = ptop
    
    # Make sure this is a valid layer
    if pbot > pres:
        pbot = pres
        pcl.blayer = pbot
    if type(interp.vtmp(prof, pbot)) == type(ma.masked): return ma.masked
    if type(interp.vtmp(prof, ptop)) == type(ma.masked): return ma.masked
    
    # Begin with the Mixing Layer
    pe1 = pbot
    h1 = interp.hght(prof, pe1)
    tp1 = thermo.virtemp(pres, tmpc, dwpc)
    
    # Lift parcel and return LCL pres (hPa) and LCL temp (C)
    pe2, tp2 = thermo.drylift(pres, tmpc, dwpc)
    blupper = pe2
    h2 = interp.hght(prof, pe2)
    te2 = interp.vtmp(prof, pe2)
    
    # Calculate lifted parcel theta for use in iterative CINH loop below
    # RECALL: lifted parcel theta is CONSTANT from LPL to LCL
    theta_parcel = thermo.theta(pe2, tp2, 1000.)
    
    # Environmental theta and mixing ratio at LPL
    bltheta = thermo.theta(pres, interp.temp(prof, pres), 1000.)
    blmr = thermo.mixratio(pres, dwpc)
    
    # ACCUMULATED CINH IN THE MIXING LAYER BELOW THE LCL
    # This will be done in 'dp' increments and will use the virtual
    # temperature correction where possible
    pp = np.arange(pbot, blupper+dp, dp)
    hh = interp.hght(prof, pp)
    tmp_env_theta = thermo.theta(pp, interp.temp(prof, pp), 1000.)
    tmp_env_dwpt = interp.dwpt(prof, pp)
    tv_env = thermo.virtemp(pp, tmp_env_theta, tmp_env_dwpt)
    tmp1 = thermo.virtemp(pp, theta_parcel, thermo.temp_at_mixrat(blmr, pp))
    tdef = (tmp1 - tv_env) / thermo.ctok(tv_env)
    
    lyre = G * (tdef[:-1]+tdef[1:]) / 2 * (hh[1:]-hh[:-1])
    totn = lyre[lyre < 0].sum()
    if not totn: totn = 0.
    
    # Move the bottom layer to the top of the boundary layer
    if pbot > pe2:
        pbot = pe2
        pcl.blayer = pbot

    
    # Find lowest observation in layer
    lptr = ma.where(pbot > prof.pres)[0].min()
    uptr = ma.where(ptop < prof.pres)[0].max()
    
    # START WITH INTERPOLATED BOTTOM LAYER
    # Begin moist ascent from lifted parcel LCL (pe2, tp2)
    pe1 = pbot
    h1 = interp.hght(prof, pe1)
    te1 = interp.vtmp(prof, pe1)
    tp1 = thermo.wetlift(pe2, tp2, pe1)
    lyre = 0
    lyrlast = 0
    for i in range(lptr, prof.pres.shape[0]):
        if not utils.QC(prof.tmpc[i]): continue
        pe2 = prof.pres[i]
        h2 = prof.hght[i]
        te2 = prof.vtmp[i]
        tp2 = thermo.wetlift(pe1, tp1, pe2)
        tdef1 = (thermo.virtemp(pe1, tp1, tp1) - te1) / thermo.ctok(te1)
        tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / thermo.ctok(te2)
        lyrlast = lyre
        lyre = G * (tdef1 + tdef2) / 2. * (h2 - h1)
        
        # Add layer energy to total positive if lyre > 0
        if lyre > 0: totp += lyre
        # Add layer energy to total negative if lyre < 0, only up to EL
        else:
            if pe2 > 500.: totn += lyre

        tote += lyre
        pelast = pe1
        pe1 = pe2
        h1 = h2
        te1 = te2
        tp1 = tp2
        # Is this the top of the specified layer
        if i >= uptr and not utils.QC(pcl.bplus):
            pe3 = pe1
            h3 = h1
            te3 = te1
            tp3 = tp1
            lyrf = lyre
            if lyrf > 0:
                pcl.bplus = totp - lyrf
                pcl.bminus = totn
            else:
                pcl.bplus = totp
                if pe2 > 500.: pcl.bminus = totn + lyrf
                else: pcl.bminus = totn
            pe2 = ptop
            h2 = interp.hght(prof, pe2)
            te2 = interp.vtmp(prof, pe2)
            tp2 = thermo.wetlift(pe3, tp3, pe2)
            tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / thermo.ctok(te3)
            tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / thermo.ctok(te2)
            lyrf = G * (tdef3 + tdef2) / 2. * (h2 - h3)
            if lyrf > 0: pcl.bplus += lyrf
            else:
                if pe2 > 500.: pcl.bminus += lyrf
            if pcl.bplus == 0: pcl.bminus = 0.
    return pcl

def parcelx(prof, pbot=None, ptop=None, dp=-1, **kwargs):
    '''
        Lifts the specified parcel, calculated various levels and parameters from
        the profile object. B+/B- are calculated based on the specified layer.
        
        !! All calculations use the virtual temperature correction unless noted. !!
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : number (optional; default surface)
        Pressure of the bottom level (hPa)
        ptop : number (optional; default 400 hPa)
        Pressure of the top level (hPa)
        pres : number (optional)
        Pressure of parcel to lift (hPa)
        tmpc : number (optional)
        Temperature of parcel to lift (C)
        dwpc : number (optional)
        Dew Point of parcel to lift (C)
        dp : negative integer (optional; default = -1)
        The pressure increment for the interpolated sounding
        exact : bool (optional; default = False)
        Switch to choose between using the exact data (slower) or using
        interpolated sounding at 'dp' pressure levels (faster)
        flag : number (optional; default = 5)
        Flag to determine what kind of parcel to create; See DefineParcel for
        flag values
        lplvals : lifting parcel layer object (optional)
        Contains the necessary parameters to describe a lifting parcel
        
        Returns
        -------
        pcl : parcel object
        Parcel Object
        
        '''
    flag = kwargs.get('flag', 5)
    pcl = Parcel(pbot=pbot, ptop=ptop)
    pcl.lplvals = kwargs.get('lplvals', DefineParcel(prof, flag))
    if prof.pres.compressed().shape[0] < 1: return pcl
    
    # Variables
    pres = kwargs.get('pres', pcl.lplvals.pres)
    tmpc = kwargs.get('tmpc', pcl.lplvals.tmpc)
    dwpc = kwargs.get('dwpc', pcl.lplvals.dwpc)
    pcl.pres = pres
    pcl.tmpc = tmpc
    pcl.dwpc = dwpc
    ptrace = []
    ttrace = []
    cap_strength = -9999.
    cap_strengthpres = -9999.
    li_max = -9999.
    li_maxpres = -9999.
    totp = 0.
    totn = 0.
    tote = 0.
    cinh_old = 0.
    
    # See if default layer is specified
    if not pbot:
        pbot = prof.pres[prof.sfc]
        pcl.blayer = pbot
        pcl.pbot = pbot
    if not ptop:
        ptop = prof.pres[prof.pres.shape[0]-1]
        pcl.tlayer = ptop
        pcl.ptop = ptop
    
    # Make sure this is a valid layer
    if pbot > pres:
        pbot = pres
        pcl.blayer = pbot
    if type(interp.vtmp(prof, pbot)) == type(ma.masked): return ma.masked
    if type(interp.vtmp(prof, ptop)) == type(ma.masked): return ma.masked
    
    # Begin with the Mixing Layer
    pe1 = pbot
    h1 = interp.hght(prof, pe1)
    tp1 = thermo.virtemp(pres, tmpc, dwpc)
    ttrace.append(tp1)
    ptrace.append(pe1)
    
    # Lift parcel and return LCL pres (hPa) and LCL temp (C)
    pe2, tp2 = thermo.drylift(pres, tmpc, dwpc)
    blupper = pe2
    h2 = interp.hght(prof, pe2)
    te2 = interp.vtmp(prof, pe2)
    pcl.lclpres = pe2
    pcl.lclhght = interp.to_agl(prof, h2)
    ptrace.append(pe2)
    ttrace.append(thermo.virtemp(pe2, tp2, tp2))
    
    # Calculate lifted parcel theta for use in iterative CINH loop below
    # RECALL: lifted parcel theta is CONSTANT from LPL to LCL
    theta_parcel = thermo.theta(pe2, tp2, 1000.)
    
    # Environmental theta and mixing ratio at LPL
    bltheta = thermo.theta(pres, interp.temp(prof, pres), 1000.)
    blmr = thermo.mixratio(pres, dwpc)
    
    # ACCUMULATED CINH IN THE MIXING LAYER BELOW THE LCL
    # This will be done in 'dp' increments and will use the virtual
    # temperature correction where possible
    pp = np.arange(pbot, blupper+dp, dp)
    hh = interp.hght(prof, pp)
    tmp_env_theta = thermo.theta(pp, interp.temp(prof, pp), 1000.)
    tmp_env_dwpt = interp.dwpt(prof, pp)
    tv_env = thermo.virtemp(pp, tmp_env_theta, tmp_env_dwpt)
    tmp1 = thermo.virtemp(pp, theta_parcel, thermo.temp_at_mixrat(blmr, pp))
    tdef = (tmp1 - tv_env) / thermo.ctok(tv_env)
    
    lyre = G * (tdef[:-1]+tdef[1:]) / 2 * (hh[1:]-hh[:-1])
    totn = lyre[lyre < 0].sum()
    if not totn: totn = 0.
    
    # Move the bottom layer to the top of the boundary layer
    if pbot > pe2:
        pbot = pe2
        pcl.blayer = pbot
    
    # Calculate height of various temperature levels
    p0c = temp_lvl(prof, 0.)
    pm10c = temp_lvl(prof, -10.)
    pm20c = temp_lvl(prof, -20.)
    pm30c = temp_lvl(prof, -30.)
    hgt0c = interp.hght(prof, p0c)
    hgtm10c = interp.hght(prof, pm10c)
    hgtm20c = interp.hght(prof, pm20c)
    hgtm30c = interp.hght(prof, pm30c)
    pcl.p0c = p0c
    pcl.pm10c = pm10c
    pcl.pm20c = pm20c
    pcl.pm30c = pm30c
    pcl.hght0c = hgt0c
    pcl.hghtm10c = hgtm10c
    pcl.hghtm20c = hgtm20c
    pcl.hghtm30c = hgtm30c
    
    # Find lowest observation in layer
    lptr = ma.where(pbot > prof.pres)[0].min()
    uptr = ma.where(ptop < prof.pres)[0].max()
    
    # START WITH INTERPOLATED BOTTOM LAYER
    # Begin moist ascent from lifted parcel LCL (pe2, tp2)
    pe1 = pbot
    h1 = interp.hght(prof, pe1)
    te1 = interp.vtmp(prof, pe1)
    tp1 = thermo.wetlift(pe2, tp2, pe1)
    lyre = 0
    lyrlast = 0
    for i in range(lptr, prof.pres.shape[0]):
        if not utils.QC(prof.tmpc[i]): continue
        pe2 = prof.pres[i]
        h2 = prof.hght[i]
        te2 = prof.vtmp[i]
        tp2 = thermo.wetlift(pe1, tp1, pe2)
        tdef1 = (thermo.virtemp(pe1, tp1, tp1) - te1) / thermo.ctok(te1)
        tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / thermo.ctok(te2)
        ptrace.append(pe2)
        ttrace.append(thermo.virtemp(pe2, tp2, tp2))
        lyrlast = lyre
        lyre = G * (tdef1 + tdef2) / 2. * (h2 - h1)
        
        # Add layer energy to total positive if lyre > 0
        if lyre > 0: totp += lyre
        # Add layer energy to total negative if lyre < 0, only up to EL
        else:
            if pe2 > 500.: totn += lyre
        
        # Check for Max LI
        mli = thermo.virtemp(pe2, tp2, tp2) - te2
        if  mli > li_max:
            li_max = mli
            li_maxpres = pe2
        
        # Check for Max Cap Strength
        mcap = te2 - mli
        if mcap > cap_strength:
            cap_strength = mcap
            cap_strengthpres = pe2
        
        tote += lyre
        pelast = pe1
        pe1 = pe2
        h1 = h2
        te1 = te2
        tp1 = tp2
        
        # Is this the top of the specified layer
        if i >= uptr and not utils.QC(pcl.bplus):
            pe3 = pe1
            h3 = h1
            te3 = te1
            tp3 = tp1
            lyrf = lyre
            if lyrf > 0:
                pcl.bplus = totp - lyrf
                pcl.bminus = totn
            else:
                pcl.bplus = totp
                if pe2 > 500.: pcl.bminus = totn + lyrf
                else: pcl.bminus = totn
            pe2 = ptop
            h2 = interp.hght(prof, pe2)
            te2 = interp.vtmp(prof, pe2)
            tp2 = thermo.wetlift(pe3, tp3, pe2)
            tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / thermo.ctok(te3)
            tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / thermo.ctok(te2)
            lyrf = G * (tdef3 + tdef2) / 2. * (h2 - h3)
            if lyrf > 0: pcl.bplus += lyrf
            else:
                if pe2 > 500.: pcl.bminus += lyrf
            if pcl.bplus == 0: pcl.bminus = 0.
        
        # Is this the freezing level
        if te2 < 0. and not utils.QC(pcl.bfzl):
            pe3 = pelast
            h3 = interp.hght(prof, pe3)
            te3 = interp.vtmp(prof, pe3)
            tp3 = thermo.wetlift(pe1, tp1, pe3)
            lyrf = lyre
            if lyrf > 0.: pcl.bfzl = totp - lyrf
            else: pcl.bfzl = totp
            if not utils.QC(p0c) or p0c > pe3:
                pcl.bfzl = 0
            elif utils.QC(pe2):
                te2 = interp.vtmp(prof, pe2)
                tp2 = thermo.wetlift(pe3, tp3, pe2)
                tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                    thermo.ctok(te3)
                tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                    thermo.ctok(te2)
                lyrf = G * (tdef3 + tdef2) / 2. * (hgt0c - h3)
                if lyrf > 0: pcl.bfzl += lyrf
        
        # Is this the -10C level
        if te2 < -10. and not utils.QC(pcl.wm10c):
            pe3 = pelast
            h3 = interp.hght(prof, pe3)
            te3 = interp.vtmp(prof, pe3)
            tp3 = thermo.wetlift(pe1, tp1, pe3)
            lyrf = lyre
            if lyrf > 0.: pcl.wm10c = totp - lyrf
            else: pcl.wm10c = totp
            if not utils.QC(pm10c) or pm10c > pcl.lclpres:
                pcl.wm10c = 0
            elif utils.QC(pe2):
                te2 = interp.vtmp(prof, pe2)
                tp2 = thermo.wetlift(pe3, tp3, pe2)
                tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                    thermo.ctok(te3)
                tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                    thermo.ctok(te2)
                lyrf = G * (tdef3 + tdef2) / 2. * (hgtm10c - h3)
                if lyrf > 0: pcl.wm10c += lyrf
        
        # Is this the -20C level
        if te2 < -20. and not utils.QC(pcl.wm20c):
            pe3 = pelast
            h3 = interp.hght(prof, pe3)
            te3 = interp.vtmp(prof, pe3)
            tp3 = thermo.wetlift(pe1, tp1, pe3)
            lyrf = lyre
            if lyrf > 0.: pcl.wm20c = totp - lyrf
            else: pcl.wm20c = totp
            if not utils.QC(pm20c) or pm20c > pcl.lclpres:
                pcl.wm20c = 0
            elif utils.QC(pe2):
                te2 = interp.vtmp(prof, pe2)
                tp2 = thermo.wetlift(pe3, tp3, pe2)
                tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                    thermo.ctok(te3)
                tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                    thermo.ctok(te2)
                lyrf = G * (tdef3 + tdef2) / 2. * (hgtm20c - h3)
                if lyrf > 0: pcl.wm20c += lyrf
        
        # Is this the -30C level
        if te2 < -30. and not utils.QC(pcl.wm30c):
            pe3 = pelast
            h3 = interp.hght(prof, pe3)
            te3 = interp.vtmp(prof, pe3)
            tp3 = thermo.wetlift(pe1, tp1, pe3)
            lyrf = lyre
            if lyrf > 0.: pcl.wm30c = totp - lyrf
            else: pcl.wm30c = totp
            if not utils.QC(pm30c) or pm30c > pcl.lclpres:
                pcl.wm30c = 0
            elif utils.QC(pe2):
                te2 = interp.vtmp(prof, pe2)
                tp2 = thermo.wetlift(pe3, tp3, pe2)
                tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                    thermo.ctok(te3)
                tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                    thermo.ctok(te2)
                lyrf = G * (tdef3 + tdef2) / 2. * (hgtm30c - h3)
                if lyrf > 0: pcl.wm30c += lyrf
        
        # Is this the 3km level
        if pcl.lclhght < 3000.:
            h = interp.to_agl(prof, interp.hght(prof, pe2))
            if h >= 3000. and not utils.QC(pcl.b3km):
                pe3 = pelast
                h3 = interp.hght(prof, pe3)
                te3 = interp.vtmp(prof, pe3)
                tp3 = thermo.wetlift(pe1, tp1, pe3)
                lyrf = lyre
                if lyrf > 0: pcl.b3km = totp - lyrf
                else: pcl.b3km = totp
                h2 = interp.to_msl(prof, 3000.)
                pe2 = interp.pres(prof, h2)
                if utils.QC(pe2):
                    te2 = interp.vtmp(prof, pe2)
                    tp2 = thermo.wetlift(pe3, tp3, pe2)
                    tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                        thermo.ctok(te3)
                    tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                        thermo.ctok(te2)
                    lyrf = G * (tdef3 + tdef2) / 2. * (h2 - h3)
                    if lyrf > 0: pcl.b3km += lyrf
        else: pcl.b3km = 0.
        
        # Is this the 6km level
        if pcl.lclhght < 6000.:
            h = interp.to_agl(prof, interp.hght(prof, pe2))
            if h >= 6000. and not utils.QC(pcl.b6km):
                pe3 = pelast
                h3 = interp.hght(prof, pe3)
                te3 = interp.vtmp(prof, pe3)
                tp3 = thermo.wetlift(pe1, tp1, pe3)
                lyrf = lyre
                if lyrf > 0: pcl.b6km = totp - lyrf
                else: pcl.b6km = totp
                h2 = interp.to_msl(prof, 6000.)
                pe2 = interp.pres(prof, h2)
                if utils.QC(pe2):
                    te2 = interp.vtmp(prof, pe2)
                    tp2 = thermo.wetlift(pe3, tp3, pe2)
                    tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                        thermo.ctok(te3)
                    tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                        thermo.ctok(te2)
                    lyrf = G * (tdef3 + tdef2) / 2. * (h2 - h3)
                    if lyrf > 0: pcl.b6km += lyrf
        else: pcl.b6km = 0.
        
        # LFC Possibility
        if lyre >= 0. and lyrlast <= 0.:
            tp3 = tp1
            te3 = te1
            pe2 = pe1
            pe3 = pelast
            while interp.vtmp(prof, pe3) > thermo.virtemp(pe3, thermo.wetlift(pe2, tp3, pe3), thermo.wetlift(pe2, tp3, pe3)):
                pe3 -= 5
                pcl.lfcpres = pe3
                pcl.lfchght = interp.to_agl(prof, interp.hght(prof, pe3))
                cinh_old = totn
                tote = 0.
                pcl.elpres = ma.masked
                li_max = -9999.
                if cap_strength < 0.: cap_strength = 0.
                pcl.cap = cap_strength
                pcl.cappres = cap_strengthpres
                # Hack to force LFC to be at least at the LCL
                if pcl.lfcpres > pcl.lclpres:
                    pcl.lfcpres = pcl.lclpres
                    pcl.lfchght = pcl.lclhght
        
        # EL Possibility
        if lyre <= 0. and lyrlast >= 0.:
            tp3 = tp1
            te3 = te1
            pe2 = pe1
            pe3 = pelast
            while interp.vtmp(prof, pe3) < thermo.virtemp(pe3, thermo.wetlift(pe2, tp3, pe3), thermo.wetlift(pe2, tp3, pe3)):
                pe3 -= 5
            pcl.elhght = interp.to_agl(prof, interp.hght(prof, pe3))
            pcl.elpres = pe3
            pcl.mplpres = ma.masked
            pcl.limax = -li_max
            pcl.limaxpres = li_maxpres
        
        # MPL Possibility
        if tote < 0. and not utils.QC(pcl.mplpres) and utils.QC(pcl.elpres):
            pe3 = pelast
            h3 = interp.hght(prof, pe3)
            te3 = interp.vtmp(prof, pe3)
            tp3 = thermo.wetlift(pe1, tp1, pe3)
            totx = tote - lyre
            pe2 = pelast
            while totx > 0:
                pe2 -= 1
                te2 = interp.vtmp(prof, pe2)
                tp2 = thermo.wetlift(pe3, tp3, pe2)
                h2 = interp.hght(prof, pe2)
                tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                    thermo.ctok(te3)
                tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / \
                    thermo.ctok(te2)
                lyrf = G * (tdef3 + tdef2) / 2. * (h2 - h3)
                totx += lyrf
                tp3 = tp2
                te3 = te2
                pe3 = pe2
            pcl.mplpres = pe2
            pcl.mplhght = interp.to_agl(prof, interp.hght(prof, pe2))
        
        # 500 hPa Lifted Index
        if prof.pres[i] <= 500. and not utils.QC(pcl.li5):
            a = interp.vtmp(prof, 500.)
            b = thermo.wetlift(pe1, tp1, 500.)
            pcl.li5 = a - thermo.virtemp(500, b, b)
        
        # 300 hPa Lifted Index
        if prof.pres[i] <= 300. and not utils.QC(pcl.li3):
            a = interp.vtmp(prof, 300.)
            b = thermo.wetlift(pe1, tp1, 300.)
            pcl.li3 = a - thermo.virtemp(300, b, b)
    
#    pcl.bminus = cinh_old
    
    if not utils.QC(pcl.bplus): pcl.bplus = totp
    
    # Calculate BRN if available
    bulk_rich(prof, pcl)
    
    # Save params
    if pcl.bplus == 0: pcl.bminus = 0.
    pcl.ptrace = np.array(ptrace)
    pcl.ttrace = np.array(ttrace)
    return pcl


def bulk_rich(prof, pcl):
    '''
        Calculates the Bulk Richardson Number for a given parcel.
        
        Parameters
        ----------
        prof : profile object
        Profile object
        pcl : parcel object
        Parcel object
        
        Returns
        -------
        Bulk Richardson Number
        
        '''
    # Make sure parcel is initialized
    if not utils.QC(pcl.lplvals):
        pbot = ma.masked
    elif pcl.lplvals.flag > 0 and pcl.lplvals.flag < 4:
        ptop = interp.pres(prof, interp.to_msl(prof, 6000.))
        pbot = prof.pres[prof.sfc]
    else:
        h0 = interp.hght(prof, pcl.pres)
        try:
            pbot = interp.pres(prof, h0-500.)
        except:
            pbot = ma.masked
        if utils.QC(pbot): pbot = prof.pres[prof.sfc]
        h1 = interp.hght(prof, pbot)
        ptop = interp.pres(prof, h1+6000.)
    
    if not utils.QC(pbot) or not utils.QC(ptop):
        pcl.brnshear = ma.masked
        pcl.brn = ma.masked
        pcl.brnu = ma.masked
        pcl.brnv = ma.masked
    #return pcl
    
    # Calculate the lowest 500m mean wind
    p = interp.pres(prof, interp.hght(prof, pbot)+500.)
    mnlu, mnlv = winds.mean_wind(prof, pbot, p)
    
    # Calculate the 6000m mean wind
    mnuu, mnuv = winds.mean_wind(prof, pbot, ptop)
    
    # Make sure CAPE and Shear are available
    if not utils.QC(pcl.bplus) or not utils.QC(mnlu) or not utils.QC(mnuu):
        pcl.brnshear = ma.masked
        pcl.brnu = ma.masked
        pcl.brnv = ma.masked
        pcl.brn = ma.masked
        return pcl
    
    # Calculate shear between levels
    dx = mnuu - mnlu
    dy = mnuv - mnlv
    pcl.brnu = dx
    pcl.brnv = dy
    pcl.brnshear = utils.KTS2MS(utils.mag(dx, dy))
    pcl.brnshear = pcl.brnshear**2 / 2.
    pcl.brn = pcl.bplus / pcl.brnshear
    return pcl


def effective_inflow_layer(prof, ecape=100, ecinh=-250, **kwargs):
    '''
        Calculates the top and bottom of the effective inflow layer based on
        research by Thompson et al. (2004).
        
        Parameters
        ----------
        prof : profile object
        Profile object
        ecape : number (optional; default=100)
        Minimum amount of CAPE in the layer to be considered part of the
        effective inflow layer.
        echine : number (optional; default=250)
        Maximum amount of CINH in the layer to be considered part of the
        effective inflow layer
        mupcl : parcel object
        Most Unstable Layer parcel
        
        Returns
        -------
        pbot : number
        Pressure at the bottom of the layer (hPa)
        ptop : number
        Pressure at the top of the layer (hPa)
        
        '''
    mupcl = kwargs.get('mupcl', None)
    if not mupcl:
        try:
            mupcl = prof.mupcl
        except:
            mulplvals = DefineParcel(prof, flag=3, pres=300)
            mupcl = cape(prof, lplvals=mulplvals)
    mucape = mupcl.bplus
    mucinh = mupcl.bminus
    
    # Scenario where shallow buoyancy present for a parcel with
    # lesser theta near the ground
    mu2lplvals = DefineParcel(prof, 3, pres=300)
    mu2pcl = cape(prof, lplvals=mu2lplvals)
    if mu2pcl.bplus > mucape:
        mucape = mu2pcl.bplus
        mucinh = mu2pcl.bminus
    
    pbot = ma.masked
    ptop = ma.masked
    if mucape >= ecape and mucinh > ecinh:
        # Begin at surface and search upward for effective surface
        for i in range(prof.sfc, prof.top):
            pcl = cape(prof, pres=prof.pres[i], tmpc=prof.tmpc[i], dwpc=prof.dwpc[i])
            if pcl.bplus >= ecape and pcl.bminus > ecinh:
                pbot = prof.pres[i]
                break
        if not utils.QC(pbot): return ma.masked, ma.masked
        bptr = i
        # Keep searching upward for the effective top
        for i in range(bptr+1, prof.top):
            pcl = cape(prof, pres=prof.pres[i], tmpc=prof.tmpc[i], dwpc=prof.dwpc[i])
            if pcl.bplus < ecape or pcl.bminus <= ecinh:
                j = 1
                while not utils.QC(prof.dwpc[i-j]) and \
                    not utils.QC(prof.tmpc[i-j]): j += 1
                ptop = prof.pres[i-j]
                if ptop > pbot: ptop = pbot
                break
    return pbot, ptop


def bunkers_storm_motion(prof, **kwargs):
    '''
        Compute the Bunkers Storm Motion for a right moving supercell using a
        parcel based approach. This code is consistent with the findings in 
        Bunkers et. al 2014, using the Effective Inflow Base as the base, and
        65% of the most unstable parcel equilibrium level height using the 
        pressure weighted mean wind.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        pbot : float (optional)
        Base of effective-inflow layer (hPa)
        mupcl : parcel object (optional)
        Most Unstable Layer parcel
        
        Returns
        -------
        rstu : number
        Right Storm Motion U-component
        rstv : number
        Right Storm Motion V-component
        lstu : number
        Left Storm Motion U-component
        lstv : number
        Left Storm Motion V-component
        
        '''
    d = utils.MS2KTS(7.5)   # Deviation value emperically derived at 7.5 m/s
    mupcl = kwargs.get('mupcl', None)
    pbot = kwargs.get('pbot', None)
    if not mupcl:
        try:
            mupcl = prof.mupcl
        except:
            mulplvals = DefineParcel(prof, flag=3, pres=400)
            mupcl = parcelx(prof, lplvals=mulplvals)
    mucape = mupcl.bplus
    mucinh = mupcl.bminus
    muel = mupcl.elhght
    if not pbot:
        pbot, ptop = effective_inflow_layer(prof, 100, -250, mupcl=mupcl)
    base = interp.to_agl(prof, interp.hght(prof, pbot))
    if mucape > 100. and utils.QC(muel):
        depth = muel - base
        htop = base + ( depth * (65./100.) )
        ptop = interp.pres(prof, interp.to_msl(prof, htop))
        mnu, mnv = winds.mean_wind(prof, pbot, ptop)
        sru, srv = winds.wind_shear(prof, pbot, ptop)
        srmag = utils.mag(sru, srv)
        uchg = d / srmag * srv
        vchg = d / srmag * sru
        rstu = mnu + uchg
        rstv = mnv - vchg
        lstu = mnu - uchg
        lstv = mnv + vchg
    else:
        rstu, rstv, lstu, lstv = winds.non_parcel_bunkers_motion(prof)
    
    return rstu, rstv, lstu, lstv


def convective_temp(prof, **kwargs):
    '''
        Computes the convective temperature, assuming no change in the moisture
        profile. Parcels are iteratively lifted until only mincinh is left as a
        cap. The first guess is the observed surface temperature.
        
        Parameters
        ----------
        prof : profile object
        Profile Object
        mincinh : parcel object (optional; default -1)
        Amount of CINH left at CI
        pres : number (optional)
        Pressure of parcel to lift (hPa)
        tmpc : number (optional)
        Temperature of parcel to lift (C)
        dwpc : number (optional)
        Dew Point of parcel to lift (C)
        
        Returns
        -------
        Convective Temperature (float) in degrees C
        
        '''
    mincinh = kwargs.get('mincinh', -5.)
    mmr = mean_mixratio(prof)
    pres = kwargs.get('pres', prof.pres[prof.sfc])
    tmpc = kwargs.get('tmpc', prof.tmpc[prof.sfc])
    dwpc = kwargs.get('dwpc', thermo.temp_at_mixrat(mmr, pres))
    
    # Do a quick search to fine whether to continue. If you need to heat
    # up more than 25C, don't compute.
    pcl = cape(prof, flag=5, pres=pres, tmpc=tmpc+25., dwpc=dwpc)
    if pcl.bplus == 0. or pcl.bminus < mincinh: return ma.masked
    
    excess = dwpc - tmpc
    if excess > 0: tmpc = tmpc + excess + 4.
    pcl = cape(prof, flag=5, pres=pres, tmpc=tmpc, dwpc=dwpc)
    if pcl.bplus == 0.: pcl.bminus = ma.masked
    while pcl.bminus < mincinh:
        if pcl.bminus < -100: tmpc += 2.
        else: tmpc += 0.5
        pcl = cape(prof, flag=5, pres=pres, tmpc=tmpc, dwpc=dwpc)
        if pcl.bplus == 0.: pcl.bminus = ma.masked
    return tmpc

def tei(prof):
    '''
        Theta-E Index (TEI)
        TEI is the difference between the surface theta-e and the minimum theta-e value
        in the lowest 400 mb AGL
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        tei : theta-e index
        '''
    
    sfc_theta = prof.thetae[prof.sfc]
    sfc_pres = prof.pres[prof.sfc]
    top_pres = sfc_pres - 400.
    
    layer_idxs = ma.where(prof.pres > top_pres)[0]
    min_thetae = ma.min(prof.thetae[layer_idxs])
    
    tei = sfc_theta - min_thetae
    return tei

def esp(prof):
    
    '''
        Enhanced Stretching Potential (ESP)
        This composite parameter identifies areas where low-level buoyancy
        and steep low-level lapse rates are co-located, which may
        favor low-level vortex stretching and tornado potential.
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        esp : ESP index
        '''
    
    mlcape = prof.mlpcl.b3km # This is the 0-3 km MLCAPE!!!!
    lr03 = prof.lapserate_3km # C/km
    if lr03 < 7. or mlcape < 250.:
        return 0
    
    esp = (mlcape / 50.) * ((lr03 - 7.0) / (1.0))
    return esp



def mmp(prof):
    
    '''
        MCS Maintenance Probability (MMP)
        The probability that a mature MCS will maintain peak intensity
        for the next hour.
        
        This equation was developed using proximity soundings and a regression equation
        Uses MUCAPE, 3-8 km lapse rate, maximum bulk shear, 3-12 km mean wind speed
        From Coniglio et. al. 2006 WAF
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        mmp : MMP index (%)
        
        
        this part is confusing...the maximum deep shear value
        
        is the maximum shear vector magnitude (SVM) between any wind vector
        
        in the lowest 1 km and any wind vector in the 6-10 km layer
        
        '''
    lr38 = lapse_rate(prof,3000.,8000.)
    plower = interp.pres(prof, interp.to_msl(prof, 3000.))
    pupper = interp.pres(prof, interp.to_msl(prof, 12000.))
    mean_wind_3t12 = winds.mean_wind( prof, pbot=plower, ptop=pupper)
    mucape = prof.mupcl.bplus
    if mucape < 100:
        return 0.
    
    a_0 = 13.0 # unitless
    a_1 = -4.59*10**-2 # m**-1 * s
    a_2 = -1.16 # K**-1 * km
    a_3 = -6.17*10**-4 # J**-1 * kg
    a_4 = -0.17 # m**-1 * s
    
    mmp = 1. / (1. + np.exp(a_0 + (a_1 * max_bulk_shear) + (a_2 * lr38) + (a_3 * mucape) + (a_4 * mean_wind_3t12)))
    
    return mmp * 100.



def wndg(prof):
    '''
        Wind Damage Parameter (WNDG)
        A non-dimensional composite parameter that identifies areas
        where large CAPE, steep low-level lapse rates,
        enhanced flow in the low-mid levels, and minimal convective
        inhibition are co-located.
        
        WNDG values > 1 favor an enhanced risk for scattered damaging
        outflow gusts with multicell thunderstorm clusters, primarily
        during the afternoon in the summer.
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        wndg : WNDG index
        '''
    
    mlcape = prof.mlpcl.bplus # J/kg
    lr03 = params.lapse_rate( prof, 0, 3000. ) # C/km
    mean_wind = winds.mean_wind(prof, pbot=interp.pres(1000.), ptop=interp.pres(3500.)) # needs to be in m/s
    mlcin = prof.mlpcl.bminus # J/kg
    
    if lr03 < 7:
        lr03 = 0.
    
    if mlcin < -50:
        mlcin = -50.
    wndg = (mlcape / 2000.) * (lr03 / 9.) * (mean_wind / 15.) * ((50. + mlcin)/40.)
    
    return wndg


def sig_severe(prof):
    '''
        Significant Severe (SigSevere)
        Craven and Brooks, 2004
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        sigsevere : significant severe parameter (m3/s3)
        '''
    mlcape = prof.mlpcl.bplus
    shr06 = utils.KTS2MS(prof.sfc_6km_shear)
    
    sigsevere = mlcape * shr06
    return sigsevere

def dcape(prof):
    '''
        Downdraft CAPE (DCAPE)
        Calculates the downdraft CAPE value using the parcel with the lowest Theta-E
        value found in the lowest 400 mb of the sounding.  Lifting this wetbulb parcel to the surface
        moist adiabatically and then calculating the energy is how this is calculated.
        
        Note: this function does not compare well to SPC
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        dcape : downdraft CAPE (J/kg)
        '''
    
    sfc_pres = prof.pres[prof.get_sfc()]
    prof_thetae = prof.thetae
    prof_wetbulb = prof.wetbulb
    idx = np.where(prof.pres > sfc_pres - 400.)[0]
    min_idx = np.ma.argmin(prof_thetae[idx])
    downdraft_t1 = prof_wetbulb[min_idx]
    downdraft_p1 = prof.pres[min_idx]
    downdraft_z1 = prof.hght[min_idx]
    downdraft_td1 = prof.dwpc[min_idx]
    env_tv1 = prof.tmpc[min_idx]
    #downdraft_q = thermo.mixratio(downdraft_p1, downdraft_t1)
    
    dp = 1
    dcape_plus = 0
    dcape_minus = 0
    for downdraft_p2 in np.arange(downdraft_p1, sfc_pres + dp, dp):
        downdraft_t2 = thermo.wetlift(downdraft_p1, downdraft_t1, downdraft_p2)
        downdraft_z2 = interp.hght(prof, downdraft_p2)
        downdraft_td2 = downdraft_t2
        
        env_tv2 = interp.temp(prof, downdraft_p2)
        
        delta_z = downdraft_z2 - downdraft_z1
        g = 9.81 # m/s^2
        
        dn1 = thermo.virtemp(downdraft_p1, downdraft_t1, downdraft_td1)
        dn2 = thermo.virtemp(downdraft_p2, downdraft_t2, downdraft_td2)
        #dn1 = virtemp(downdraft_p1, downdraft_t1, downdraft_q)
        #dn2 = virtemp(downdraft_p2, downdraft_t2, downdraft_q)
        env1 = virtemp(downdraft_p1, env_tv1, interp.dwpt(prof, downdraft_p1))
        env2 = virtemp(downdraft_p2, env_tv2, interp.dwpt(prof, downdraft_p2))
        
        buoyancy_1 = (thermo.ctok(dn1) - thermo.ctok(env1)) / (thermo.ctok(env1))
        buoyancy_2 = (thermo.ctok(dn2) - thermo.ctok(env2)) / (thermo.ctok(env2))
        
        d_dcape = (g * (delta_z/2.) * (buoyancy_1 + buoyancy_2))
        if d_dcape >= 0:
            dcape_plus = dcape_plus + d_dcape
        else:
            dcape_minus = dcape_minus + d_dcape
        env_tv1 = env_tv2
        downdraft_t1 = downdraft_t2
        downdraft_p1 = downdraft_p2
        downdraft_z1 = downdraft_z2
    
    return dcape_plus + dcape_minus

def downrush_temp(prof):
    '''
        Downrush Temperature (DTEMP)
        
        This is the surface temperature of the hypothetical downdraft used in the
        DCAPE calculation.
        
        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        dtemp : downdraft temperature (F)
        '''
    
    sfc_pres = prof.pres[prof.get_sfc()]
    prof_thetae = prof.thetae
    prof_wetbulb = prof.wetbulb
    idx = np.where(prof.pres > sfc_pres - 400.)[0]
    min_idx = np.ma.argmin(prof_thetae[idx])
    downdraft_inital_temp = prof_wetbulb[idx][min_idx]
    downdraft_q = thermo.mixratio(prof.pres[min_idx], downdraft_inital_temp)
    downdraft_inital_temp = thermo.virtemp(prof.pres[min_idx], downdraft_inital_temp, downdraft_q)
    downdraft_t = thermo.wetlift(prof.pres[idx][min_idx], downdraft_inital_temp, sfc_pres)
    
    return thermo.ctof(downdraft_t), prof.pres[min_idx]


