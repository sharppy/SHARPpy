SHARPpy
=======
Sounding/Hodograph Analysis and Research Program in Python

Required Packages:

NumPy

PySide

This is primarily tested and used with the Anaconda Python Distribution
from Continuum Analytics. Anaconda can be downloaded here:
https://store.continuum.io/cshop/anaconda/

You will then need to install the PySide package through the anaconda package manager:

conda install PySide

To install the SHARPpy package into your Python path, type:

python setup.py install

To run the SHARPpy GUI, you will need both Numpy and PySide installed
with your Python distribution.  To run the gui, copy the runsharp folder
to the location at which you wish to run the program. Navigate to that
folder in your terminal and run the following command:

python full_gui.py

=======================================================================

Many people have put an immeasurable amount of time into developing this software package. 
If SHARPpy is used to develop a weather product or contributes to research that leads to a 
scientific publication, please acknowledge the SHARPpy project by citing the code. You can use 
this ready-made citation entry or provide a link back to this website:

Halbert, K. T., W. G. Blumberg, and P. T. Marsh, 2015: "SHARPpy: Fueling the Python Cult". Preprints, 5th Symposium on Advances in Modeling and Analysis Using Python, Phoenix AZ.

http://sharppy.github.io/SHARPpy/index.html

https://github.com/sharppy/SHARPpy

Also, please send an email letting us know where SHARPpy is being used or 
has helped your work at this address so we may track the success of the project:

sharppy.project@gmail.com.

=======================================================================

### Using the GUI

To open a sounding, select a sounding type, a model run time (if the type is an NWP model), and then select a time(s).
Afterwards, click on your desired location on the point and click map.  Once all of these are selected, click "Generate Profiles".

After all profiles have been generated, a window should show up with your desired data.  Below are things you can do:

1. Advance through the profiles (if more than one is selected) using the left and right arrow keys.
2. Change the hodograph cursor or point the hodograph window is centered on by right clicking on the hodograph.
3. Modify the right 2 insets by right clicking on either one.  Different insets are available to help the user interrogate the data.
4. Zoom in/out the Skew-T or hodograph by using the scroll wheel function on your mouse or trackpad.
5. Graphically modify the Skew-T and hodograph by clicking and dragging the points of the temperature/dewpoint/hodograph lines.  Recalculations of all indices will take place when this is done.  (Added 2/19/2015 by Tim Supinie.)

Insets available for use:

1. SARS - Sounding Analog Retrieval System provides matching of the current sounding to past severe weather events.
2. STP STATS - Information on the significant tornado parameter with CIN (STPC) associated with the sounding.
3. SHIP - Distribution of expected hail sizes associated with the significant hail parameter (SHIP).
4. STP COND - Conditional probablities for different tornado strengths based on STPC.
5. WINTER - Information on precipitation type, melting and freezing in the profile, and the dendritic growth zone.
6. FIRE - Fire weather information such as wind speed and humidity in the boundary layer.
7. VROT - Conditional probabilities for different tornado strengths based on the 0.5 degree rotational velocity. (Double click inside the inset to input a VROT value.)

The GUI uses color to highlight the features a forecaster ought to look at.  Most indices have a color ranking and thresholds using these colors (1, very high values to 6, very low values):

1. MAGENTA
2. RED
3. YELLOW
4. WHITE
5. LIGHT BROWN
6. DARK BROWN

=======================================================================

### Known Issues

Known Windows Issues:
- Inset text is not properly sized or placed in their windows.
- When incrementing/decrementing profiles, the entire screen goes blank and redraws (FIXED AS OF 2/11/2015)
- The program’s menu bar does not display
- The sounding window may not properly size at first. A fix is to manually resize it and manipulate it.

Other Issues:
- Multi-select does not work for Observed soundings
- Some forecast sounding (HRRR, NAM, etc.) point-click locations do not exist on the data server. This will cause the program to crash.
- Wind barbs for very fast winds sometimes have barbs misplaced with respect to the stick of the wind diagram.  (FIXED AS OF 2/20/2015)
