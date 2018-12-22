import os
import pytest

@pytest.mark.skipif("DISPLAY_AVAIL" in os.environ and os.environ["DISPLAY_AVAIL"] == 'NO', reason="DISPLAY not set")
def test_main_entry_pt():
    os.system('python runsharp/full_gui.py examples/data/14061619.OAX')

