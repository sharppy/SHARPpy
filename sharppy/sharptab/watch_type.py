from sharppy.sharptab import *
import numpy as np

def wind_chill(prof):
    # Needs to be tested
    # Equation from www.nws.noaa.gov/os/windchill/index.shtml
    #
    sfc_temp = thermo.ctof(prof.tmpc[prof.get_sfc()])
    sfc_wspd = utils.KTS2MPH(prof.wspd[prof.get_sfc()])

    wind_chill = 35.74 + (0.6215*sfc_temp) - (35.75*(sfc_wspd**0.16))\
               + 0.4275 * (sfc_temp) * (sfc_wspd**0.16)
    return wind_chill

def init_phase(prof):
    '''
        Determine the initial phase of any precipitation source in the profile.

        '''

    plevel = 0
    phase = -1

    if prof.omega.all() is not ma.masked:
        # No vertical velocity data to be used
        below_5km_idx = np.ma.where(prof.hght[1:] < interp.to_msl(prof, 5000.))[0]
    else:
        # Use the VV to find the source of precip.
        below_5km_idx = np.ma.where((prof.hght[1:] < interp.to_msl(prof, 5000.)) & (prof.omeg <= 0))[0]    
   
    # Compute the RH at the top and bottom of 50 mb layers
    rh = thermo.relh(prof.pres[1:][below_5km_idx], prof.tmpc[1:][below_5km_idx], prof.dwpc[1:][below_5km_idx])
    new_pres = prof.pres[1:][below_5km_idx] + 50.
    new_temp = interp.temp(prof, new_pres)
    new_dwpt = interp.dwpt(prof, new_pres)
    rh_plus50 = thermo.relh(new_pres, new_temp, new_dwpt)
    
    # Find layers where the RH is >80% at the top and bottom
    layers_idx = np.ma.where((rh_plus50 > 80) & (rh > 80))[0]

    if len(layers_idx) == 0:
        st = "N/A"
        return plevel, phase, st

    # Find the highest layer up via the largest index
    top_most_layer = np.ma.max(layers_idx)
    plevel = new_pres[top_most_layer] - 25.

    # Determine the initial precip type based on the temp in the layer
    tmp = interp.temp(prof, plevel)
    if tmp > 0:
        phase = 0
        st = "Rain"
    elif tmp <= 0 and tmp > -5:
        phase = 1
        st = "Freezing Rain"
    elif tmp <=-5 and tmp > -9:
        phase = 1
        st = "ZR/S Mix"
    elif tmp <= -9:
        phase = 3
        st = "Snow"
    else:
        st = "N/A"

    return plevel, phase, st

def posneg_temperature(prof, start):
    return

def posneg_wetbulb(prof, start):


    # Find lowest obs in layer
    lower = prof.pres[prof.get_sfc()]
    lptr  = prof.get_sfc()

    # Find the highest obs in the layer
    if start == -1:
        lvl, phase, st = init_phase(prof)
        if lvl > 0:
            upper = lvl
        else:
            upper = 500.
    else:
        upper = start

    # Something needs to be done here to get the right uptr
    # I don't want to duplicate this loop
    '''
        i=numlvl-1;
        while(sndg[i][pIndex] < upper) {
            i--;
            if (i < 0) {
                fprintf(stderr,
                 "Warning: posneg_temp: Could not find a pressure greater than %.2f\n",
                   upper);
                fprintf(stderr, "Using %.2f as the upper level.\n",
                  sndg[0][pIndex]);
                i = 0;
                break;
                }
        }
        uptr = i;
        if (sndg[i][pIndex] == upper)
            uptr--;
    '''
    # Start with the upper layer
    pe1 = upper;
    h1 =  interp.hght(prof, pe1);
    te1 = wetbulb(pe1, interp.temp(prof, pe1), interp.dwpt(prof, pe1))
    tp1 = 0

    totp = totn = tote = ptop = pbot = lyrlast = 0

    for i in np.arange(uptr, lptr-1, -1):
        pe2 = prof.pres[i]
        h2 = prof.hght[i]
        te2 = thermo.wetbulb(pe2, interp.temp(prof, pe2), interp.dwpt(prof, pe2))
        tp2 = 0
        tdef1 = (0 - te1) / (te1 + 273.15);
        tdef2 = (0 - te2) / (te2 + 273.15);
        lyrlast = lyre;
        lyre = 9.8 * (tdef1 + tdef2) / 2.0 * (h2 - h1);

        # Has a warm layer been found yet?
        if te2 > 0:
            if warmlayer == 0:
                warmlayer = 1
                ptop = pe2

        # Has a cold layer been found yet?
        if te2 < 0:
            if warmlayer == 1 and coldlayer == 0:
                coldlayer = 1
                pbot = pe2

        if warmlayer > 0:
            if lyre > 0:
                totp += lyre
            else:
                totn += lyre
            tote += lyre

        pelast = pe1
        pe1 = pe2
        h1 = h2
        te1 = te2
        tp1 = tp2
    
    if warmlayer == 1 and coldlayer == 1:
        pos = totp
        neg = totn
        top = ptop
        bot = pbot
    else:
        neg = 0
        pos = 0
        bot = 0
        top = 0

    return pos, neg, top, bot

def best_guess_precip(struct):
    return

def precip_type(prof):
    #
    # This function looks at the current SHARPPY profile (prof)
    # and makes a single guess of the precipitation type associated with
    # that profile.
    #
    # it would be nice to produce probabilites of the preciptation type using
    # different methods, but it's 12 AM now.
    #
    # it would also be nice to have BUFKIT's precpitation intensity and type algorithm

    # Step 1: Check for ice in a cloud (is there a cloud with temps of -10 to -18 C?)

    # if no ice in cloud, check surface temp
    # if surface temp > 0 C, it's rain
    # if surface temp < 0 C, it's freezing rain

    # if there is ice in the cloud, what are the temperatures below it?
    # if the temperature below is less than 0.5 C, it's snow, but ony if T_w <= 0 C
    # otherwise if T_w > 0 C in the lowest 100 meters, and sfc T_w > 33 F, it's rain

    # if the temperatures below the ice cloud are between 0.5 to 3 C, there will be melting
    # if T_w or T are <= 0C, it's a mix (if warm layer is near 1 C) or sleet ( if warm layer is near 3 C)
    # if T_w >= 0 C in lowest 100 m and T_w > 33F, it's rain or drizzle

    # if the temperatures below the ice cloud are > 3 C, there's total melting
    # if minimum cold layer temp is > -12 C and sfc_T <= 0 C, it's freezing rain
    # if minimum cold layer temp is > -12 C and sfc_T > 0 C, it's rain.
    # if minimum cold layer temp is < -12 C and sfc_T_w < 33 F, it's snow and sleet
    return

def possible_watch(prof):
    #
    # This function looks at the current SHARPPY profile (prof)
    # and creates a list of possible watch types from this profile
    # using critera for the different watches, as well as some
    # subjectively determined thresholds.
    #
    # (it would be nice if someone made a database of soundings and watch types
    # to find which indices corresponded to which types of watches)
    #
    # Watch types covered in this code:
    # - Tornado Watch
    # - PDS Tornado Watch
    # - Severe Thunderstorm Watch
    # - PDS Severe Thunderstorm Watch
    # - Flash Flood Watch
    # - Blizzard Watch
    # - Winter Storm Watch
    # - Wind Chill Watch
    # - Fire Weather Watch
    # - Excessive Heat Watch
    # - Freeze Watch
    
    """
        Updated on 10/6/2014 - Added Rich Thompson's code
    
        Requires these calculations to already be in the profile object:
        STP_EFF
        MLCAPE
        SHIP

    """
        
    watch_types = []
    colors = []
    

    """BEGIN RICH'S DECISION TREE CODE"""
    lr1 = params.lapse_rate( prof, 0, 1000, pres=False )
    stp_eff = prof.stp_cin
    stp_fixed = prof.stp_fixed
    srw_4_6km = utils.mag(prof.srw_4_6km[0],prof.srw_4_6km[1])
    sfc_8km_shear = utils.mag(prof.sfc_8km_shear[0],prof.sfc_8km_shear[1])
    right_esrh = prof.right_esrh[0]
    srh1km = prof.srh1km[0]
    if stp_eff >= 3 and stp_fixed >= 3 and srh1km >= 200 and right_esrh >= 200 and srw_4_6km >= 15.0 and \
        sfc_8km_shear > 45.0 and prof.sfcpcl.lclhght < 1000. and prof.mlpcl.lclhght < 1200 and lr1 >= 5.0 and \
        prof.mlpcl.bminus > -50 and prof.ebotm == 0:
        watch_types.append("PDS TOR")
        colors.append("#FF0000")
    elif (stp_eff >= 3 or stp_fixed >= 4) and prof.mlpcl.bminus > -125. and prof.ebotm == 0:
        watch_types.append("TOR")
        colors.append("#FF0000")
    elif (stp_eff >= 1 or stp_fixed >= 1) and (srw_4_6km >= 15.0 or sfc_8km_shear >= 40) and \
        prof.mlpcl.bminus > -50 and prof.ebotm == 0:
        watch_types.append("TOR")
        colors.append("#FF0000")
    elif (stp_eff >= 1 or stp_fixed >= 1) and ((prof.low_rh + prof.mid_rh)/2. >= 60) and lr1 >= 5.0 and \
        prof.mlpcl.bminus > -50 and prof.ebotm == 0:
        watch_types.append("TOR")
        colors.append("#FF0000")
    elif (stp_eff >= 1 or stp_fixed >= 1) and prof.mlpcl.bminus > -150 and prof.ebotm == 0.:
        watch_types.append("MRGL TOR")
        colors.append("#FF0000")
    elif (stp_eff >= 0.5 and prof.right_esrh >= 150) or (stp_fixed >= 0.5 and srh1km >= 150) and \
        prof.mlpcl.bminus > -50 and prof.ebotm == 0.:
        watch_types.append("MRGL TOR")
        colors.append("#FF0000")

    #SVR LOGIC
    if (stp_fixed >= 1.0 or prof.right_scp >= 4.0 or stp_eff >= 1.0) and prof.mupcl.bminus >= -50:
        colors.append("#FFFF00")
        watch_types.append("SVR")
    elif prof.right_scp >= 2.0 and (prof.ship >= 1.0 or prof.dcape >= 750) and prof.mupcl.bminus >= -50:
        colors.append("#FFFF00")
        watch_types.append("SVR")
    elif prof.sig_severe >= 30000 and prof.mmp >= 0.6 and prof.mupcl.bminus >= -50:
        colors.append("#FFFF00")
        watch_types.append("SVR")
    elif prof.mupcl.bminus >= -75.0 and (prof.wndg >= 0.5 or prof.ship >= 0.5 or prof.right_scp >= 0.5):
        colors.append("#0099CC")
        watch_types.append("MRGL SVR")
    """END RICH'S CODE"""
    
    # Flash Flood Watch PWV is larger than normal and cloud layer mean wind speeds are slow
    # This is trying to capture the ingredients of moisture and advection speed, but cannot
    # handle precipitation efficiency or vertical motion
    pw_climo_flag = prof.pwv_flag
    pwat = prof.pwat
    upshear = utils.comp2vec(prof.upshear_downshear[0],prof.upshear_downshear[1])
    if pw_climo_flag >= 2 and upshear[1] < 25:
        watch_types.append("FLASH FLOOD")
        colors.append("#5FFB17")
    #elif pwat > 1.3 and upshear[1] < 25:
    #    watch_types.append("FLASH FLOOD")
    #    colors.append("#5FFB17")
    
    # Blizzard Watch if sfc winds > 35 mph and precip type detects snow
    sfc_wspd = utils.KTS2MPH(prof.wspd[prof.get_sfc()])
    if sfc_wspd > 35. and prof.tmpc[prof.get_sfc()] <= 32:
        watch_types.append("BLIZZARD")
        colors.append("#3366FF")
    # Winter Storm Watch if precip type is snow, ice, or sleet
    
    # Wind Chill Watch (if wind chill gets below -20 F)
    if wind_chill(prof) < -20.:
        watch_types.append("WIND CHILL")
        colors.append("#3366FF")
    
    # Fire WX Watch (sfc RH < 30% and sfc_wind speed > 15 mph)
    if sfc_wspd > 15. and thermo.relh(prof.pres[prof.get_sfc()], prof.tmpc[prof.get_sfc()], prof.tmpc[prof.get_sfc()]) < 30. :
        watch_types.append("FIRE WEATHER")
        colors.append("#FF9900")
    
    # Excessive Heat Watch (if Max_temp > 105 F and sfc dewpoint > 75 F)
    if thermo.ctof(prof.dwpc[prof.get_sfc()]) > 75. and thermo.ctof(params.max_temp(prof)) >= 105.:
        watch_types.append("EXCESSIVE HEAT")
        colors.append("#CC33CC")
    
    # Freeze Watch (checks to see if dewpoint is below freezing and temperature isn't and wind speeds are low)
    if thermo.ctof(prof.dwpc[prof.get_sfc()]) < 32. and thermo.ctof(prof.tmpc[prof.get_sfc()]) > 40. and prof.wspd[prof.get_sfc()] < 5.:
        watch_types.append("FREEZE")
        colors.append("#3366FF")
    
    watch_types.append("NONE")
    colors.append("#FFCC33")
    
    return np.asarray(watch_types), np.asarray(colors)

