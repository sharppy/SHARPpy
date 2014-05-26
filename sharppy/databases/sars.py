import numpy as np
import os

## routine written by Greg Blumberg
## wblumberg@ou.edu

def sars_supercell():
    return

def sars_hail(database_fn, mumr, mucape, h5_temp, lr, shr6, shr9, shr3, srh):
    '''
        INPUT:
        mumr - most unstable parcel mixing ratio (g/kg)
        mucape - most unstable CAPE (J/kg)
        h5_temp - 500 mb temperature (C)
        lr - 700-500 mb lapse rate (C/km)
        shr6 - 0-6 km shear (m/s)
        shr9 - 0-9 km shear (m/s)
        shr3 - 0-3 km shear (m/s)
        srh - 0-3 Storm Relative Helicity (m2/s2)
    
        OUTPUT:
        quality_matches_dates - dates of the quality matches
        quality_matches_sizes - hail sizes of the quality matches
        num_loose_matches - number of loose matches
        num_sig_reports - number of significant hail reports (>= 2 inches)
        prob_sig_hail - SARS sig. hail probability
    '''
    database_fn = os.path.join( os.path.dirname( __file__ ), database_fn )

    hail_database = np.loadtxt(database_fn, skiprows=1, dtype=str)
    
    #Set range criteria for matching soundings
    
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

    #Get database variables and make them floats
    matmr = np.asarray(hail_database[:,4], dtype=float) # MU Mixing Ratio
    matcape = np.asarray(hail_database[:,3], dtype=float) # MUCAPE
    matlr = np.asarray(hail_database[:,7], dtype=float) # 700-500 mb lapse rate
    mattemp = np.asarray(hail_database[:,5], dtype=float) # 500 mb temp
    matshr6 = np.asarray(hail_database[:,10], dtype=float) # 0-6 shear
    matshr9 = np.asarray(hail_database[:,11], dtype=float) # 0-9 shear
    matshr3 = np.asarray(hail_database[:,9], dtype=float) # 0-3 shear
    matsrh = np.asarray(hail_database[:,12], dtype=float) # 0-3 SRH

    # Find the loose matches
    loose_match_idx = np.where((mumr >= (matmr - range_mumr)) & (mumr <= (matmr + range_mumr)) & \
                               (mucape >= (matcape - range_mucape)) & (mucape <= (matcape + range_mucape)) & \
                               (lr >= (matlr - range_lr)) & (lr <= (matlr + range_lr)) & \
                               (h5_temp >= (mattemp - range_temp)) & (h5_temp <= (mattemp + range_temp)) & \
                               (shr6 >= (matshr6 - range_shr6)) & (shr6 <= (matshr6 + range_shr6)) & \
                               (shr9 >= (matshr9 - range_shr9)) & (shr9 <= (matshr9 + range_shr9)) & \
                               (shr3 >= (matshr3 - range_shr3)) & (shr3 <= (matshr3 + range_shr3)))[0]

    num_loose_matches = float(len(loose_match_idx))
    hail_sizes = np.asarray(hail_database[:,2], dtype=float)
    num_sig_reports = float(len(np.where(hail_sizes[loose_match_idx] >= 2.)[0]))
    # Calculate the Probability of significant hail
    if num_loose_matches > 0:
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
    
    return quality_match_dates, quality_match_sizes, num_loose_matches, num_sig_reports, prob_sig_hail

