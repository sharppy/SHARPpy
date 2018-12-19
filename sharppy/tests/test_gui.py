from PySide import QtGui, QtCore
import sharppy.viz as viz
from sharppy.io.spc_decoder import SPCDecoder

def test_insets():
    insets = [viz.fire.plotFire,
              viz.winter.plotWinter,
              viz.thermo.plotText,
              viz.kinematics.plotKinematics,
              viz.stp.plotSTP,
              viz.ship.plotSHIP,
              viz.vrot.plotVROT,
              viz.analogues.plotAnalogues,
              viz.stpef.plotSTPEF]
    names = ['fire', 'thermo', 'kinematics', 'stp', 'ship', 'vrot', 'sars', 'stpef']
    for inset, name in zip(insets, names):
        print("Testing:", str(inset))
        if inset is viz.thermo.plotText:
            test = inset(['SFC', 'ML', 'MU', 'FCST'])
        else:
            test = inset()
        try:
            test.setProf(prof)
        except:
            continue
        test.setGeometry(50,50,293,195)
        test.plotBitMap.save(name + '_test.png', format='png')
        del test

def test_main():
    skew = viz.skew.plotSkewT
    hodo = viz.hodo.plotHodo

    s = skew()
    s.addProfileCollection(prof_coll)
    s.setActiveCollection(0)
    s.plotBitMap.save('skew.png', format='png')

dec = SPCDecoder('../../examples/data/14061619.OAX')
prof_coll = dec.getProfiles()
prof = prof_coll.getCurrentProfs()['']
app_frame = QtGui.QApplication([])    
test_main()    
test_insets()

