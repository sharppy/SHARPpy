import os
import sys
import pytest
import runsharp.full_gui as full_gui
#from runsharp import full_gui

@pytest.mark.skipif("DISPLAY_AVAIL" in os.environ and os.environ["DISPLAY_AVAIL"] == 'NO', reason="DISPLAY not set")
def test_main_entry_pt():
    #sys.argv = []
    #print(full_gui.sys.argv)
    #full_gui.sys.argv.append('examples/data/14061619.OAX')
    full_gui.test('examples/data/14061619.OAX')

#test_main_entry_pt()

