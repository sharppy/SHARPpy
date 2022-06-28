
import fire_gui as gui
from multiprocessing import freeze_support
import os

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.getcwd()

if __name__ == "__main__":
    freeze_support()
    
    gui.main()

