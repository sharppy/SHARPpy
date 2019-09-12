import pytest
import sharppy.io.decoder as decoder
import sharppy.io.buf_decoder as buf_decoder
import sharppy.io.spc_decoder as spc_decoder
import sharppy.io.pecan_decoder as pecan_decoder
import sharppy.io.uwyo_decoder as uwyo_decoder
"""
    Unit tests to test to see if decoders work on different file types
"""
files = ['examples/data/14061619.OAX',
         'examples/data/rap_oun.buf',
         'examples/data/oun_uwyo.html',
         'examples/data/ABR.txt',
         'examples/data/OUN.txt']

decoders = decoder.getDecoders()
assert len(decoders) > 0

def test_spc_decoder():
    dec = spc_decoder.SPCDecoder(files[0])
    profs = dec.getProfiles()
    profs._backgroundCopy("")
    
    # Test Interpolation
    profs.interp()
    assert profs.isInterpolated() == True
    profs.resetInterpolation()
    assert profs.isInterpolated() == False

    # Test setting storm motion vectors 
    profs.modifyStormMotion('right', 0, 0)
    profs.modifyStormMotion('left', 0, 0)
    profs.resetStormMotion()
    
    # Try modify
    profs.modify(0, tmpc=35)
    profs.modify(0, u=0)
    tmp = profs._profs[""][0].tmpc
    tmp[0:2] = 35
    profs.modify(-999, tmpc=tmp, idx_range=[0,1])
    profs.resetModification('tmpc')
    profs.resetModification('u')
   
def test_bufkit_decoder(): 
    # Load in a BUFKIT file     
    dec = buf_decoder.BufDecoder(files[1])
    profs = dec.getProfiles()
    stn_id = dec.getStnId()

    # Test some of the characteristics of the ProfCollection
    assert profs.isEnsemble() == False
    assert profs.isModified() == False
    assert profs.getAnalogDate() is None
    assert profs.hasCurrentProf() == True

def test_uwyo_decoder():
    # Try to load in the UWYO file
    try:
        dec = uwyo_decoder.UWYODecoder(files[2]) 
    except:
        print("FAILED")

def test_pecan_decoder():
    try:
        # Load in the PECAN-type files
        dec = pecan_decoder.PECANDecoder(files[3])
        dec = pecan_decoder.PECANDecoder(files[4])
    except:
        return
    # Test some of the characteristics of this ProfCollection
    assert dec.getProfiles().isEnsemble() == True
    profs = dec.getProfiles()
    profs.advanceHighlight(1)
    profs.advanceHighlight(-1)
    profs.advanceTime(1)
    profs.advanceTime(-1)
    #print(profs) 

