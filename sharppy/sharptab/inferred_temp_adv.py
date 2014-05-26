import numpy as np
from sharppy.sharptab import winds, utils, interp

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
        multiplier = (f / (9.81)) * (np.pi / 180.) # Units: (s**-1 / (m/s**2)) * (radians/degrees)
    else:
        # If you can't pass the latitude of the profile point, use this calculation (approximate)
        multiplier = ((10.**-4) / 9.81) * (np.pi / 180.) # Units: (s**-1 / (m/s**2)) * (radians/degrees))

    pressures = np.arange(prof.pres[prof.get_sfc()], 100, -100) # Units: mb

    pressure_bounds = []
    temp_adv = np.empty(len(pressures) - 1)
    for i in range(1, len(pressures)):
        bottom_pres = pressures[i-1]
        top_pres = pressures[i]

        if bottom_pres == 0:
            sfc_idx = prof.get_sfc()
            bottom_pres = prof.pres[sfc_idx]
        
        # Get the temperatures from both levels (in Kelvin)
        btemp = interp.temp(prof, bottom_pres) + 273.15
        ttemp = interp.temp(prof, top_pres) + 273.15

        # Calculate the average temperature
        avg_temp = (btemp + ttemp) / 2.

        # Calculate the mean wind between the two levels (this is assumed to be geostrophic)
        mean_u, mean_v = winds.mean_wind(prof, pbot=bottom_pres, ptop=top_pres)

        mean_wdir, mean_wspd = utils.comp2vec(mean_u, mean_v) # Wind speed is in knots here
        mean_wspd = utils.KTS2MS(mean_wspd) # Convert this geostrophic wind speed to m/s
        
        # Get the two heights of the top and bottom layer
        bhght = interp.hght(prof, bottom_pres) # Units: meters
        thght = interp.hght(prof, top_pres) # Units: meters
        
        top_wdir = interp.vec(prof, top_pres)[0] # Meteorological degrees (degrees from north)
        bottom_wdir = interp.vec(prof, bottom_pres)[0] # same units as top_wdir

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
        t_adv = multiplier * np.power(mean_wspd,2) * avg_temp * (d_theta / (thght - bhght)) # Units: Kelvin / seconds
        
        # Append the pressure bounds so the person knows the pressure
        pressure_bounds.append((bottom_pres, top_pres))
        temp_adv[i-1] = t_adv*60.*60. # Converts Kelvin/seconds to Kelvin/hour (or Celsius/hour)

    pressure_bounds = np.asarray(pressure_bounds)
    return temp_adv, pressure_bounds
    
