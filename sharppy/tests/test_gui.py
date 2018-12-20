from PySide import QtGui, QtCore
import sharppy.viz as viz
import sharppy.viz.preferences as preferences
from sharppy.io.spc_decoder import SPCDecoder
import pytest
import os
import sys

""" plotText() and plotSkewT keep failing """
## Travis CI allows for a psuedo X-window editor to run if you are running
## a Linux image.  So that means that only on Linux can we run GUI tests
## This is problematic, as I haven't found a way to run tests on the macOS
## image, but skip these GUI tests.  For now we will just ignore these test
## overall.

def load_data():

    dec = SPCDecoder('../../examples/data/14061619.OAX')
    prof_coll = dec.getProfiles()
    prof = prof_coll.getCurrentProfs()['']
    app_frame = QtGui.QApplication([])    
    return prof, prof_coll, app_frame
    
#@pytest.mark.skipif(os.environ["OS"] == 'osx', reason="DISPLAY not set")
@pytest.mark.skipif(True, reason="DISPLAY not set")
def test_insets():
    prof, prof_coll, app = load_data()
    insets = [viz.fire.plotFire,
              viz.winter.plotWinter,
              viz.kinematics.plotKinematics,
              viz.stp.plotSTP,
              viz.ship.plotSHIP,
              viz.vrot.plotVROT,
              viz.analogues.plotAnalogues,
              viz.stpef.plotSTPEF]
    names = ['fire', 'kinematics', 'stp', 'ship', 'vrot', 'sars', 'stpef']
    for inset, name in zip(insets, names):
        print("Testing:", str(inset))
        if inset is viz.thermo.plotText:
            test = inset(['SFC', 'ML', 'MU', 'FCST'])
        else:
            test = inset()
        #try:
        test.setProf(prof)
        #except:
        #    continue
        test.setGeometry(50,50,293,195)
        test.plotBitMap.save(name + '_test.png', format='png')
        del test

#@pytest.mark.skipif(os.environ["OS"] == 'osx', reason="DISPLAY not set")
@pytest.mark.skipif(True, reason="DISPLAY not set")
def test_skew_hodo():
    prof, prof_coll, app = load_data()
    skew = viz.skew.plotSkewT
    hodo = viz.hodo.plotHodo

    s = hodo()
    s.addProfileCollection(prof_coll)
    s.setActiveCollection(0)
    s.plotBitMap.save('hodo.png', format='png')

    #s = skew()
    #s.addProfileCollection(prof_coll)
    #s.setActiveCollection(0)
    #s.plotBitMap.save('skew.png', format='png')

#@pytest.mark.skipif(os.environ["OS"] == 'osx', reason="DISPLAY not set")
@pytest.mark.skipif(True, reason="DISPLAY not set")
def test_other():
    prof, prof_coll, app = load_data()
    insets = [viz.speed.plotSpeed,
              viz.advection.plotAdvection,
              viz.watch.plotWatch,
              viz.srwinds.plotWinds,
              viz.slinky.plotSlinky,
              viz.thetae.plotThetae]
    names = ['speed', 'advection', 'watch', 'srwinds', 'slinky', 'thetae']
    for inset, name in zip(insets, names):
        print("Testing:", str(inset))
        test = inset()
        test.setProf(prof)
        test.setGeometry(50,50,293,195)
        test.plotBitMap.save(name + '_test.png', format='png')
        del test
    sys.exit(app.exec_())


