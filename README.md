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

=======================================================================

To open a sounding, select a sounding type, a model run time (if the type is an NWP model), and then select a time(s).
Afterwards, click on your desired location on the point and click map.  Once all of these are selected, click "Generate Profiles".

After all profiles have been generated, a window should show up with your desired data.  Below are things you can do:

1.) Advance through the profiles (if more than one is selected) using the left and right arrow keys.
2.) Change the hodograph cursor or point the hodograph window is centered on by right clicking on the hodograph.
3.) Modify the right 2 insets by right clicking on either one.  Different insets are available to help the user interrogate the data.

Insets available:
1.) SARS - Sounding Analog Retrieval System
2.) STP STATS - Information on the significant tornado parameter with CIN (STPC) associated with the sounding.
3.) SHIP - Distribution of expected hail sizes associated with the significant hail parameter (SHIP).
4.) STP COND - Conditional probablities for different tornado strengths based on STPC.
5.) WINTER - Information on precipitation type, melting and freezing in the profile, and the dendritic growth zone.
6.) FIRE - Fire weather information such as wind speed and humidity in the boundary layer.
7.) VROT - Conditional probabilities for different tornado strengths based on the 0.5 degree rotational velocity.



Known Windows Issues:
- Inset text is not properly sized or placed in their windows.
- When incrementing/decrementing profiles, the entire screen goes blank and redraws
- The program’s menu bar does not display
- The sounding window may not properly size at first. A fix is to manually resize it and manipulate it.

Other Issues:
- Multi-select does not work for Observed soundings
- Some forecast sounding (HRRR, NAM, etc.) point-click locations do not exist on the data server. This will cause the program to crash.
