from sharppy.sharptab import *
import numpy as np

## Routines implemented in Python by Greg Blumberg - CIMMS and Kelton Halbert (OU SoM)
## wblumberg@ou.edu, greg.blumberg@noaa.gov, kelton.halbert@noaa.gov, keltonhalbert@ou.edu

def fosberg(prof):
    '''
        The Fosberg Fire Weather Index
        Adapted from code by Rich Thompson - NOAA Storm Prediction Center

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

        Source - http://www.spc.noaa.gov/exper/firecomp/INFO/fosbinfo.html

        Parameters
        ----------
        prof - Profile object

        Returns
        -------
        param - the Fosberg Fire Weather Index

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
