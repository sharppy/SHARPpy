''' Thermodynamic Parameter Routines '''
from __future__ import division
import numpy as np
import numpy.ma as ma
from sharppy.sharptab import interp, utils, thermo, winds
from sharppy.sharptab.constants import *


__all__ = ['DefineParcel', 'Parcel', 'inferred_temp_advection']
__all__ += ['k_index', 't_totals', 'c_totals', 'v_totals', 'precip_water']
__all__ += ['temp_lvl', 'max_temp', 'mean_mixratio', 'mean_theta', 'mean_thetae', 'mean_relh']
__all__ += ['lapse_rate', 'most_unstable_level', 'parcelx', 'bulk_rich']
__all__ += ['bunkers_storm_motion', 'effective_inflow_layer']
__all__ += ['convective_temp', 'esp', 'pbl_top', 'precip_eff', 'dcape', 'sig_severe']
__all__ += ['dgz', 'ship', 'stp_cin', 'stp_fixed', 'scp', 'mmp', 'wndg', 'sherb', 'tei', 'cape']
__all__ += ['mburst', 'dcp', 'ehi', 'sweat', 'hgz', 'lhp']


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
            self.presval = kwargs.get('pres', prof.pres[prof.sfc])
            self.__user(prof, **kwargs)
        elif flag == 6:
            self.presval = kwargs.get('pres', 100)
            self.__effective(prof, **kwargs)
        else:
            #print 'Defaulting to Surface Parcel'
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
        pbot = self.pres; ptop = self.pres - 100.
        self.dwpc = thermo.temp_at_mixrat(mean_mixratio(prof, pbot, ptop, exact=True), self.pres)
    
    
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

            If
            
            '''
        self.desc = '%.2f hPa Mixed Layer Parcel' % self.presval
        pbot = kwargs.get('pbot', prof.pres[prof.sfc])
        ptop = pbot - self.presval
        self.pres = pbot
        mtheta = mean_theta(prof, pbot, ptop, exact=True)
        self.tmpc = thermo.theta(1000., mtheta, self.pres)
        mmr = mean_mixratio(prof, pbot, ptop, exact=True)
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
        self.pres = ma.masked # Parcel beginning pressure (mb)
        self.tmpc = ma.masked # Parcel beginning temperature (C)
        self.dwpc = ma.masked # Parcel beginning dewpoint (C)
        self.ptrace = ma.masked # Parcel trace pressure (mb)
        self.ttrace = ma.masked # Parcel trace temperature (C)
        self.blayer = ma.masked # Pressure of the bottom of the layer the parcel is lifted (mb)
        self.tlayer = ma.masked # Pressure of the top of the layer the parcel is lifted (mb)
        self.entrain = 0. # A parcel entrainment setting (not yet implemented)
        self.lclpres = ma.masked # Parcel LCL (lifted condensation level) pressure (mb)
        self.lclhght = ma.masked # Parcel LCL height (m AGL)
        self.lfcpres = ma.masked # Parcel LFC (level of free convection) pressure (mb)
        self.lfchght = ma.masked # Parcel LFC height (m AGL)
        self.elpres = ma.masked # Parcel EL (equilibrium level) pressure (mb)
        self.elhght = ma.masked # Parcel EL height (m AGL)
        self.mplpres = ma.masked # Maximum Parcel Level (mb)
        self.mplhght = ma.masked # Maximum Parcel Level (m AGL)
        self.bplus = ma.masked # Parcel CAPE (J/kg)
        self.bminus = ma.masked # Parcel CIN (J/kg)
        self.bfzl = ma.masked # Parcel CAPE up to freezing level (J/kg)
        self.b3km = ma.masked # Parcel CAPE up to 3 km (J/kg)
        self.b6km = ma.masked # Parcel CAPE up to 6 km (J/kg)
        self.p0c = ma.masked # Pressure value at 0 C  (mb)
        self.pm10c = ma.masked # Pressure value at -10 C (mb)
        self.pm20c = ma.masked # Pressure value at -20 C (mb)
        self.pm30c = ma.masked # Pressure value at -30 C (mb)
        self.hght0c = ma.masked # Height value at 0 C (m AGL)
        self.hghtm10c = ma.masked # Height value at -10 C (m AGL)
        self.hghtm20c = ma.masked # Height value at -20 C (m AGL)
        self.hghtm30c = ma.masked # Height value at -30 C (m AGL)
        self.wm10c = ma.masked # w velocity at -10 C ?
        self.wm20c = ma.masked # w velocity at -20 C ?
        self.wm30c = ma.masked # Wet bulb at -30 C ? 
        self.li5 = ma.masked # Lifted Index at 500 mb (C)
        self.li3 = ma.masked # Lifted Index at 300 mb (C)
        self.brnshear = ma.masked # Bulk Richardson Number Shear
        self.brnu = ma.masked # Bulk Richardson Number U (kts)
        self.brnv = ma.masked # Bulk Richardson Number V (kts)
        self.brn = ma.masked # Bulk Richardson Number (unitless)
        self.limax = ma.masked # Maximum Lifted Index (C)
        self.limaxpres = ma.masked # Pressure at Maximum Lifted Index (mb)
        self.cap = ma.masked # Cap Strength (C)
        self.cappres = ma.masked # Cap strength pressure (mb)
        self.bmin = ma.masked # Buoyancy minimum in profile (C)
        self.bminpres = ma.masked # Buoyancy minimum pressure (mb)
        for kw in kwargs: setattr(self, kw, kwargs.get(kw))

def hgz(prof):
    '''
        Hail Growth Zone Levels
    
        This function finds the pressure levels for the dendritic 
        growth zone (from -10 C to -30 C).  If either temperature cannot be found,
        it is set to be the surface pressure.

        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        pbot : number
        Pressure of the bottom level (mb)
        ptop : number 
        Pressure of the top level (mb)
    '''

    pbot = temp_lvl(prof, -10)
    ptop = temp_lvl(prof, -30)

    if not utils.QC(pbot):
        pbot = prof.pres[prof.sfc]
    if not utils.QC(ptop):
        ptop = prof.pres[prof.sfc]

    return pbot, ptop


def dgz(prof):
    '''
        Dendritic Growth Zone Levels
    
        This function finds the pressure levels for the dendritic 
        growth zone (from -12 C to -17 C).  If either temperature cannot be found,
        it is set to be the surface pressure.

        Parameters
        ----------
        prof : profile object
        Profile Object
        
        Returns
        -------
        pbot : number
        Pressure of the bottom level (mb)
        ptop : number 
        Pressure of the top level (mb)
    '''

    pbot = temp_lvl(prof, -12)
    ptop = temp_lvl(prof, -17)

    if not utils.QC(pbot):
        pbot = prof.pres[prof.sfc]
    if not utils.QC(ptop):
        ptop = prof.pres[prof.sfc]

    return pbot, ptop

def lhp(prof):
    '''
        Large Hail Parameter

        From Johnson and Sugden (2014), EJSSM

        Parameters
        ----------
        prof : profile object
            ConvectiveProfile object

        Returns
        -------
        lhp : number
            large hail parameter (unitless)
    '''

    mag06_shr = utils.KTS2MS(utils.mag(*prof.sfc_6km_shear))

    if prof.mupcl.bplus >= 400 and mag06_shr >= 14:
        lr75 = prof.lapserate_700_500
        zbot, ztop = interp.hght(prof, hgz(prof))
        thk_hgz = ztop - zbot

        term_a = (((prof.mupcl.bplus - 2000.)/1000.) +\
                 ((3200 - thk_hgz)/500.) +\
                 ((lr75 - 6.5)/2.))

        if term_a < 0:
            term_a = 0

        p_1km, p_3km, p_6km = interp.pres(prof, interp.to_msl(prof, [1000, 3000, 6000]))
        shear_el = utils.KTS2MS(utils.mag(*winds.wind_shear(prof, pbot=prof.pres[prof.sfc], ptop=prof.mupcl.elpres)))
        grw_el_dir = interp.vec(prof, prof.mupcl.elpres)[0]
        grw_36_dir = utils.comp2vec(*winds.mean_wind(prof, pbot=p_3km, ptop=p_6km))[0]
        grw_alpha_el = grw_el_dir - grw_36_dir

        if grw_alpha_el > 180:
            grw_alpha_el = -10

        srw_01_dir = utils.comp2vec(*winds.sr_wind(prof, pbot=prof.pres[prof.sfc], ptop=p_1km, stu=prof.srwind[0], stv=prof.srwind[1]))[0]
        srw_36_dir = utils.comp2vec(*winds.sr_wind(prof, pbot=p_3km, ptop=p_6km, stu=prof.srwind[0], stv=prof.srwind[1]))[0]
        srw_alpha_mid = srw_36_dir - srw_01_dir

        term_b = (((shear_el - 25.)/5.) +\
                  ((grw_alpha_el + 5.)/20.) +\
                  ((srw_alpha_mid - 80.)/10.))
        if term_b < 0:
            term_b = 0

        lhp = term_a * term_b + 5

    else:
        lhp = 0

    return lhp


def ship(prof, **kwargs):
    '''
        Calculate the Sig Hail Parameter (SHIP)

        Parameters
        ----------
        prof : Profile object
        mupcl : (optional) Most-Unstable Parcel
        lr75 : (optional) 700 - 500 mb lapse rate (C/km)
        h5_temp : (optional) 500 mb temperature (C)
        shr06 : (optional) 0-6 km shear (m/s)
        frz_lvl : (optional) freezing level (m)

        Returns
        -------
        ship : number
            significant hail parameter (unitless)

        Ryan Jewell (SPC) helped in correcting this equation as the SPC
        sounding help page version did not have the correct information
        of how SHIP was calculated.

        The significant hail parameter (SHIP; SPC 2014) is
        an index developed in-house at the SPC. (Johnson and Sugden 2014)
    '''
      
    mupcl = kwargs.get('mupcl', None)
    sfc6shr = kwargs.get('sfc6shr', None)
    frz_lvl = kwargs.get('frz_lvl', None)
    h5_temp = kwargs.get('h5_temp', None)
    lr75 = kwargs.get('lr75', None)

    if not mupcl:
        try:
            mupcl = prof.mupcl
        except:
            mulplvals = DefineParcel(prof, flag=3, pres=300)
            mupcl = cape(prof, lplvals=mulplvals)
    mucape = mupcl.bplus
    mumr = thermo.mixratio(mupcl.pres, mupcl.dwpc)

    if not frz_lvl:
        frz_lvl = interp.hght(prof, temp_lvl(prof, 0))

    if not h5_temp:
        h5_temp = interp.temp(prof, 500.)

    if not lr75:
        lr75 = lapse_rate(prof, 700., 500., pres=True)

    if not sfc6shr:
        try:
            sfc_6km_shear = prof.sfc_6km_shear
        except:
            sfc = prof.pres[prof.sfc]
            p6km = interp.pres(prof, interp.to_msl(prof, 6000.))
            sfc_6km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p6km)
    
    sfc_6km_shear = utils.mag(sfc_6km_shear[0], sfc_6km_shear[1])
    shr06 = utils.KTS2MS(sfc_6km_shear)
    
    if shr06 > 27:
        shr06 = 27.
    elif shr06 < 7:
        shr06 = 7.

    if mumr > 13.6:
        mumr = 13.6
    elif mumr < 11.:
        mumr = 11.

    if h5_temp > -5.5:
        h5_temp = -5.5

    ship = -1. * (mucape * mumr * lr75 * h5_temp * shr06) / 42000000.
    
    if mucape < 1300:
        ship = ship*(mucape/1300.)
    
    if lr75 < 5.8:
        ship = ship*(lr75/5.8)

    if frz_lvl < 2400:
        ship = ship * (frz_lvl/2400.)
    
    return ship

def stp_cin(mlcape, esrh, ebwd, mllcl, mlcinh):
    '''
        Significant Tornado Parameter (w/CIN)

        From Thompson et al. 2012 WAF, page 1139

        Parameters
        ----------
        mlcape : Mixed-layer CAPE from the parcel class (J/kg)
        esrh : effective storm relative helicity (m2/s2)
        ebwd : effective bulk wind difference (m/s)
        mllcl : mixed-layer lifted condensation level (m)
        mlcinh : mixed-layer convective inhibition (J/kg)

        Returns
        -------
        stp_cin : number
            significant tornado parameter (unitless)

    '''
    cape_term = mlcape / 1500.
    eshr_term = esrh / 150.
    
    if ebwd < 12.5:
        ebwd_term = 0.
    elif ebwd > 30.:
        ebwd_term = 1.5
    else:
        ebwd_term  = ebwd / 20.

    if mllcl < 1000.:
        lcl_term = 1.0
    elif mllcl > 2000.:
        lcl_term = 0.0
    else:
        lcl_term = ((2000. - mllcl) / 1000.)

    if mlcinh > -50:
        cinh_term = 1.0
    elif mlcinh < -200:
        cinh_term = 0
    else:
        cinh_term = ((mlcinh + 200.) / 150.)

    stp_cin = cape_term * eshr_term * ebwd_term * lcl_term * cinh_term
    if stp_cin is np.ma.masked or stp_cin < 0:
        stp_cin = 0.0

    return stp_cin



def stp_fixed(sbcape, sblcl, srh01, bwd6):
    '''
        Significant Tornado Parameter (fixed layer)
   
        From Thompson et al. 2003

        Parameters
        ----------
        sbcape : Surface based CAPE from the parcel class (J/kg)
        sblcl : Surface based lifted condensation level (LCL) (m)
        srh01 : Surface to 1 km storm relative helicity (m2/s2)
        bwd6 : Bulk wind difference between 0 to 6 km (m/s)

        Returns
        -------
        stp_fixed : number
            signifcant tornado parameter (fixed-layer)
    '''
    
    # Calculate SBLCL term
    if sblcl < 1000.: # less than 1000. meters
        lcl_term = 1.0
    elif sblcl > 2000.: # greater than 2000. meters
        lcl_term = 0.0
    else:
        lcl_term = ((2000.-sblcl)/1000.)

    # Calculate 6BWD term
    if bwd6 > 30.: # greater than 30 m/s
        bwd6 = 30
    elif bwd6 < 12.5:
        bwd6 = 0.0
    
    bwd6_term = bwd6 / 20.

    cape_term = sbcape / 1500.
    srh_term = srh01 / 150.

    stp_fixed = cape_term * lcl_term * srh_term * bwd6_term
   
    return stp_fixed



def scp(mucape, srh, ebwd):
    '''
        Supercell Composite Parameter

        From Thompson et al. 2004

        Parameters
        ----------
        prof : Profile object
        mucape : Most Unstable CAPE from the parcel class (J/kg) (optional)
        srh : the effective SRH from the winds.helicity function (m2/s2)
        ebwd : effective bulk wind difference (m/s)

        Returns
        -------
        scp : number
            supercell composite parameter
    
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
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        dwpt = interp.dwpt(prof, p)
    w = thermo.mixratio(p, dwpt)
    return (((w[:-1]+w[1:])/2 * (p[:-1]-p[1:])) * 0.00040173).sum()


def inferred_temp_adv(prof, lat=35):
    '''
        Inferred Temperature Advection

        SHARP code deduced by Greg Blumberg.  Not based on actual SPC code.

        Calculates the inferred temperature advection from the surface pressure
        and up every 100 mb assuming all winds are geostrophic.  The units returned are
        in C/hr.  If no latitude is specified the function defaults to 35 degrees North.

        This function doesn't compare well to SPC in terms of magnitude of the results.  The direction
        and relative magnitude I think I've got right. My calculations seem to be consistently less
        than those seen on the SPC website.  Although, this function may be right as the SPC values seem
        a little high for typical synoptic scale geostrophic temperature advection (10 Kelvin/day is typical).

        This code uses Equation 4.1.139 from Bluestein's Synoptic book (Volume 1)

        Parameters
        ----------
        prof : Profile object
        lat : latitude in decimal degrees (optional)

        Returns
        -------
        temp_adv : an array of temperature advection values in C/hr
        pressure_bounds: a 2D array indicating the top and bottom bounds of the temperature advection layers.
    '''

    omega = (2. * np.pi) / (86164.)
    f = 2. * omega * np.sin(np.radians(lat)) # Units: (s**-1)
    multiplier = (f / 9.81) * (np.pi / 180.) # Units: (s**-1 / (m/s**2)) * (radians/degrees)

    dp = -100
    pres_idx = np.where(prof.pres >= 100.)[0]
    pressures = np.arange(prof.pres[prof.get_sfc()], prof.pres[pres_idx][-1], dp, dtype=type(prof.pres[prof.get_sfc()])) # Units: mb
    temps = thermo.ctok(interp.temp(prof, pressures))
    heights = interp.hght(prof, pressures)
    temp_adv = np.empty(len(pressures) - 1)
    dirs = interp.vec(prof, pressures)[0]
    pressure_bounds = np.empty((len(pressures) - 1, 2))
    for i in xrange(1, len(pressures)):
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

    return np.power(10, np.interp(temp, [prof.tmpc[ind+1], prof.tmpc[ind]],
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
    temp = thermo.ctok(interp.temp(prof, mixlayer)) + 2
    return thermo.ktoc(temp * (prof.pres[prof.sfc] / mixlayer)**ROCP)


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
        Mean Relative Humidity
        
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
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        tmp = interp.temp(prof, p)
        dwpt = interp.dwpt(prof, p)
    rh = thermo.relh(p, tmp, dwpt)
    return ma.average(rh, weights=p)

def mean_omega(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Calculates the mean omega from a profile object within the
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
        Mean Omega
        
        '''
    if hasattr(prof, 'omeg'): 
        if prof.omeg.all() is np.ma.masked:
            return prof.missing
    else:
        return prof.missing
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 100.
    if not utils.QC(interp.omeg(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.omeg(prof, ptop)): return ma.masked
    if exact:
        # This condition of the if statement is not tested
        omeg = prof.omeg
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        omeg1 = interp.omeg(prof, pbot)
        omeg2 = interp.omeg(prof, ptop)
        omeg = omeg[ind1:ind2+1]
        mask = ~omeg.mask
        omeg = np.concatenate([[omeg1], omeg[mask], omeg[mask], [omeg2]])
        tott = omeg.sum() / 2.
        num = float(len(omeg)) / 2.
        thta = tott / num
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        omeg = interp.omeg(prof, p)
        omeg = ma.average(omeg, weights=p)
    return omeg

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
        dwpt = np.concatenate([[dwpt1], prof.dwpc[ind1:ind2+1][mask], prof.dwpc[ind1:ind2+1][mask], [dwpt2]])
        p = np.concatenate([[pbot], prof.pres[ind1:ind2+1][mask],prof.pres[ind1:ind2+1][mask], [ptop]])
        totd = dwpt.sum() / 2.
        totp = p.sum() / 2.
        num = float(len(dwpt)) / 2.
        w = thermo.mixratio(totp/num, totd/num)
    
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        dwpt = interp.dwpt(prof, p)
        w = ma.average(thermo.mixratio(p, dwpt))
    return w

def mean_thetae(prof, pbot=None, ptop=None, dp=-1, exact=False):
    '''
        Calculates the mean theta-e from a profile object within the
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
        Mean Theta-E
        
        '''
    if not pbot: pbot = prof.pres[prof.sfc]
    if not ptop: ptop = prof.pres[prof.sfc] - 100.
    if not utils.QC(interp.temp(prof, pbot)): pbot = prof.pres[prof.sfc]
    if not utils.QC(interp.temp(prof, ptop)): return ma.masked
    if exact:
        ind1 = np.where(pbot > prof.pres)[0].min()
        ind2 = np.where(ptop < prof.pres)[0].max()
        thetae1 = thermo.thetae(pbot, interp.temp(prof, pbot), interp.dwpt(prof, pbot))
        thetae2 = thermo.thetae(ptop, interp.temp(prof, ptop), interp.dwpt(prof, pbot))
        thetae = np.ma.empty(prof.pres[ind1:ind2+1].shape)
        for i in np.arange(0, len(thetae), 1):
            thetae[i] = thermo.thetae(prof.pres[ind1:ind2+1][i],  prof.tmpc[ind1:ind2+1][i], prof.dwpc[ind1:ind2+1][i])
        mask = ~thetae.mask
        thetae = np.concatenate([[thetae1], thetae[mask], thetae[mask], [thetae2]])
        tott = thetae.sum() / 2.
        num = float(len(thetae)) / 2.
        thtae = tott / num
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        #temp = interp.temp(prof, p)
        #dwpt = interp.dwpt(prof, p)
        #thetae = np.empty(p.shape)
        #for i in np.arange(0, len(thetae), 1):
        #   thetae[i] = thermo.thetae(p[i], temp[i], dwpt[i])
        thetae = interp.thetae(prof, p)
        thtae = ma.average(thetae, weights=p)
    return thtae

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
        theta1 = thermo.theta(pbot, interp.temp(prof, pbot))
        theta2 = thermo.theta(ptop, interp.temp(prof, ptop))
        theta = thermo.theta(prof.pres[ind1:ind2+1],  prof.tmpc[ind1:ind2+1])
        mask = ~theta.mask
        theta = np.concatenate([[theta1], theta[mask], theta[mask], [theta2]])
        tott = theta.sum() / 2.
        num = float(len(theta)) / 2.
        thta = tott / num
    else:
        dp = -1
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        temp = interp.temp(prof, p)
        theta = thermo.theta(p, temp)
        thta = ma.average(theta, weights=p)
    return thta


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
        p = np.arange(pbot, ptop+dp, dp, dtype=type(pbot))
        t = interp.temp(prof, p)
        d = interp.dwpt(prof, p)
    p2, t2 = thermo.drylift(p, t, d)
    mt = thermo.wetlift(p2, t2, 1000.) # Essentially this is making the Theta-E profile, which we are already doing in the Profile object!
    ind = np.where(np.fabs(mt - np.nanmax(mt)) < TOL)[0]
    return p[ind[0]]

def parcelTraj(prof, parcel, smu=None, smv=None):
    '''
        Parcel Trajectory Routine (Storm Slinky)
        Coded by Greg Blumberg

        This routine is a simple 3D thermodynamic parcel trajectory model that
        takes a thermodynamic profile and a parcel trace and computes the
        trajectory of a parcel that is lifted to its LFC, then given a 5 m/s
        nudge upwards, and then left to accelerate up to the EL.  (Based on a description
        in the AWIPS 2 Online Training.)
        
        This parcel is assumed to be moving horizontally via the storm motion vector, which
        if not supplied is taken to be the Bunkers Right Mover storm motion vector.
        As the parcel accelerates upwards, it is advected by the storm relative winds.
        The environmental winds are assumed to be steady-state.
        
        This simulates the path a parcel in a storm updraft would take using pure parcel theory.
        
        Parameters
        ----------
        prof : Profile object
        parcel : parcel object
        smu: optional (storm motion vector u)
        smv: optional (storm motion vector v)
        
        Returns
        -------
        pos_vector : a list of tuples, where each element of the list is a location of the parcel in time
        theta : the tilt of the updraft measured by the angle of the updraft with respect to the horizon
        '''
    
    t_parcel = parcel.ttrace # temperature
    p_parcel = parcel.ptrace # mb
    elhght = parcel.elhght # meter
    elpres = parcel.elpres # meter
    
    y_0 = 0 # meter
    x_0 = 0 # meter
    z_0 = parcel.lfchght # meter
    p_0 = parcel.lfcpres # meter
    
    g = 9.8 # m/s**2
    t_0 = 0 # seconds
    w_0 = 5 # m/s (the initial parcel nudge)
    u_0 = 0 # m/s
    v_0 = 0 # m/s (initial parcel location, which is storm motion relative)
    
    delta_t = 25 # the trajectory increment
    pos_vector = [(x_0,y_0,z_0)]
    speed_vector = [(u_0, v_0, w_0)]
    
    if smu==None or smv==None:
        smu = prof.srwind[0] # Expected to be in knots
        smv = prof.srwind[1] # Is expected to be in knots

    if z_0 > elhght:
        # The parcel doesn't have any positively buoyant areas.
        return

    while z_0 < elhght:
        t_1 = delta_t + t_0 # the time step increment
        
        # Compute the vertical acceleration
        env_tempv = interp.vtmp(prof, p_0) + 273.15
        pcl_tempv = interp.generic_interp_pres(np.log10(p_0), np.log10(p_parcel.copy())[::-1], t_parcel[::-1]) + 273.15
        accel = g * ((pcl_tempv - env_tempv) / env_tempv)
        
        # Compute the vertical displacement
        z_1 = (.5 * accel * np.power(t_1 - t_0, 2)) + (w_0 * (t_1 - t_0)) + z_0
        w_1 = accel * (t_1 - t_0) + w_0
        
        # Compute the parcel-relative winds
        u, v = interp.components(prof, p_0)
        u_0 = utils.KTS2MS(u - smu)
        v_0 = utils.KTS2MS(v - smv)
        
        # Compute the horizontal displacements
        x_1 = u_0 * (t_1 - t_0) + x_0
        y_1 = v_0 * (t_1 - t_0) + y_0
        
        pos_vector.append((x_1, y_1, z_1))
        speed_vector.append((u_0, v_0, w_1))
        
        # Update parcel position
        z_0 = z_1
        y_0 = y_1
        x_0 = x_1
        t_0 = t_1
        p_0 = interp.pres(prof, interp.to_msl(prof, z_1))
        
        # Update parcel vertical velocity
        w_0 = w_1
    
    # Compute the angle tilt of the updraft
    r = np.sqrt(np.power(pos_vector[-1][0], 2) + np.power(pos_vector[-1][1], 2))
    theta = np.degrees(np.arctan2(pos_vector[-1][2],r))
    return pos_vector, theta

def cape(prof, pbot=None, ptop=None, dp=-1, **kwargs):
    '''        
        Lifts the specified parcel, calculates various levels and parameters from
        the profile object. Only B+/B- are calculated based on the specified layer. 
        
        This is a convenience function for effective_inflow_layer and convective_temp, 
        as well as any function that needs to lift a parcel in an iterative process.
        This function is a stripped back version of the parcelx function, that only
        handles bplus and bminus. The intention is to reduce the computation time in
        the iterative functions by reducing the calculations needed.

        This method of creating a stripped down parcelx function for CAPE/CIN calculations
        was developed by Greg Blumberg and Kelton Halbert and later implemented in
        SPC's version of SHARP to speed up their program.
        
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
    pp = np.arange(pbot, blupper+dp, dp, dtype=type(pbot))
    hh = interp.hght(prof, pp)
    tmp_env_theta = thermo.theta(pp, interp.temp(prof, pp), 1000.)
    tmp_env_dwpt = interp.dwpt(prof, pp)
    tv_env = thermo.virtemp(pp, tmp_env_theta, tmp_env_dwpt)
    tmp1 = thermo.virtemp(pp, theta_parcel, thermo.temp_at_mixrat(blmr, pp))
    tdef = (tmp1 - tv_env) / thermo.ctok(tv_env)

    tidx1 = np.arange(0, len(tdef)-1, 1)
    tidx2 = np.arange(1, len(tdef), 1)
    lyre = G * (tdef[tidx1]+tdef[tidx2]) / 2 * (hh[tidx2]-hh[tidx1])
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
    for i in xrange(lptr, prof.pres.shape[0]):
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
    ttrace = [tp1]
    ptrace = [pe1]
    
    # Lift parcel and return LCL pres (hPa) and LCL temp (C)
    pe2, tp2 = thermo.drylift(pres, tmpc, dwpc)
    blupper = pe2
    h2 = interp.hght(prof, pe2)
    te2 = interp.vtmp(prof, pe2)
    pcl.lclpres = min(pe2, prof.pres[prof.sfc]) # Make sure the LCL pressure is
                                                # never below the surface
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
    pp = np.arange(pbot, blupper+dp, dp, dtype=type(pbot))
    hh = interp.hght(prof, pp)
    tmp_env_theta = thermo.theta(pp, interp.temp(prof, pp), 1000.)
    tmp_env_dwpt = interp.dwpt(prof, pp)
    tv_env = thermo.virtemp(pp, tmp_env_theta, tmp_env_dwpt)
    tmp1 = thermo.virtemp(pp, theta_parcel, thermo.temp_at_mixrat(blmr, pp))
    tdef = (tmp1 - tv_env) / thermo.ctok(tv_env)


    tidx1 = np.arange(0, len(tdef)-1, 1)
    tidx2 = np.arange(1, len(tdef), 1)
    lyre = G * (tdef[tidx1]+tdef[tidx2]) / 2 * (hh[tidx2]-hh[tidx1])
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
    lptr = ma.where(pbot >= prof.pres)[0].min()
    uptr = ma.where(ptop <= prof.pres)[0].max()
    
    # START WITH INTERPOLATED BOTTOM LAYER
    # Begin moist ascent from lifted parcel LCL (pe2, tp2)
    pe1 = pbot
    h1 = interp.hght(prof, pe1)
    te1 = interp.vtmp(prof, pe1)
    tp1 = thermo.wetlift(pe2, tp2, pe1)
    lyre = 0
    lyrlast = 0


    iter_ranges = np.arange(lptr, prof.pres.shape[0])
    ttraces = ma.zeros(len(iter_ranges))
    ptraces = ma.zeros(len(iter_ranges))
    ttraces[:] = ptraces[:] = ma.masked

    for i in iter_ranges:
        if not utils.QC(prof.tmpc[i]): continue
        pe2 = prof.pres[i]
        h2 = prof.hght[i]
        te2 = prof.vtmp[i]
        #te2 = thermo.virtemp(prof.pres[i], prof.tmpc[i], prof.dwpc[i])
        tp2 = thermo.wetlift(pe1, tp1, pe2)
        tdef1 = (thermo.virtemp(pe1, tp1, tp1) - te1) / thermo.ctok(te1)
        tdef2 = (thermo.virtemp(pe2, tp2, tp2) - te2) / thermo.ctok(te2)

        ptraces[i-iter_ranges[0]] = pe2
        ttraces[i-iter_ranges[0]] = thermo.virtemp(pe2, tp2, tp2)
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
        te1 = te2
        tp1 = tp2
        
        # Is this the top of the specified layer
        if i >= uptr and not utils.QC(pcl.bplus):
            pe3 = pe1
            h3 = h2
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
            if interp.to_agl(prof, h1) <=3000. and interp.to_agl(prof, h2) >= 3000. and not utils.QC(pcl.b3km):
                pe3 = pelast
                h3 = interp.hght(prof, pe3)
                te3 = interp.vtmp(prof, pe3)
                tp3 = thermo.wetlift(pe1, tp1, pe3)
                lyrf = lyre
                if lyrf > 0: pcl.b3km = totp - lyrf
                else: pcl.b3km = totp
                h4 = interp.to_msl(prof, 3000.)
                pe4 = interp.pres(prof, h4)
                if utils.QC(pe2):
                    te2 = interp.vtmp(prof, pe4)
                    tp2 = thermo.wetlift(pe3, tp3, pe4)
                    tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                        thermo.ctok(te3)
                    tdef2 = (thermo.virtemp(pe4, tp2, tp2) - te2) / \
                        thermo.ctok(te2)
                    lyrf = G * (tdef3 + tdef2) / 2. * (h4 - h3)
                    if lyrf > 0: pcl.b3km += lyrf
        else: pcl.b3km = 0.
        
        # Is this the 6km level
        if pcl.lclhght < 6000.:
            if interp.to_agl(prof, h1) <=6000. and interp.to_agl(prof, h2) >= 6000. and not utils.QC(pcl.b6km):
                pe3 = pelast
                h3 = interp.hght(prof, pe3)
                te3 = interp.vtmp(prof, pe3)
                tp3 = thermo.wetlift(pe1, tp1, pe3)
                lyrf = lyre
                if lyrf > 0: pcl.b6km = totp - lyrf
                else: pcl.b6km = totp
                h4 = interp.to_msl(prof, 6000.)
                pe4 = interp.pres(prof, h4)
                if utils.QC(pe2):
                    te2 = interp.vtmp(prof, pe4)
                    tp2 = thermo.wetlift(pe3, tp3, pe4)
                    tdef3 = (thermo.virtemp(pe3, tp3, tp3) - te3) / \
                        thermo.ctok(te3)
                    tdef2 = (thermo.virtemp(pe4, tp2, tp2) - te2) / \
                        thermo.ctok(te2)
                    lyrf = G * (tdef3 + tdef2) / 2. * (h4 - h3)
                    if lyrf > 0: pcl.b6km += lyrf
        else: pcl.b6km = 0.
        
        h1 = h2

        # LFC Possibility
        if lyre >= 0. and lyrlast <= 0.:
            tp3 = tp1
            #te3 = te1
            pe2 = pe1
            pe3 = pelast
            if interp.vtmp(prof, pe3) < thermo.virtemp(pe3, thermo.wetlift(pe2, tp3, pe3), thermo.wetlift(pe2, tp3, pe3)):
                pcl.lfcpres = pe3
                pcl.lfchght = interp.to_agl(prof, interp.hght(prof, pe3))
            else:
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
            if pcl.lfcpres >= pcl.lclpres:
                pcl.lfcpres = pcl.lclpres
                pcl.lfchght = pcl.lclhght
        
        # EL Possibility
        if lyre <= 0. and lyrlast >= 0.:
            tp3 = tp1
            #te3 = te1
            pe2 = pe1
            pe3 = pelast
            while interp.vtmp(prof, pe3) < thermo.virtemp(pe3, thermo.wetlift(pe2, tp3, pe3), thermo.wetlift(pe2, tp3, pe3)):
                pe3 -= 5
            pcl.elpres = pe3
            pcl.elhght = interp.to_agl(prof, interp.hght(prof, pcl.elpres))
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
    if np.floor(pcl.bplus) == 0: pcl.bminus = 0.
    pcl.ptrace = ma.concatenate((ptrace, ptraces))
    pcl.ttrace = ma.concatenate((ttrace, ttraces))

    # Find minimum buoyancy from Trier et al. 2014, Part 1
    idx = np.ma.where(pcl.ptrace >= 500.)[0]
    if len(idx) != 0:
        b = pcl.ttrace[idx] - interp.vtmp(prof, pcl.ptrace[idx])
        idx2 = np.ma.argmin(b)
        pcl.bmin = b[idx2]
        pcl.bminpres = pcl.ptrace[idx][idx2]

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
    mucape   = mupcl.bplus
    mucinh = mupcl.bminus
    pbot = ma.masked
    ptop = ma.masked
    if mucape != 0:
        if mucape >= ecape and mucinh > ecinh:
            # Begin at surface and search upward for effective surface
            for i in xrange(prof.sfc, prof.top):
                pcl = cape(prof, pres=prof.pres[i], tmpc=prof.tmpc[i], dwpc=prof.dwpc[i])
                if pcl.bplus >= ecape and pcl.bminus > ecinh:
                    pbot = prof.pres[i]
                    break
            if not utils.QC(pbot): return ma.masked, ma.masked
            bptr = i
            # Keep searching upward for the effective top
            for i in xrange(bptr+1, prof.top):
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
    mincinh = kwargs.get('mincinh', 0.)
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
       
        Note: This is the definition of TEI on the SPC help page,
        but these calculations do not match up with the TEI values on the SPC Online Soundings.
        The TEI values online are more consistent with the max Theta-E
        minus the minimum Theta-E found in the lowest 400 mb AGL.

        This is what our TEI calculation shall be for the time being.

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
    
    layer_idxs = ma.where(prof.pres >= top_pres)[0]
    min_thetae = ma.min(prof.thetae[layer_idxs])
    max_thetae = ma.max(prof.thetae[layer_idxs])

    #tei = sfc_theta - min_thetae
    tei = max_thetae - min_thetae
    return tei

def esp(prof, **kwargs):
    
    '''
        Enhanced Stretching Potential (ESP)
        This composite parameter identifies areas where low-level buoyancy
        and steep low-level lapse rates are co-located, which may
        favor low-level vortex stretching and tornado potential.
       
        REQUIRES: 0-3 km MLCAPE (from MLPCL)

        Parameters
        ----------
        prof : Profile object
        mlpcl : Mixed-Layer Parcel object (optional)

        Returns
        -------
        esp : ESP index
        '''
     
    mlpcl = kwargs.get('mlpcl', None)
    if not mlpcl:
        try:
            mlpcl = prof.mlpcl
        except:
            mlpcl = parcelx(prof, flag=4)
    mlcape = mlpcl.b3km
    
    lr03 = prof.lapserate_3km # C/km
    if lr03 < 7. or mlpcl.bplus < 250.:
        return 0
    esp = (mlcape / 50.) * ((lr03 - 7.0) / (1.0))
    
    return esp

def sherb(prof, **kwargs):
    '''
        Severe Hazards In Environments with Reduced Buoyancy (SHERB) Parameter

        A composite parameter designed to assist forecasters in the High-Shear
        Low CAPE (HSLC) environment.  This allows better discrimination 
        between significant severe and non-severe convection in HSLC enviroments.

        It can detect significant tornadoes and significant winds.  Values above
        1 are more likely associated with significant severe.

        See Sherburn et. al. 2014 WAF for more information

        REQUIRES (if effective==True): The effective inflow layer be defined

        Parameters
        ----------
        prof : Profile object
        effective : True or False...use the effective layer computation or not
                    the effective bulk wind difference (prof.ebwd) must exist first
                    if not specified it will default to False (optional)
        ebottom : bottom of the effective inflow layer (mb) (optional) 
        etop :top of the effective inflow layer (mb) (optional) 
        mupcl : Most-Unstable Parcel (optional)

        Returns
        -------
        sherb : an integer for the SHERB parameter
                if effective==True and an effective inflow layer cannot be found,
                this function returns prof.missing

        '''

    effective = kwargs.get('effective', False)
    ebottom = kwargs.get('ebottom', None)
    etop = kwargs.get('etop', None)

    lr03 = lapse_rate(prof, 0, 3000, pres=False)
    lr75 = lapse_rate(prof, 700, 500, pres=True)

    if effective == False:
        p3km = interp.pres(prof, interp.to_msl(prof, 3000))
        sfc_pres = prof.pres[prof.get_sfc()]
        shear = utils.KTS2MS(winds.wind_shear(prof, pbot=sfc_pres, ptop=p3km))
        sherb = ( shear / 26. ) * ( lr03 / 5.2 ) * ( lr75 / 5.6 )
    else:
        if hasattr(prof, 'ebwd'):
            # If the Profile object has the attribute "ebwd"
            shear = utils.KTS2MS(utils.mag( prof.ebwd[0], prof.ebwd[1] ))

        elif ((not ebottom) or (not etop)) or \
             ((not hasattr(prof, 'ebottom') or not hasattr(prof, 'etop'))):
            # if the effective inflow layer hasn't been specified via the function arguments
            # or doesn't exist in the Profile object we need to calculate it, but we need mupcl
            if ebottom is None or etop is None:
                #only calculate ebottom and etop if they're not supplied by the kwargs
                if not hasattr(prof, 'mupcl') or not kwargs.get('mupcl', None):
                    # If the mupcl attribute doesn't exist in the Profile
                    # or the mupcl hasn't been passed as an argument
                    # compute the mupcl
                    mulplvals = DefineParcel(prof, flag=3, pres=300)
                    mupcl = cape(prof, lplvals=mulplvals)
                else:
                    mupcl = prof.mupcl
           
                # Calculate the effective inflow layer
                ebottom, etop = effective_inflow_layer( prof, mupcl=mupcl )
            
            if ebottom is np.masked or etop is np.masked:
                # If the inflow layer doesn't exist, return missing
                return prof.missing
            else:
                # Calculate the Effective Bulk Wind Difference
                ebotm = interp.to_agl(prof, interp.hght(prof, ebottom))
                depth = ( mupcl.elhght - ebotm ) / 2
                elh = interp.pres(prof, interp.to_msl(prof, ebotm + depth))
                ebwd = winds.wind_shear(prof, pbot=ebottom, ptop=elh)
        else:
            # If there's no way to compute the effective SHERB
            # because there's no information about how to get the
            # inflow layer, return missing.
            return prof.missing
        
        shear = utils.KTS2MS(utils.mag( prof.ebwd[0], prof.ebwd[1] ))
        sherb = ( shear / 27. ) * ( lr03 / 5.2 ) * ( lr75 / 5.6 )

    return sherb

def mmp(prof, **kwargs):

    """
        MCS Maintenance Probability (MMP)
        The probability that a mature MCS will maintain peak intensity
        for the next hour.
        
        This equation was developed using proximity soundings and a regression equation
        Uses MUCAPE, 3-8 km lapse rate, maximum bulk shear, 3-12 km mean wind speed
        From Coniglio et. al. 2006 WAF
        
        REQUIRES: MUCAPE (J/kg) 

        Parameters
        ----------
        prof : Profile object
        mupcl : Most-Unstable Parcel object (optional)
        
        Returns
        -------
        mmp : MMP index (%)
        
        Note:
        Per Mike Coniglio (personal comm.), the maximum deep shear value is computed by
        computing the shear vector between all the wind vectors
        in the lowest 1 km and all the wind vectors in the 6-10 km layer.
        The maximum speed shear from this is the max_bulk_shear value (m/s).
        """
    
    mupcl = kwargs.get('mupcl', None)
    if not mupcl:
        try:
            mupcl = prof.mupcl
        except:
            mulplvals = DefineParcel(prof, flag=3, pres=300)
            mupcl = cape(prof, lplvals=mulplvals)
    mucape = mupcl.bplus

    if mucape < 100.:
        return 0.

    agl_hght = interp.to_agl(prof, prof.hght)
    lowest_idx = np.where(agl_hght <= 1000)[0]
    highest_idx = np.where((agl_hght >= 6000) & (agl_hght < 10000))[0]
    possible_shears = np.empty((len(lowest_idx),len(highest_idx)))
    pbots = interp.pres(prof, prof.hght[lowest_idx])
    ptops = interp.pres(prof, prof.hght[highest_idx])

    for b in xrange(len(pbots)):
        for t in xrange(len(ptops)):
            if b < t: continue
            u_shear, v_shear = winds.wind_shear(prof, pbot=pbots[b], ptop=ptops[t])
            possible_shears[b,t] = utils.mag(u_shear, v_shear)

    max_bulk_shear = utils.KTS2MS(np.nanmax(possible_shears.ravel()))
    lr38 = lapse_rate(prof, 3000., 8000., pres=False)
    plower = interp.pres(prof, interp.to_msl(prof, 3000.))
    pupper = interp.pres(prof, interp.to_msl(prof, 12000.))
    mean_wind_3t12 = winds.mean_wind( prof, pbot=plower, ptop=pupper)
    mean_wind_3t12 = utils.KTS2MS(utils.mag(mean_wind_3t12[0], mean_wind_3t12[1]))

    a_0 = 13.0 # unitless
    a_1 = -4.59*10**-2 # m**-1 * s
    a_2 = -1.16 # K**-1 * km
    a_3 = -6.17*10**-4 # J**-1 * kg
    a_4 = -0.17 # m**-1 * s
    
    mmp = 1. / (1. + np.exp(a_0 + (a_1 * max_bulk_shear) + (a_2 * lr38) + (a_3 * mucape) + (a_4 * mean_wind_3t12)))
    
    return mmp

def wndg(prof, **kwargs):
    '''
        Wind Damage Parameter (WNDG)

        A non-dimensional composite parameter that identifies areas
        where large CAPE, steep low-level lapse rates,
        enhanced flow in the low-mid levels, and minimal convective
        inhibition are co-located.
        
        WNDG values > 1 favor an enhanced risk for scattered damaging
        outflow gusts with multicell thunderstorm clusters, primarily
        during the afternoon in the summer.
        
        REQUIRES: MLCAPE (J/kg), MLCIN (J/kg)

        Parameters
        ----------
        prof : Profile object
        mlpcl : Mixed-Layer Parcel object (optional) 

        Returns
        -------
        wndg : WNDG index
        '''
    
    mlpcl = kwargs.get('mlpcl', None)
    if not mlpcl:
        try:
            mlpcl = prof.mlpcl
        except:
            mllplvals = DefineParcel(prof, flag=4)
            mlpcl = cape(prof, lplvals=mllplvals)
    mlcape = mlpcl.bplus

    lr03 = lapse_rate( prof, 0, 3000., pres=False ) # C/km
    bot = interp.pres( prof, interp.to_msl( prof, 1000. ) )
    top = interp.pres( prof, interp.to_msl( prof, 3500. ) )
    mean_wind = winds.mean_wind(prof, pbot=bot, ptop=top) # needs to be in m/s
    mean_wind = utils.KTS2MS(utils.mag(mean_wind[0], mean_wind[1]))
    mlcin = mlpcl.bminus # J/kg
    
    if lr03 < 7:
        lr03 = 0.
    
    if mlcin < -50:
        mlcin = -50.
    wndg = (mlcape / 2000.) * (lr03 / 9.) * (mean_wind / 15.) * ((50. + mlcin)/40.)
    
    return wndg


def sig_severe(prof, **kwargs):
    '''
        Significant Severe (SigSevere)
        Craven and Brooks, 2004
        
        REQUIRES: MLCAPE (J/kg), 0-6km Shear (kts)

        Parameters
        ----------
        prof : Profile object
        mlpcl : Mixed-Layer Parcel object (optional) 

        Returns
        -------
        sigsevere : significant severe parameter (m3/s3)
    '''
     
    mlpcl = kwargs.get('mlpcl', None)
    sfc6shr = kwargs.get('sfc6shr', None)
    if not mlpcl:
        try:
            mlpcl = prof.mlpcl
        except:
            mllplvals = DefineParcel(prof, flag=4)
            mlpcl = cape(prof, lplvals=mllplvals)
    mlcape = mlpcl.bplus

    if not sfc6shr:
        try:
            sfc_6km_shear = prof.sfc_6km_shear
        except:
            sfc = prof.pres[prof.sfc]
            p6km = interp.pres(prof, interp.to_msl(prof, 6000.))
            sfc_6km_shear = winds.wind_shear(prof, pbot=sfc, ptop=p6km)

    sfc_6km_shear = utils.mag(sfc_6km_shear[0], sfc_6km_shear[1])
    shr06 = utils.KTS2MS(sfc_6km_shear)
    
    sigsevere = mlcape * shr06
    return sigsevere

def dcape(prof):
    '''
        Downdraft CAPE (DCAPE)
        
        Adapted from John Hart's (SPC) DCAPE code in NSHARP donated by Rich Thompson (SPC)

        Calculates the downdraft CAPE value using the downdraft parcel source found in the lowest
        400 mb of the sounding.  This downdraft parcel is found by identifying the minimum 100 mb layer 
        averaged Theta-E.

        Afterwards, this parcel is lowered to the surface moist adiabatically (w/o virtual temperature
        correction) and the energy accumulated is called the DCAPE.

		Future adaptations of this function may utilize the Parcel/DefineParcel object.

        Parameters
        ----------
        prof : Profile object
        
        Returns
        -------
        dcape : downdraft CAPE (J/kg)
        ttrace : downdraft parcel trace temperature (C)
        ptrace : downdraft parcel trace pressure (mb)
        '''
    
    sfc_pres = prof.pres[prof.sfc]
    prof_thetae = prof.thetae
    prof_wetbulb = prof.wetbulb
    mask1 = prof_thetae.mask
    mask2 = prof.pres.mask
    mask = np.maximum( mask1, mask2 ) 
    prof_thetae = prof_thetae[~mask]
    prof_wetbulb = prof_wetbulb[~mask]
    pres = prof.pres[~mask]
    hght = prof.hght[~mask]
    dwpc = prof.dwpc[~mask]
    tmpc = prof.tmpc[~mask]
    idx = np.where(prof.pres >= sfc_pres - 400.)[0]

    # Find the minimum average theta-e in a 100 mb layer
    mine = 1000.0
    minp = -999.0
    for i in idx:
        thta_e_mean = mean_thetae(prof, pbot=pres[i], ptop=pres[i]-100.)
        if utils.QC(thta_e_mean) and thta_e_mean < mine:
            minp = pres[i] - 50.
            mine = thta_e_mean

    upper = minp
    uptr = np.where(pres >= upper)[0]
    uptr = uptr[-1]
    
    # Define parcel starting point
    tp1 = thermo.wetbulb(upper, interp.temp(prof, upper), interp.dwpt(prof, upper))
    pe1 = upper
    te1 = interp.temp(prof, pe1)
    h1 = interp.hght(prof, pe1)
    tote = 0
    lyre = 0

    # To keep track of the parcel trace from the downdraft
    ttrace = [tp1] 
    ptrace = [upper]

    # Lower the parcel to the surface moist adiabatically and compute
    # total energy (DCAPE)
    iter_ranges = xrange(uptr, -1, -1)
    ttraces = ma.zeros(len(iter_ranges))
    ptraces = ma.zeros(len(iter_ranges))
    ttraces[:] = ptraces[:] = ma.masked
    for i in iter_ranges:
        pe2 = pres[i]
        te2 = tmpc[i]
        h2 = hght[i]
        tp2 = thermo.wetlift(pe1, tp1, pe2)

        if utils.QC(te1) and utils.QC(te2):
            tdef1 = (tp1 - te1) / (thermo.ctok(te1))
            tdef2 = (tp2 - te2) / (thermo.ctok(te2))
            lyrlast = lyre
            lyre = 9.8 * (tdef1 + tdef2) / 2.0 * (h2 - h1)
            tote += lyre

        ttraces[i] = tp2
        ptraces[i] = pe2

        pe1 = pe2
        te1 = te2
        h1 = h2
        tp1 = tp2
    drtemp = tp2 # Downrush temp in Celsius

    return tote, ma.concatenate((ttrace, ttraces[::-1])), ma.concatenate((ptrace, ptraces[::-1]))

def precip_eff(prof, **kwargs):
    '''
        Precipitation Efficiency

        This calculation comes from Noel and Dobur 2002, published
        in NWA Digest Vol 26, No 34.

        The calculation multiplies the PW from the whole atmosphere
        by the 1000 - 700 mb mean relative humidity (in decimal form)

        Values on the SPC Mesoanalysis range from 0 to 2.6.

        Larger values means that the precipitation is more efficient.

        Parameters
        ----------
        prof : Profile object
               if the Profile object does not have a pwat attribute
               this function will perform the calculation.
        pwat : (optional) precomputed precipitable water vapor (inch)
        pbot : (optional) the bottom pressure of the RH layer (mb)
        ptop : (optional) the top pressure of the RH layer (mb)

        Returns
        -------
        precip_efficency : the PE value (units inches)

    '''
    
    pw = kwargs.get('pwat', None)
    pbot = kwargs.get('pbot', 1000)
    ptop = kwargs.get('ptop', 700)

    if pw is None or not hasattr(prof, 'pwat'):
        pw = precip_water(prof)
    else:
        pw = prof.pwat

    mean_rh = mean_relh(prof, pbot=pbot, ptop=ptop) / 100.

    return pw*mean_rh

def pbl_top(prof):
    '''
        Planetary Boundary Layer Depth
        Adapted from NSHARP code donated by Rich Thompson (SPC)

        Calculates the planetary boundary layer depth by calculating the 
        virtual potential temperature of the surface parcel + .5 K, and then searching
        for the location above the surface where the virtual potential temperature of the profile
        is greater than the surface virtual potential temperature.

        While this routine suggests a parcel lift, this Python adaptation does not use loop
        like parcelx().

        Parameters
        ----------
        prof : Profile object

        Returns
        -------
        ppbl_top : the pressure that corresponds to the top of the PBL
    '''

    thetav = thermo.theta(prof.pres, thermo.virtemp(prof.pres, prof.tmpc, prof.dwpc))
    try:
        level = np.where(thetav[prof.sfc]+.5 < thetav)[0][0]
    except IndexError:
        print "Warning: PBL top could not be found."
        level = thetav.shape[0] - 1

    return prof.pres[level]

def dcp(prof):
    '''
        Derecho Composite Parameter

        This parameter is based on a data set of 113 derecho events compiled by Evans and Doswell (2001).
        The DCP was developed to identify environments considered favorable for cold pool "driven" wind
        events through four primary mechanisms:

        1) Cold pool production [DCAPE]
        2) Ability to sustain strong storms along the leading edge of a gust front [MUCAPE]
        3) Organization potential for any ensuing convection [0-6 km shear]
        4) Sufficient flow within the ambient environment to favor development along downstream portion of the
            gust front [0-6 km mean wind].

        This index is fomulated as follows:
        DCP = (DCAPE/980)*(MUCAPE/2000)*(0-6 km shear/20 kt)*(0-6 km mean wind/16 kt)

        Reference:
        Evans, J.S., and C.A. Doswell, 2001: Examination of derecho environments using proximity soundings. Wea. Forecasting, 16, 329-342.

        Parameters
        ----------
        prof : Profile object

        Returns
        -------
        dcp : number
            Derecho Composite Parameter (unitless)

    '''
    sfc = prof.pres[prof.sfc]
    p6km = interp.pres(prof, interp.to_msl(prof, 6000.))
    dcape_val = getattr(prof, 'dcape', dcape( prof )[0])
    mupcl = getattr(prof, 'mupcl', parcelx(prof, flag=1))
    sfc_6km_shear = getattr(prof, 'sfc_6km_shear', winds.wind_shear(prof, pbot=sfc, ptop=p6km))
    mean_6km = getattr(prof, 'mean_6km', utils.comp2vec(*winds.mean_wind(prof, pbot=sfc, ptop=p6km)))
    mag_shear = utils.mag(sfc_6km_shear[0], sfc_6km_shear[1])
    mag_mean_wind = mean_6km[1]

    dcp = (dcape_val/980.) * (mupcl.bplus/2000.) * (mag_shear / 20. ) * (mag_mean_wind / 16.)

    return dcp


def mburst(prof):
    '''
        Microburst Composite

        Developer unknown.

        Below is taken from the SPC Mesoanalysis:
        The Microburst Composite is a weighted sum of the following individual parameters: SBCAPE, SBLI,
        lapse rates, vertical totals (850-500 mb temperature difference), DCAPE, and precipitable water.
        The specific terms and weights are listed below:

        SBCAPE term -> < 3100 set to 0; 3100-3999 set to 1; >= 4000 set to 2;
        SBLI term -> > -8 set to 0; <= -8 set to 1; <= -9 set to 2; <= -10 set to 3;
        0-3 km lapse rate term -> <= 8.4 set to 0; > 8.4 set to 1;
        vertical totals term -> < 27 set to 0; >= 27 set to 1; >= 28 set to 2; >= 29 set to 3;
        DCAPE term -> < 900 set to 0; >= 900 set to 1; >= 1100 set to 2; >= 1300 set to 3;
        precipitable water term -> <= 1.5 set to -5; > 1.5 set to 0.

        All six of the terms are summed to arrive at the final microburst composite value.
        The values can be interpreted in the following manner: 3-4 infers a "slight chance" of a microburst;
        5-8 infers a "chance" of a microburst; >= 9 infers that microbursts are "likely".
        These values can also be viewed as conditional upon the existence of a storm.

        Parameters
        ----------
        prof : Profile object

        Returns
        -------
        mburst : number
            Microburst Composite (unitless)
    '''

    sbpcl = getattr(prof, 'sfcpcl', parcelx(prof, flag=1))
    lr03 = getattr(prof, 'lapserate_3km', lapse_rate( prof, 0., 3000., pres=False ))
    tt = getattr(prof, 'totals_totals', t_totals( prof ))
    dcape_val = getattr(prof, 'dcape', dcape( prof )[0])
    pwat = getattr(prof, 'pwat', precip_water( prof ))

    if sbpcl.bplus < 3100:
        sbcape_term = 0
    elif sbpcl.bplus >= 3100 and sbpcl.bplus < 3999:
        sbcape_term = 1
    else:
        sbcape_term = 2

    if sbpcl.li5 > -8:
        sbli_term = 0
    elif sbpcl.li5 <= -8 and sbpcl.li5 > -9:
        sbli_term = 1
    elif sbpcl.li5 <= -9 and sbpcl.li5 > -10:
        sbli_term = 2
    elif sbpcl.li5 <= -10:
        sbli_term = 3

    if lr03 <= 8.4:
        lr03_term = 0
    else:
        lr03_term = 1

    if tt < 27:
        tt_term = 0
    elif tt >= 27 and tt < 28:
        tt_term = 1
    elif tt >= 28 and tt < 29:
        tt_term = 2
    else:
        tt_term = 3

    if dcape_val < 900:
        dcape_term = 0
    elif dcape_val >= 900 and dcape_val < 1100:
        dcape_term = 1
    elif dcape_val >= 1100 and dcape_val < 1300:
        dcape_term = 2
    else:
        dcape_term = 3

    if pwat <= 1.5:
        pwat_term = -5
    else:
        pwat_term = 0

    mburst = sbcape_term + sbli_term + lr03_term + tt_term + dcape_term + pwat_term

    return mburst

def ehi(prof, pcl, hbot, htop, stu=0, stv=0):
    '''
        Energy-Helicity Index

        Computes the energy helicity index (EHI) using a parcel
        object and a profile object.

        The equation is EHI = (CAPE * HELICITY) / 160000.

        Parameters
        ----------
        prof : Profile object
        pcl : Parcel object
        hbot : number
            Height of the bottom of the helicity layer [m]
        htop : number
            Height of the top of the helicity layer [m]
        stu : number
            Storm-relative wind U component [kts]
            (optional; default=0)
        stv : number
            Storm-relative wind V component [kts]
            (optional; default=0)

        Returns
        -------
        ehi : number
            Energy Helicity Index (unitless)
    '''

    helicity = winds.helicity(prof, hbot, htop, stu=stu, stv=stv)[0]
    ehi = (helicity * pcl.bplus) / 160000.

    return ehi

def sweat(prof):
    '''
        SWEAT Index

        Computes the SWEAT (Severe Weather Threat Index) using the following numbers:

        1.) 850 Dewpoint
        2.) Total Totals Index
        3.) 850 mb wind speed
        4.) 500 mb wind speed
        5.) Direction of wind at 500
        6.) Direction of wind at 850

        Parameters
        ----------
        prof : Profile object

        Returns
        -------
        sweat : number
            SWEAT Index (number)
    '''

    td850 = interp.dwpt(prof, 850)
    vec850 = interp.vec(prof, 850)
    vec500 = interp.vec(prof, 500)
    tt = getattr(prof, 'totals_totals', t_totals( prof ))

    if td850 > 0:
        term1 = 12. * td850
    else:
        term1 = 0

    if tt < 49:
        term2 = 0
    else:
        term2 = 20. * (tt - 49)

    term3 = 2 * vec850[1]
    term4 = vec500[1]
    if vec500[0] - vec850[0] > 0:
        term5 = 125 * (np.sin( np.radians(vec500[0] - vec850[0])  + 0.2))
    else:
        term5 = 0

    sweat = term1 + term2 + term3 + term4 + term5

    return sweat
