import sharppy.io.spc_decoder as spc_decoder
import sharppy.sharptab.profile as profile
import sharppy.sharptab.watch_type as watch
import numpy.testing as npt
import numpy as np

files = ['examples/data/14061619.OAX']
dec = spc_decoder.SPCDecoder(files[0])
profs = dec.getProfiles()
stn_id = dec.getStnId()

all_profs = profs._profs
prof = all_profs[''][0]
dates = profs._dates
prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                  wdir=prof.wdir, strictQC=False, profile='convective', date=dates[0])

def test_heat_index():
    temps = np.array([104,100,92,92,86,80,80,60, 30])
    rh = np.array([55,65,60,90,90,75,40, 90, 50])
    correct_hi = np.array([137.361, 135.868, 104.684, 131.256, 105.294, 83.5751, 79.79, 59.965, 30.00])
    returned_hi = []
    for i in range(len(temps)):
        returned_hi.append(watch.heat_index(temps[i], rh[i]))
    returned_hi = np.asarray(returned_hi)
    npt.assert_almost_equal(returned_hi, correct_hi,0) 

def test_wind_chill():
    prof.tmpc[prof.sfc] = 0
    prof.wspd[prof.sfc] = 10
    assert round(watch.wind_chill(prof)) == 23

test_heat_index()
test_wind_chill() 
