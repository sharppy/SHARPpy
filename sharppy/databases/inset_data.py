import numpy as np
"""
    Contains the data to generate the plots in certain insets.
"""

def sherbData():
    # FOR THE STP INSET BOX/WHISKE
    # From Thompson et al. 2012 WAF
    sherb_ytexts = ['2.5', '2', '1.5', '1', '0.5', '0', ' ']
    sherb_xtexts = ['3SIG', '3SIGTOR', '3NULL', 'ESIG', 'ESIGTOR', 'ENULL']
    sherb = [[0.25, 0.8, 1.02, 1.25, 1.95], #3SIG
    [0.6, 1.0, 1.2, 1.4, 1.8], #3SIGTOR
    [0.1, 0.6, 0.8, 1.05, 1.6], #3NULL
    [0.0, 0.6, 1.0, 1.35, 2.3], #ESIG
    [0.2, 1.0, 1.25, 1.55, 2.0], # ESIGTOR
    [0.0, 0.4, 0.75, 1.0, 1.95]] # ENULL
    sherb = np.array(sherb)
    stp_inset_data = {}
    stp_inset_data['sherb_ytexts'] = sherb_ytexts
    stp_inset_data['sherb_xtexts'] = sherb_xtexts
    stp_inset_data['sherb'] = sherb    
    return stp_inset_data

def shipData():
    # FOR THE SHIP INSET BOX/WHISKER
    # Developed interally by Ryan Jewell (SPC)
    ship_ytexts = ['5', '4', '3', '2', '1', '0', ' ']
    ship_xtexts = ['<= 1.5\"', '>= 2.5\"']
    ship_dist = [[0.2, 0.3, 0.2, 0.9, 1.2],
                 [1.1, 1.4, 0.8, 2.8, 4.0]] # <= 1.5"
    ship_dist = np.array(ship_dist)
    ship_inset_data = {}
    ship_inset_data['ship_xtexts'] = ship_xtexts
    ship_inset_data['ship_ytexts'] = ship_ytexts
    ship_inset_data['ship_dist'] = ship_dist

    return ship_inset_data

def stpData():
    # FOR THE STP INSET BOX/WHISKER
    # From Thompson et al. 2012 WAF
    stp_ytexts = ['11', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']
    stp_xtexts = ['EF4+', 'EF3', 'EF2', 'EF1', 'EF0', 'NONTOR']
    ef = [[1.2, 2.6, 5.3, 8.3, 11.0], #ef4
    [0.2, 1.0, 2.4, 4.5, 8.4], #ef3
    [0.0, 0.6, 1.7, 3.7, 5.6], #ef2
    [0.0, 0.3, 1.2, 2.6, 4.5], #ef1
    [0.0, 0.1, 0.8, 2.0, 3.7], # ef-0
    [0.0, 0.0, 0.2, 0.7, 1.7]] #nontor
    ef = np.array(ef)
    stp_inset_data = {}
    stp_inset_data['stp_ytexts'] = stp_ytexts
    stp_inset_data['stp_xtexts'] = stp_xtexts
    stp_inset_data['ef'] = ef

    return stp_inset_data

def condSTPData():
    # For the CONDITIONAL STP VS EF INSET (LINE PLOT)
    # Provided by Bryan Smith (SPC) and Rich Thompson (SPC)
    ef1plus = np.asarray([15.3, 28.0, 36.1, 47.8, 52.3, 54.4, 60.3, 61.6, 61.2, 73.2, 73.4])
    ef2plus = np.asarray([2.7, 6.6, 6.5, 13.8, 14.9, 17.5, 21.8, 31.5, 33.3, 46.2, 53.1])
    ef3plus = np.asarray([0, 1.2, 1.2, 2.7, 2.7, 4.1, 7.3, 10.0, 13.2, 25.8, 39.1])
    ef4plus = np.asarray([0, 0, 0, 0, 0.2, .1, 1.5, 2.3, 6.2, 9.7, 17.2])
    xtexts = ['0', '.01-.49', '.5-.99', '1-1.99', '2-2.99', '3-3.99', '4-5.99', '6-7.99', '8-9.99', '10-11.99', '>12']
    xticks = ['0', '.01-.5', '.5-1', '1-2', '2-3', '3-4', '4-6', '6-8', '8-10', '10-12', '>12']
    ytexts = [' ', '0', '10', '20', '30', '40', '50', '60', '70'][::-1]
    condSTP_inset_data = {}
    condSTP_inset_data['xtexts'] = xtexts
    condSTP_inset_data['ytexts'] = ytexts
    condSTP_inset_data['xticks'] = xticks
    condSTP_inset_data['EF1+'] = ef1plus
    condSTP_inset_data['EF2+'] = ef2plus
    condSTP_inset_data['EF3+'] = ef3plus
    condSTP_inset_data['EF4+'] = ef4plus

    return condSTP_inset_data

def vrotData():
    # For the VROT plot
    # Provided by Bryan Smith (SPC) and Rich Thompson (SPC)
    xtexts = ['0-9.9', '10-19.9', '20-29.9', '30-39.9', '40-49.9', '50-59.9', '60-69.9', '70-79.9', '80-89.9', '90-99.9', '100-109.9']
    ytexts = [' ', '0', '10', '20', '30', '40', '50', '60', '70'][::-1]
    xpts = np.arange(5, 115, 10)
    ef01 = [100.0, 98.6, 95.3, 91.0, 80.2, 61.9, 42.1, 29.1, 16.3, 5.6, 0.0]
    ef23 = [0.0, 1.0, 4.7, 9.0, 19.3, 36.5, 51.1, 62.8, 65.1, 50.0, 25.0]
    ef45 = [0.0, 0.0, 0.0, 0.0, 0.5, 1.6, 6.8, 8.1, 18.6, 44.4, 75.0]
    vrot_inset_data = {}
    vrot_inset_data['xpts'] = xpts
    vrot_inset_data['xtexts'] = xtexts
    vrot_inset_data['ytexts'] = ytexts
    vrot_inset_data['EF0-EF1'] = ef01
    vrot_inset_data['EF2-EF3'] = ef23
    vrot_inset_data['EF4-EF5'] = ef45
    return vrot_inset_data
