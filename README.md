SHARPpy
=======
Sounding/Hodograph Analysis and Research Program in Python

This is primarily tested and used with the Anaconda Python Distribution
from Continuum Analytics. Anaconda can be downloaded here:
https://store.continuum.io/cshop/anaconda/

To install the SHARPpy package into your Python path, type:

python setup.py install

To run the SHARPpy GUI, you will need both Numpy and PySide installed
with your Python distribution.  To run the gui, copy the runsharp folder
to the location at which you wish to run the program. Navigate to that
folder in your terminal and run the following command:

python full_gui.py

Known Windows Issues:
- Inset text is not properly sized or placed in their windows.
- When incrementing/decrementing profiles, the entire screen goes blank and redraws
- The program’s menu bar does not display
- The sounding window may not properly size at first. A fix is to manually resize it and manipulate it.

Other Issues:
- Multi-select does not work for Observed soundings
- Some forecast sounding (HRRR, NAM, etc.) point-click locations do not exist on the data server. This will cause the program to crash.
