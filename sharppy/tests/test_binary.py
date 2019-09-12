import os
import sys
import pytest
import glob
import sharppy.databases.sars as sars
import numpy as np
#from PySide import QtGui
full_gui = pytest.importorskip('runsharp.full_gui') 

#@pytest.mark.skipif(QtGui.QX11Info.display())
@pytest.mark.skipif("DISPLAY_AVAIL" in os.environ and os.environ["DISPLAY_AVAIL"] == 'NO', reason="DISPLAY not set")
def test_main_entry_pt():
    #sys.argv = []
    #print(full_gui.sys.argv)
    #full_gui.sys.argv.append('examples/data/14061619.OAX')
    hail_files = glob.glob(sars.get_sars_dir('hail') + '*')
    supercell_files = glob.glob(sars.get_sars_dir('supercell') + '*')
    #print(hail_files + supercell_files)
    sars_files = np.asarray(hail_files + supercell_files)
    idx = np.random.randint(0, len(sars_files), 10)
    files = list(sars_files[idx]) + ['examples/data/14061619.OAX']
    print(files)
    full_gui.test(files)

    
#test_main_entry_pt()

