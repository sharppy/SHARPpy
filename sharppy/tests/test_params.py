import sharppy.io.spc_decoder as spc_decoder
import sharppy.sharptab.profile as profile
import sharppy.sharptab as tab
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

def test_lapse_rate():
    assert round(tab.params.lapse_rate(prof, 0, 3000, pres=False),1) == 6.6
    assert round(tab.params.lapse_rate(prof, 3000, 6000, pres=False),1) == 8.6
    assert round(tab.params.lapse_rate(prof, 850, 500, pres=True),1) == 7.8
    assert round(tab.params.lapse_rate(prof, 700, 500, pres=True),1) == 8.8

def test_pwat():
    assert round(tab.params.precip_water(prof), 2) == 1.53

def test_kindex():
    assert round(tab.params.k_index(prof), 0) == 37

def test_mmp():
    assert round(tab.params.mmp(prof),2) == 1

def test_wndg():
    assert round(tab.params.wndg(prof), 1) == 0.0

def test_convT():
    assert round(tab.thermo.ctof(tab.params.convective_temp(prof)), 0) == 90

#def test_maxT():
#    assert round(tab.thermo.

def test_parcels():
    sfc_truth = [5765, -1, 513, -14, 613]
    pcl = prof.sfcpcl
    sfc_returned = [round(pcl.bplus), round(pcl.bminus), round(pcl.lclhght), round(pcl.li5,0), round(pcl.lfchght,0)]
    print(sfc_truth)
    print(sfc_returned)

def test_composite_severe():
    assert tab.params.stp_fixed(0,0,0,0) == 0
    assert tab.params.stp_cin(0,0,0,0,0) == 0
    assert tab.params.stp_fixed(0,3000,0,0) == 0
    assert tab.params.scp(0,0,0) == 0
    assert round(tab.params.ship(prof),1) == 4.9
    
def test_tei():
    assert round(tab.params.tei(prof),0) == 39

def test_sweat():
    assert round(tab.params.sweat(prof)) == 622

#def test_ehi():
#    print(prof.mlpcl.bplus)
#    print(tab.params.ehi(prof.mlpcl, 0, 3000))

def test_mburst():
    assert tab.params.mburst(prof) == 11

def test_sherb():
    assert round(tab.params.sherb(prof),1) == 1.8



test_sweat()
#test_ehi()
test_mburst()
test_sherb()

test_tei()
test_convT()
test_wndg()
test_mmp()
test_parcels()
test_kindex()
test_pwat()    
test_lapse_rate()
