#SHARPpy

######Sounding/Hodograph Analysis and Research Program in Python

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

**REMINDER: You must re-run the "python setup.py install" script for updates to take hold**

**NOTICE: If you have any custom data sources, you must add an "observed" flag to each data source your XML file, or SHARPpy will fail to load (see the [Adding Custom Data Sources](#adding-custom-data-sources) section).**

**Table of Contents**

- [Developer Requests](#developer-requests)
- [Installing SHARPpy](#installing-sharppy)
- [Running the SHARPpy GUI](#running-the-sharppy-gui)
- [Using the GUI](#using-the-gui)
    - [Available Insets](#available-insets)
    - [Lifting Parcels](#lifting-parcels)
- [Known GUI Issues](#known-gui-issues)
- [Adding Custom Data Sources](#adding-custom-data-sources)
- [Scripting with SHARPpy](#scripting-with-sharppy)
- [SHARPpy Development Team](#sharppy-development-team)

=======================================================================
#####Developer Requests:
<sup>[[Return to Top]](#sharppy)</sup>

1.) Many people have put an immeasurable amount of time into developing this software package. 
If SHARPpy is used to develop a weather product or contributes to research that leads to a 
scientific publication, please acknowledge the SHARPpy project by citing the code. You can use 
this ready-made citation entry or provide a link back to this website:


    Halbert, K. T., W. G. Blumberg, and P. T. Marsh, 2015: "SHARPpy: Fueling the Python Cult". 
    Preprints, 5th Symposium on Advances in Modeling and Analysis Using Python, Phoenix AZ.


http://sharppy.github.io/SHARPpy/index.html

https://github.com/sharppy/SHARPpy

Additionally, Jeff Whitaker created the Basemap package, from which we have borrowed data and code to develop the SHARPpy data selector GUI.

2.) Also, please send an email letting us know where SHARPpy is being used or 
has helped your work at this address so we may track the success of the project: sharppy.project@gmail.com.

3.) All bug reports and feature requests should be submitted through the Github issues page in order to assist the developers in tracking the issues noted by the users.  Before you open a new issue, please check to see if your issue (or a similar one) has already been opened.  If your issue already exists, please add a comment to the issue comment thread explaining your bug report or feature request with as much detail as possible.  More detail will help the developers fix the issue (in the case of a bug report).  The issues page for the SHARPpy project can be found here:

https://github.com/sharppy/SHARPpy/issues

Please also consider posting to the sharppy group on Google Groups.  Other users may have encountered your problem already, and may be able to help you!

https://groups.google.com/forum/#!forum/sharppy

=======================================================================
### Installing SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy can be installed on _Windows_, _Mac OS X_, and _Linux_, as all these platforms can run Python programs.  SHARPpy may run on other operating systems, but this has not been tested by the developers.  Chances are if it can run Python, it can run SHARPpy.  Running SHARPpy requires a.) the Python interpreter and b.) additional Python libraries.  Although there are multiple ways to meet these requirements, we recommend you install the _Python 2.7_ Anaconda Python Distribution from Continuum Analytics.  SHARPpy is primarily tested using this distribution.  

The Anaconda Python Distribution can be downloaded here: https://store.continuum.io/cshop/anaconda/

Additional ways to meet these requirements may include the Enthought Python Distribution, MacPorts, or Brew, but as of this moment we cannot provide support for these methods.

__Required Python Packages/Libraries:__

- NumPy

- PySide

Since SHARPpy requires the PySide and Numpy packages, you will need to install them.  If you choose to use the Anaconda distribution, Numpy comes installed by default.  PySide can be installed through the Anaconda package manager that comes with the Anaconda distribution by opening up your command line program (Terminal in Mac OS X/Linux and Command Prompt in Windows) and typing:

    conda install PySide

After installing all the required Python packages for SHARPpy, you now can install the SHARPpy package to your computer.  You'll need to download it to your computer first and open up a command line prompt.  You can download it as a ZIP file (link on the right) or clone the Git respository (you will need the git program) into a directory on your computer by typing this into your command line:

    git clone https://github.com/sharppy/SHARPpy.git
    
If you follow the route of cloning SHARPpy, you can update to the most recent SHARPpy package by typing the following within the folder you downloaded SHARPpy to:

    git pull origin master
    
Once the package has been downloaded to your computer, use your command line to navigate into the SHARPpy directory and type this command in to install SHARPpy:

    python setup.py install

After installing the package, you can run the SHARPpy GUI and interact with the SHARPpy libraries through Python scripts.

A video tutorial for installing on Windows: https://dl.dropboxusercontent.com/u/6375163/SHARPpy.mp4

=======================================================================
### Running the SHARPpy GUI
<sup>[[Return to Top]](#sharppy)</sup>

To run the SHARPpy GUI and interact with real-time observed and forecast soundings, navigate to the `runsharp/` folder contained within the SHARPpy directory you downloaded.  Once there, run the following command:

    python full_gui.py

As of May 8th, 2015, we recommend you __do not__ move the `runsharp/` folder or `full_gui.py` from its original downloaded location. This will break your SHARPpy program. This "feature" will be fixed in a future release.

=======================================================================

### Using the GUI
<sup>[[Return to Top]](#sharppy)</sup>

To open a sounding, select a sounding source (observed, GFS, HRRR, etc.), a cycle time, and then select profile time(s) to view in the GUI.  Next, click on your desired location on the point and click map.  Once all of these are selected, click "Generate Profiles".

After all profiles have been generated, a window should show up with your desired data.  Below are things you can do:

1. Advance through the profiles (if more than one is selected) using the left and right arrow keys.
2. Change the hodograph cursor or point the hodograph window is centered on by right clicking on the hodograph.
3. Modify the right 2 insets by right clicking on either one.  Different insets are available to help the user interrogate the data.
4. Zoom in/out the Skew-T or hodograph by using the scroll wheel function on your mouse or trackpad.
5. Graphically modify the Skew-T and hodograph by clicking and dragging the points of the temperature/dewpoint/hodograph lines.  Recalculations of all indices will take place when this is done.  (Added 2/19/2015 by Tim Supinie.)
6. View different parcels that can be lifted and lift custom parcels.  
7. Compare the profiles and hodograph from severe weather sounding analogs retrieved by SARS by clicking on any of the analogs displayed.
8. Save an image of the sounding you are viewing (Control+S; Windows/Linux, Command+S; OS X)
9. Open up a text file that contains observed sounding data you wish to view.  While in the sounding picker, use the keys Control+O for Windows/Linux, Command+O for OS X.  Text files must be in a tabular format similar to what is seen on the SPC soundings page.  See the OAX file in the tutorials folder for an example.  

#### Available Insets
<sup>[[Return to Top]](#sharppy)</sup>

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

#### Lifting Parcels
<sup>[[Return to Top]](#sharppy)</sup>

By default, soundings opened up in the GUI show these 4 parcels in the lower left inset window:

1.) Surface-based Parcel

2.) 100 mb Mixed-layer Parcel

3.) Forecasted Surface Parcel

4.) Most-Unstable Parcel

Double clicking on this inset will allow you to swap out these parcels for two others:

1.) Effective Inflow Layer Mean Parcel

2.) User Defined Parcel

The user defined parcel can be set by right clicking on the Skew-T and selecting a custom
parcel to lift.  The location of the cursor (or readout cursor) selects the level (or bottom of the layer)
you are lifting.

Clicking on any of the 4 parcels in the inset will change the a) the parcel trace drawn on the Skew-T and b) change the parcel used in the parcel trajectory calculation (aka Storm Slinky.)

=======================================================================

### Known GUI Issues
<sup>[[Return to Top]](#sharppy)</sup>

Known Issues:
- Text can sometimes overlap. (Windows)
- The program’s menu bar does not display (minimal issue since there are very few menu bar functions) (Windows)
- SHARPpy will not work with QT 4.8.6.0 on Linux.  There is a bug in the QT package affects the ability of the GUI to render.  UPDATE: This bug has been fixed by a new release from QT (Noted 4/24/2015).
- Some observed soundings will be unable to be loaded into the program due to data quality issues.  This is a preventative measure taken by the program that checks the sounding data for a.) incorrect ordering of the data such as in the height or pressure arrays or b.) unrealistic data values. (All OSes)

=======================================================================
### Adding Custom Data Sources
<sup>[[Return to Top]](#sharppy)</sup>

To add a custom data source, add to the `datasources/` directory an XML file containing the data source information and a CSV file containing all the location information.  We do not recommend modifying the `standard.xml` file, as it may break SHARPpy, and your custom data source information may get overwritten when you update SHARPpy.

##### 1. Make a new XML file
The XML file contains the information for how the data source behaves. Questions like "Is this data source an ensemble?" or "How far out does this data source forecast?" are answered in this file. It should be a completely new file.  It can be named whatever you like, as long as the extension is `.xml`. The format should look like the `standard.xml` file in the `datasources/` directory, but an example follows:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<sourcelist>
    <datasource name="My Data Source" observed="false" ensemble="false">
        <outlet name="My Server" url="http://www.example.com/myprofile_{date}{cycle}_{srcid}.buf" format="bufkit" >
            <time range="24" delta="1" cycle="6" offset="0" delay="2" archive="24"/>
            <points csv="mydatasource.csv" />
        </outlet>
    </datasource>
</sourcelist>
```

For the `outlet` tag:
* `name`: A name for the data source outlet
* `url`: The URL for the profiles. The names in curly braces are special variables that SHARPpy fills in the following manner:
  * `date`: The current date in YYMMDD format (e.g. 150602 for 2 June 2015).
  * `cycle`: The current cycle hour in HHZ format (e.g. 00Z).
  * `srcid`: The source's profile ID (will be filled in with the same column from the CSV file; see below).
* `format`: The format of the data source.  Currently, the only supported formats are `bufkit` for model profiles and `spc` for observed profiles. Others will be available in the future.

For the `time` tag:
* `range`: The forecast range in hours for the data source. Observed data sources should set this to 0.
* `delta`: The time step in hours between profiles. Observed data sources should set this to 0.
* `cycle`: The amount of time in hours between cycles for the data source.
* `offset`: The time offset in hours of the cycles from 00 UTC.
* `delay`: The time delay in hours between the cycle and the data becoming available.
* `archive`: The length of time in hours that data are kept on the server.

These should all be integer numbers of hours; support for sub-hourly data is forthcoming.

##### 2. Make a new CSV file
The CSV file contains information about where your profiles are located and what the locations are called. It should look like the following:
```
icao,iata,synop,name,state,country,lat,lon,elev,priority,srcid
KTOP,TOP,72456,Topeka/Billard Muni,KS,US,39.08,-95.62,268,3,ktop
KFOE,FOE,,Topeka/Forbes,KS,US,38.96,-95.67,320,6,kfoe
...
```
The only columns that are strictly required are the `lat`, `lon`, and `srcid` columns.  The rest must be present, but can be left empty. However, SHARPpy will use as much information as it can get to make a pretty name for the station on the picker map.

##### 3. Run `python setup.py install`
This will install your new data source and allow SHARPpy to find it. If the installation was successful, you should see it in the "Data Sources" drop-down menu.

=======================================================================
### Scripting with SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

To learn more about interacting with the SHARPpy libraries using the Python
programming language, see the tutorial listed in tutorials/ and check out the link:

http://nbviewer.ipython.org/github/sharppy/SHARPpy/blob/master/tutorials/SHARPpy_basics.ipynb

=======================================================================

### SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (OU School of Meteorology)
- Greg Blumberg (OU/CIMMS)
- Tim Supinie (OU School of Meteorology)

Questions and concerns not related to bug reports or feature requests should be may be directed to the team through this email: sharppy.project@gmail.com

