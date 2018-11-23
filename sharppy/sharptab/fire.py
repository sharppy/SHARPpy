from sharppy.sharptab import thermo, utils, interp, constants
import numpy as np

## Routines implemented in Python by Greg Blumberg - CIMMS and Kelton Halbert (OU SoM)
## wblumberg@ou.edu, greg.blumberg@noaa.gov, kelton.halbert@noaa.gov, keltonhalbert@ou.edu

def fosberg(prof):
    '''
        The Fosberg Fire Weather Index
        Adapted from code donated by Rich Thompson - NOAA Storm Prediction Center

        Description:
        The FWI (Fire Weather Index) is defined by a quantitative model that provides
        a nonlinear filter of meteorological data which results in a linear relationship
        between the combined meteorological variables of relative humidity and wind speed,
        and the behavior of wildfires. Thus the index deals with only the weather conditions,
        not the fuels. Several sets of conditions have been defined by Fosberg (Fosberg, 1978)
        to apply this to fire weather management. The upper limits have been set to give an
        index value of 100 if the moisture content is zero and the wind is 30 mph. 

        Thus, the numbers range from 0 to 100 and if any number is larger than 100, it is set back to 100. 
        The index can be used to measure changes in fire weather conditions. Over several years of use, 
        Fosberg index values of 50 or greater generally appear significant on a national scale.
        The SPC fire weather verification scheme uses the Fosberg Index, but with a check for
        both temperature (60F) and adjective fire danger rating (3-High, 4-Very High, 5-Extreme).

        Description Source - http://www.spc.noaa.gov/exper/firecomp/INFO/fosbinfo.html

        WARNING: This function has not been fully tested.

        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        param : number
            Fosberg Fire Weather Index

    '''
    tmpf = thermo.ctof(prof.tmpc[prof.get_sfc()])
    fmph = utils.KTS2MPH(prof.wspd[prof.get_sfc()])

    rh = thermo.relh(prof.pres[prof.sfc], prof.tmpc[prof.sfc], prof.dwpc[prof.sfc])
    if (rh <= 10):
        em = 0.03229 + 0.281073*rh - 0.000578*rh*tmpf
    elif (10 < rh <= 50):
        em = 2.22749 + 0.160107*rh - 0.014784*tmpf
    else:
        em = 21.0606 + 0.005565*rh*rh - 0.00035*rh*tmpf - 0.483199*rh

    em30 = em/30
    u_sq = fmph*fmph
    fmdc = 1 - 2*em30 + 1.5*em30*em30 - 0.5*em30*em30*em30

    param = (fmdc*np.sqrt(1+u_sq))/0.3002

    return param

def haines_height(prof):
    '''
        Haines Index Height calculation
        
        Calculates the appropriate height category(Low/Mid/High) given the 
        the lowest height in the sounding. 
        
        Adapted from S-591 course
        Added by Nickolai Reimer (NWS Billings, MT)
                
        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        param : number
            the Haines Index Height

    '''
    sfc_elevation = prof.hght[prof.sfc]
    
    # Haines low elevation below 1000 ft / 305 m
    if sfc_elevation < 305:
        return constants.HAINES_LOW
    
    # Haines mid elevation between 1000 ft / 305 m and 3000 ft / 914 m
    elif 305 <= sfc_elevation and sfc_elevation <= 914:
        return constants.HAINES_MID
    
    # Haines high elevation above 3000 ft / 914 m
    else:
        return constants.HAINES_HIGH
        
def haines_low(prof):
    '''
        Haines Index Low Elevation calculation
        
        Calculates the Haines Index(Lower Atmosphere Severity Index)
        using the lower elevation parmeters, used below 1000ft or 305 m.
        
        Pressure levels 950 mb and 850 mb
        Dewpoint depression at 850 mb
        
        Lapse Rate Term
        ---------------
        1 : < 4C
        2 : 4C to 7C
        3 : > 7C
        
        Dewpoint Depression Term
        ------------------------
        1 : < 6C
        2 : 6C to 9C
        3 : > 9C
        
        Adapted from S-591 course 
        Added by Nickolai Reimer (NWS Billings, MT)
        
        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        param : number
            the Haines Index low

    '''
    
    tp1  = interp.temp(prof, 950)
    tp2  = interp.temp(prof, 850)
    tdp2 = interp.dwpt(prof, 850)
    
    if utils.QC(tp1) and utils.QC(tp2) and utils.QC(tdp2):
        lapse_rate = tp1 - tp2
        dewpoint_depression = tp2 - tdp2
        
        if lapse_rate < 4:
            a = 1
        elif 4 <= lapse_rate and lapse_rate <= 7:
            a = 2
        else:
            a = 3
        
        if dewpoint_depression < 6:
            b = 1
        elif 6 <= dewpoint_depression and dewpoint_depression <= 9:
            b = 2
        else:
            b = 3
        return a + b
    else:
        return constants.MISSING

def haines_mid(prof):
    '''
        Haines Index Mid Elevation calculation
        
        Calculates the Haines Index(Lower Atmosphere Severity Index)
        using the middle elevation parmeters, used 
        between 1000 ft or 305 m and 3000 ft or 914 m.
        
        Pressure levels 850 mb and 700 mb
        Dewpoint depression at 850 mb
        
        Lapse Rate Term
        ---------------
        1 : < 6C
        2 : 6C to 10C
        3 : > 10C
        
        Dewpoint Depression Term
        ------------------------
        1 : < 6C
        2 : 6C to 12C
        3 : > 12C
        
        Adapted from S-591 course
        Added by Nickolai Reimer (NWS Billings, MT)
        
        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        param : number
            the Haines Index mid

    '''
    
    tp1  = interp.temp(prof, 850)
    tp2  = interp.temp(prof, 700)
    tdp1 = interp.dwpt(prof, 850)
    
    if utils.QC(tp1) and utils.QC(tp2) and utils.QC(tdp1):
        lapse_rate = tp1 - tp2
        dewpoint_depression = tp1 - tdp1
        
        if lapse_rate < 6:
            a = 1
        elif 6 <= lapse_rate and lapse_rate <= 10:
            a = 2
        else:
            a = 3
        
        if dewpoint_depression < 6:
            b = 1
        elif 6 <= dewpoint_depression and dewpoint_depression <= 12:
            b = 2
        else:
            b = 3
        return a + b
    else:
        return constants.MISSING

def haines_high(prof):
    '''
        Haines Index High Elevation calculation
        
        Calculates the Haines Index(Lower Atmosphere Severity Index)
        using the higher elevation parmeters, used above 3000ft or 914 m.
        
        Pressure levels 700 mb and 500 mb
        Dewpoint depression at 700 mb
        
        Lapse Rate Term
        ---------------
        1 : < 18C
        2 : 18C to 21C
        3 : > 21C
        
        Dewpoint Depression Term
        ------------------------
        1 : < 15C
        2 : 15C to 20C
        3 : > 20C
        
        Adapted from S-591 course
        Added by Nickolai Reimer (NWS Billings, MT)
        
        Parameters
        ----------
        prof : profile object
            Profile object

        Returns
        -------
        param : number
            the Haines Index high

    '''
    tp1  = interp.temp(prof, 700)
    tp2  = interp.temp(prof, 500)
    tdp1 = interp.dwpt(prof, 700)
    
    if utils.QC(tp1) and utils.QC(tp2) and utils.QC(tdp1):
        lapse_rate = tp1 - tp2
        dewpoint_depression = tp1 - tdp1
        
        if lapse_rate < 18:
            a = 1
        elif 18 <= lapse_rate and lapse_rate <= 21:
            a = 2
        else:
            a = 3
        
        if dewpoint_depression < 15:
            b = 1
        elif 15 <= dewpoint_depression and dewpoint_depression <= 20:
            b = 2
        else:
            b = 3
        return a + b
    else:
        return constants.MISSING


