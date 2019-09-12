import numpy as np
import os
#import sharppy.io.spc_decoder as spc_decoder

## original database and code provided by
## Ryan Jewell - NOAA Storm Prediction Center (hail)
## Rich Thompson - NOAA Storm Prediction Center (supercell)

## Routines implemented in Python by Greg Blumberg - CIMMS and Kelton Halbert (OU SoM)
## wblumberg@ou.edu, greg.blumberg@noaa.gov, kelton.halbert@noaa.gov, keltonhalbert@ou.edu

def supercell(database_fn, mlcape, mllcl, h5temp, lr, shr, srh, shr3k, shr9k, srh3):
    '''
    The SARS Supercell database was provided by Rich Thompson of the 
    NOAA Storm Prediction Center in Norman, Oklahoma. This is a database
    of observed and model proximity soundings to both tornadic and 
    nontornadic supercell thunderstorms.
    
    This function works by searching for matches to particular variables
    in the database that have been found to be useful in forecasting 
    supercell thunderstorms. It searches through the database to find 
    matches to a given sounding within a range of uncertainty that
    has been tested internally in SPC to provide the best analogues
    possible. There is a loose criteria that is used to get probabilities,
    and there is a tighter criteria for quality matches that are supposed to
    be similar to the given sounding.
    
    The loose matches are based on the mixed layer cape (mlcape), mixed layer
    lcl (mllcl), 0-1km shear (shr), 0-1km storm relative helicity (srh), 500mb
    temperature (h5temp), and the 700-500mb lapse rate (lr).
    
    The ranges for the loose matches are set as such:
        mlcape: +/- 1300 J/kg
        mllcl: +/- 500 m
        shr: +/- 14 kts
        srh < 50 m^2/s^2: +/- 100 m^2/s^2
        srh >= 50 m^2/s^2: +/- 100% m^2/s^2
        h5temp: +/- 7.0 C
        lr: +/-1.0 C/km
    
    The quality matches are based on the same variables as the loose matches,
    with the addition of the 0-3km shear (shr3k), 0-9km shear (shr9k), and the
    0-3km Storm Relative Helicity (srh3).
    
    The ranges for the quality matches are set as such:
        mlcape: +/- 25% J/kg
        mllcl: +/- 200 m
        shr: +/- 10 kts
        srh < 100 m^2/s^2: +/- 50 m^2/s^2
        srh >= 100 m^2/s^2: +/- 30% m^2/s^2
        srh3 < 100 m^2/s^2: +/- 50 m^2/s^2
        srh3 >= 100 m^2/s^2: +/- 50% m^s/s^2
        h5temp: +/- 5 C
        lr: +/- 0.8 C/km
        shr3k: +/- 15 kts
        shr9k: +/- 25 kts
        
    Parameters
    ----------
    database_fn - filename of the database
    mlcape - the mixed layer cape (J/kg)
    mllcl - the mixed layer LCL (m)
    h5temp - the 500mb temp (C)
    lr - the 700-500mb lapse rate (C/km)
    shr - the 0-1km shear (kts)
    srh - the 0-1km storm relative helicity (m^2/s^2)
    shr3k - the 0-3km shear (kts)
    shr9k - the 0-9km shear (kts)
    srh3 - the 0-3km storm relative helicity (m^2/s^2)
    
    Returns
    -------
    quality_match_soundings: The dates/locations of the quality matches
    quality_match_tortype: The type of quality match (SIGTOR/WEAKTOR/NONTOR)
    len(loose_match_idx):  The number of loose matches
    num_matches: The number of weak and sig matches in the loose matches
    tor_prob: SARS sig. tornado probability
    '''
    # Open and read the file
    database_fn = os.path.join( os.path.dirname( __file__ ), database_fn)
    supercell_database = np.loadtxt(database_fn, skiprows=1, dtype=bytes, comments="%%%%")

    # Set range citeria for matching soundings
    # MLCAPE ranges
    if mlcape == 0:
        range_mlcape = 0
    else:
        range_mlcape = 1300 # J/kg
    range_mlcape_t1 = mlcape * 0.25 # J/kg

    # MLLCL ranges
    range_mllcl = 500 # m
    range_mllcl_t1 = 200 # m

    # 0-6 km shear ranges (kts)
    range_shr = 14
    range_shr_t1 = 10

    # 0-1 km SRH Ranges (m2/s2)
    if np.abs(srh) < 50:
        range_srh = 100.
    else:
        range_srh = srh

    if np.abs(srh) < 100:
        range_srh_t1 = 50
    else:
        range_srh_t1 = np.abs(srh) * 0.30

    # 0-3 SRH tier 1 ranges (m2/s2)
    if np.abs(srh3) < 100:
        range_srh3_t1 = 50.
    else:
        range_srh3_t1 = np.abs(srh3) * 0.50

    # 500 mb temperature ranges
    range_temp = 7 # C
    range_temp_t1 = 5 # C

    # 700-500 mb lapse rate ranges (C/km)
    range_lr = 1.0
    range_lr_t1 = 0.8

    # 3 km and 9 km shear matching
    range_shr3k_t1 = 15
    range_shr9k_t1 = 25
    ## Read in the columns for each variable
    mat_category = np.asarray(supercell_database[:,1], dtype=float) # category of match (0=non, 1=weak, 2=sig)
    mat_mlcape = np.asarray(supercell_database[:,3], dtype=float)
    mat_mllcl = np.asarray(supercell_database[:,5], dtype=float)
    mat_shr = np.asarray(supercell_database[:,7], dtype=float) # 0-6 KM SHEAR
    mat_srh = np.asarray(supercell_database[:,6], dtype=float) # 0-1 KM SRH
    mat_srh3 = np.asarray(supercell_database[:,14], dtype=float) # 0-3 KM SRH
    mat_h5temp = np.asarray(supercell_database[:,9], dtype=float) # 500 MB TEMP C
    mat_lr75 = np.asarray(supercell_database[:,11], dtype=float) # 700-500 MB LAPSE RATE
    mat_shr3 = np.asarray(supercell_database[:,12], dtype=float) # 0-3 KM SHEAR
    mat_shr9 = np.asarray(supercell_database[:,13], dtype=float) # 0-9 KM SHEAR
    ## Get the loose matches
    loose_match_idx = np.where((mlcape >= (mat_mlcape - range_mlcape)) & (mlcape <= (mat_mlcape + range_mlcape)) & \
                               (mllcl >= (mat_mllcl - range_mllcl)) & (mllcl <= (mat_mllcl + range_mllcl)) & \
                               (shr >= (mat_shr - range_shr)) & (shr <= (mat_shr + range_shr)) & \
                               (srh >= (mat_srh - range_srh)) & (srh <= (mat_srh + range_srh)) & \
                               (h5temp >= (mat_h5temp - range_temp)) & (h5temp <= (mat_h5temp + range_temp)) & \
                               (lr >= (mat_lr75 - range_lr)) & (lr <= (mat_lr75 + range_lr)))[0]

    num_matches = len(np.where(mat_category[loose_match_idx] > 0)[0]) #number of weak and sig matches in the loose matches

    ## Probability for tornado - needs to check to avoid zero division
    if len(loose_match_idx) > 0. and mlcape > 0:
        tor_prob = num_matches / float(len(loose_match_idx))
    else:
        tor_prob = 0.

    # Tier 1 matches (also known as the quality matches)
    quality_match_idx = np.where((mlcape >= (mat_mlcape - range_mlcape_t1)) & (mlcape <= (mat_mlcape + range_mlcape_t1)) & \
                               (mllcl >= (mat_mllcl - range_mllcl_t1)) & (mllcl <= (mat_mllcl + range_mllcl_t1)) & \
                               (shr >= (mat_shr - range_shr_t1)) & (shr <= (mat_shr + range_shr_t1)) & \
                               (srh >= (mat_srh - range_srh_t1)) & (srh <= (mat_srh + range_srh_t1)) & \
                               (h5temp >= (mat_h5temp - range_temp_t1)) & (h5temp <= (mat_h5temp + range_temp_t1)) & \
                               (lr >= (mat_lr75 - range_lr_t1)) & (lr <= (mat_lr75 + range_lr_t1)) & \
                               (shr3k >= (mat_shr3 - range_shr3k_t1)) & (shr3k <= (mat_shr3 + range_shr3k_t1)) & \
                               (shr9k >= (mat_shr9 - range_shr9k_t1)) & (shr9k <= (mat_shr9 + range_shr9k_t1)) & \
                               (srh3 >= (mat_srh3 - range_srh3_t1)) & (srh3 <= (mat_srh3 + range_srh3_t1)))[0]

    quality_match_soundings = supercell_database[:,0][quality_match_idx]
    quality_match_tortype = np.asarray(supercell_database[:,1][quality_match_idx], dtype='|S7')

    np.place(quality_match_tortype, quality_match_tortype==b'2', 'SIGTOR')
    np.place(quality_match_tortype, quality_match_tortype==b'1', 'WEAKTOR')
    np.place(quality_match_tortype, quality_match_tortype==b'0', 'NONTOR')

    quality_match_soundings = np.array([ qms.decode('utf-8') for qms in quality_match_soundings ])
    quality_match_tortype = np.array([ qmt.decode('utf-8') for qmt in quality_match_tortype ])

    return quality_match_soundings, quality_match_tortype, len(loose_match_idx), num_matches, tor_prob





def hail(database_fn, mumr, mucape, h5_temp, lr, shr6, shr9, shr3, srh):
    '''
    The SARS Hail database was provided by Ryan Jewell of the NOAA Storm
    Prediction Center in Norman, Oklahoma. This is a database of observed
    and model proximity analogue soundings to hail events.
    
    This function works by searching for matches to particular variables in 
    the database that have been attributed to hail events given a certain 
    range of uncertainty. The loose matches are used for statistics such as
    % significant hail matches, and are based on a looser criteria for
    matches. The analogues that get displayed are based on a tighter criteria
    for matches to insure that only quality matches are received. Ranges for
    loose and quality matches are semi-arbitrary, and were tuned by testing
    internally by SPC.
    
    The loose matches are based on the most unstable parcel mixing ratio (mumr),
    most unstable cape (mucape), 700-500mb labse rate (lr), 500mb temperature
    (h5_temp), 0-3km shear (shr3), 0-6km shear (shr6), and the 0-9km shear (shr9).
    
    The ranges for the loose matches are set as such:
        mumr: +/- 2.0 g/kg
        mucape: +/- 30% J/kg
        lr: +/- 2.0 C/km
        h5_temp: +/- 9.0 C
        shr6: +/- 12 m^2/s^2
        shr9: +/- 22 m^2/s^2
        shr3: +/- 10 m^2/s^2
    
    The quality matches use the fields described in the loose matches, plus the
    0-3km Storm Relative Helicity (srh). The bounds for the search for quality 
    matches is much more strict that the loose matches.
    
    The ranges for the quality matches are set as such:
        mumr: +/- 2.0 g/kg
        mucape < 500 J/kg: +/- 50% J/kg
        mucape < 2000 J/kg: +/- 25% J/kg
        mucape >= 2000 J/kg: +/- 20% J/kg
        lr: +/- 0.4 C/km
        h5_temp: +/- 1.5 C/km
        shr6: +/- 6 m^2/s^2
        shr9: +/- 15 m^2/s^2
        shr3: +/- 8 m^2/s^2
        srh < 50 m^2/s^2: +/- 25 m^2/s^2
        srh >= 50 m^2/s^2: +/- 50% m^2/s^2
    
    Parameters
    ----------
    mumr - most unstable parcel mixing ratio (g/kg)
    mucape - most unstable CAPE (J/kg)
    h5_temp - 500 mb temperature (C)
    lr - 700-500 mb lapse rate (C/km)
    shr6 - 0-6 km shear (m/s)
    shr9 - 0-9 km shear (m/s)
    shr3 - 0-3 km shear (m/s)
    srh - 0-3 Storm Relative Helicity (m2/s2)
    
    Returns
    -------
    quality_match_dates (str) - dates of the quality matches
    quality_match_sizes (float) - hail sizes of the quality matches
    num_loose_matches (int) - number of loose matches
    num_sig_reports (int) - number of significant hail reports (>= 2 inches)
    prob_sig_hail (float) - SARS sig. hail probability
    
    '''
    ## open the file in the current directory with the name database_fn
    database_fn = os.path.join( os.path.dirname( __file__ ), database_fn )
    hail_database = np.loadtxt(database_fn, skiprows=1, dtype=bytes)

    #Set range criteria for matching sounding
    # MU Mixing Ratio Ranges
    range_mumr = 2.0 # g/kg
    range_mumr_t1 = 2.0 # g/kg

    # MUCAPE Ranges (J/kg)
    range_mucape = mucape*.30
    if mucape < 500.:
        range_mucape_t1 = mucape * .50
    elif mucape >= 500. and mucape < 2000.:
        range_mucape_t1 = mucape * .25
    else:
        range_mucape_t1 = mucape * .20

    # 700-500 mb Lapse Rate Ranges
    range_lr = 2.0 # C/km
    range_lr_t1 = 0.4 # C/km

    # 500 mb temperature ranges
    range_temp = 9 # C
    range_temp_t1 = 1.5 # C

    # 0-6 km shear ranges
    range_shr6 = 12 # m/s
    range_shr6_t1 = 6 # m/s

    # 0-9 km shear ranges

    range_shr9 = 22 # m/s
    range_shr9_t1 = 15 # m/s

    # 0-3 km shear ranges
    range_shr3 = 10
    range_shr3_t1 = 8

    # 0-3 SRH Ranges
    range_srh = 100
    if srh < 50:
        range_srh_t1 = 25
    else:
        range_srh_t1 = srh * 0.5

    #Get database variables from the columns in the file and make them floats
    matmr = np.asarray(hail_database[:,4], dtype=float) # MU Mixing Ratio
    matcape = np.asarray(hail_database[:,3], dtype=float) # MUCAPE
    matlr = np.asarray(hail_database[:,7], dtype=float) # 700-500 mb lapse rate
    mattemp = np.asarray(hail_database[:,5], dtype=float) # 500 mb temp
    matshr6 = np.asarray(hail_database[:,10], dtype=float) # 0-6 shear
    matshr9 = np.asarray(hail_database[:,11], dtype=float) # 0-9 shear
    matshr3 = np.asarray(hail_database[:,9], dtype=float) # 0-3 shear
    matsrh = np.asarray(hail_database[:,12], dtype=float) # 0-3 SRH

    # Find the loose matches using the ranges set above
    loose_match_idx = np.where((mumr >= (matmr - range_mumr)) & (mumr <= (matmr + range_mumr)) & \
                               (mucape >= (matcape - range_mucape)) & (mucape <= (matcape + range_mucape)) & \
                               (lr >= (matlr - range_lr)) & (lr <= (matlr + range_lr)) & \
                               (h5_temp >= (mattemp - range_temp)) & (h5_temp <= (mattemp + range_temp)) & \
                               (shr6 >= (matshr6 - range_shr6)) & (shr6 <= (matshr6 + range_shr6)) & \
                               (shr9 >= (matshr9 - range_shr9)) & (shr9 <= (matshr9 + range_shr9)) & \
                               (shr3 >= (matshr3 - range_shr3)) & (shr3 <= (matshr3 + range_shr3)))[0]
    ## How many loose matches are there?
    num_loose_matches = float(len(loose_match_idx))
    ## What were the sizes of those matches?
    hail_sizes = np.asarray(hail_database[:,2], dtype=float)
    ## How many of them were significant (>2.0 in)?
    num_sig_reports = float(len(np.where(hail_sizes[loose_match_idx] >= 2.)[0]))

    ## Calculate the Probability of significant hail - must make sure
    ## loose matches are > 0 to prevent division by 0.
    if num_loose_matches > 0 and mucape > 0:
        prob_sig_hail = num_sig_reports / num_loose_matches
        # Calculate the average hail size from the loose matches
        avg_hail_size = np.mean(hail_sizes[loose_match_idx])
    else:
        prob_sig_hail = 0

    # Find the quality matches
    quality_match_idx = np.where((mumr >= (matmr - range_mumr_t1)) & (mumr <= (matmr + range_mumr_t1)) & \
                               (mucape >= (matcape - range_mucape_t1)) & (mucape <= (matcape + range_mucape_t1)) & \
                               (lr >= (matlr - range_lr_t1)) & (lr <= (matlr + range_lr_t1)) & \
                               (h5_temp >= (mattemp - range_temp_t1)) & (h5_temp <= (mattemp + range_temp_t1)) & \
                               (shr6 >= (matshr6 - range_shr6_t1)) & (shr6 <= (matshr6 + range_shr6_t1)) & \
                               (shr9 >= (matshr9 - range_shr9_t1)) & (shr9 <= (matshr9 + range_shr9_t1)) & \
                               (shr3 >= (matshr3 - range_shr3_t1)) & (shr3 <= (matshr3 + range_shr3_t1)) & \
                               (srh >= (matsrh - range_srh_t1)) & (srh <= (matsrh + range_srh_t1)))[0]

    quality_match_dates = hail_database[quality_match_idx,0]
    quality_match_sizes = np.asarray(hail_database[quality_match_idx,2], dtype=float)

    # This filtering was in the sars.f file so the graphical output wasn't overrun by historical quality matches
    max_quality_matches = 15
    quality_match_dates = quality_match_dates[:max_quality_matches]
    quality_match_sizes = quality_match_sizes[:max_quality_matches]

    quality_match_dates = np.array([ qmd.decode('utf-8') for qmd in quality_match_dates ])

    return quality_match_dates, quality_match_sizes, num_loose_matches, num_sig_reports, prob_sig_hail


def get_sars_dir(match_type):
    """
    Returns the directory where the raw SARS files are.
    
    Parameters
    ----------
    match_type : str
        'supercell' or 'hail'
    Returns
    -------
    string

    """
    return os.path.join(os.path.dirname(__file__), "sars/" + match_type.lower() + "/")

## written by Kelton Halbert
def getSounding(match_string, match_type, profile="default"):
    """
    Given a match string and type (supercell:hail) from one of the
    SARS routines, decode the raw sounding data into a Profile
    object and return said object. It will default to a "default"
    profile object that does not compute any indices, but can be
    set to profile="convective" if indices are desired.

    :param match_string:
    :param match_type:
    :return: a Profile object
    """
    ## make sure the requested match type is valid
    #if (match_type.lower() != "supercell") or (match_type.lower() != "hail"):
    #    raise Exception("InvalidSARSType", match_type.lower() + " is an invalid SARS type.")
    ## get the directory with the data
    data_dir = get_sars_dir(match_type)

    match_date, match_loc = match_string.split(".")
    files = os.listdir(data_dir)
    for file in files:
        if file.startswith(match_date) and file.endswith(match_loc.lower()):
            datafile = data_dir + file
            break
        elif file.startswith(match_date) and file.endswith(match_loc.upper()):
            datafile = data_dir + file
            break
    return datafile

