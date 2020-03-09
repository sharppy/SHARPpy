import sharppy.io.spc_decoder as spc_decoder
import sharppy.sharptab.profile as profile
import sharppy.sharptab as tab
import numpy.testing as npt
import numpy as np

files = ['examples/data/14061619.OAX', 'examples/data/14072800.BNA']

def getProf(fname):
    dec = spc_decoder.SPCDecoder(fname)
    profs = dec.getProfiles()
    stn_id = dec.getStnId()

    all_profs = profs._profs
    prof = all_profs[''][0]
    dates = profs._dates
    prof = profile.create_profile(pres=prof.pres, hght=prof.hght, tmpc=prof.tmpc, dwpc=prof.dwpc, wspd=prof.wspd, \
                                      wdir=prof.wdir, strictQC=False, profile='convective', date=dates[0])
    return prof

profs = []
for f in files:
    profs.append(getProf(f))

def test_lapse_rate():
    prof = profs[0]
    # Values from SHARP
    assert round(tab.params.lapse_rate(prof, 0, 3000, pres=False),1) == 6.6
    assert round(tab.params.lapse_rate(prof, 3000, 6000, pres=False),1) == 8.6
    assert round(tab.params.lapse_rate(prof, 850, 500, pres=True),1) == 7.8
    assert round(tab.params.lapse_rate(prof, 700, 500, pres=True),1) == 8.8

def test_pwat():
    prof = profs[0]
    assert round(tab.params.precip_water(prof), 2) == 1.53 # Value from SHARP

def test_kindex():
    prof = profs[0]
    assert round(tab.params.k_index(prof), 0) == 37 # Value from SHARP

def test_mmp():
    prof = profs[0]
    assert round(tab.params.mmp(prof),2) == 1 # Value from SHARP

def test_wndg():
    prof = profs[0]
    assert round(tab.params.wndg(prof), 1) == 0.0 # Value from SHARP
    prof = profs[1]
    npt.assert_almost_equal(tab.params.wndg(prof),2.18739090) # Value from SHARP

def test_convT():
    prof = profs[0]
    assert round(tab.thermo.ctof(tab.params.convective_temp(prof)), 0) == 90 # Value from SHARP
    #prof = profs[1]

def test_maxT():
    prof = profs[1]
    assert round(tab.params.max_temp(prof),5) == 34.60104

def test_parcels():
    prof = profs[0]
    # Values from SHARP online
    truth_pcls = {'sfcpcl': [5765, -1, 513, -14, 613],\
                  'mlpcl': [4203, -58, 1003, -11, 2393],\
                  'mupcl': [5765, -1, 513, -14, 613],\
                  'fcstpcl': [5206, 0, 1495, -13, 1699]}

    for key in truth_pcls.keys():
        pcl = getattr(prof, key)
        returned = [round(pcl.bplus), round(pcl.bminus), round(pcl.lclhght), round(pcl.li5,0), round(pcl.lfchght,0)]
        #print(truth_pcls[key])
        #print(returned)
        bias = np.array(truth_pcls[key]) - np.array(returned)
        assert np.abs(bias).max() < 10

def test_composite_severe():
    prof = profs[0]
    assert tab.params.stp_fixed(0,0,0,0) == 0
    assert tab.params.stp_cin(0,0,0,0,0) == 0
    assert tab.params.stp_fixed(0,3000,0,0) == 0
    assert tab.params.scp(0,0,0) == 0
    assert round(tab.params.ship(prof),1) == 4.9 # Value from SHARP
    prof = profs[1]
    assert round(tab.params.ship(prof), 1) == 1.7 # Value from SHARP
    assert round(prof.right_stp_fixed,1) == 1.9 # Value from SHARP
    assert round(prof.right_stp_cin,1) == 1.9 # Value from SHARP
    
def test_tei():
    prof = profs[0]
    assert round(tab.params.tei(prof),0) == 39 # Value from SHARP
    prof = profs[1]
    assert round(tab.params.tei(prof),0) == 44 # Value from SHARP

def test_sweat():
    prof = profs[0]
    assert round(tab.params.sweat(prof)) == 622

#def test_ehi():
#    print(prof.mlpcl.bplus)
#    print(tab.params.ehi(prof.mlpcl, 0, 3000))

def test_mburst():
    prof = profs[0]
    assert tab.params.mburst(prof) == 11

def test_sherb():
    prof = profs[0]
    assert round(tab.params.sherb(prof),1) == 1.8 
    prof = profs[1]
    assert round(tab.params.sherb(prof, effective=1), 1) == 1.5 # Value from SHARP 

#test_sweat()
#test_maxT()
#test_ehi()
#test_mburst()
#test_sherb()

#test_tei()
##test_convT()
#test_wndg()
#test_mmp()
#test_parcels()
#test_kindex()
#test_pwat()    
#test_lapse_rate()
