#SHARPpy

######Sounding/Hodograph Analysis and Research Program in Python

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

**REMINDER: You must re-run the "python setup.py install" script for updates to take hold**

**NOTICE: If you have any custom data sources, you must add an "observed" flag to each data source your XML file, or SHARPpy will fail to load (see the [Adding Custom Data Sources](#adding-custom-data-sources) section).**

**Table of Contents**

- [Developer Requests](#developer-requests)
- [Installing SHARPpy](#installing-sharppy)
    - [Installing a Pre-compiled Binary](#installing-a-pre-compiled-binary)
    - [Installing the Code](#installing-the-code)
- [Using the SHARPpy Application](#using-the-sharppy-application)
    - [Using the SHARPpy Sounding Picker](#using-the-sharppy-sounding-picker)
        - [Loading in Multiple Soundings](#loading-in-multiple-soundings)
        - [Loading in Archived Data Files](#loading-in-archived-data-files)
        - [Adding Custom Data Sources](#adding-custom-data-sources)
    - [Using the Sounding Window](#using-the-sounding-window)
        - [Zooming and Changing Views](#zooming-and-changing-views)
        - [Swapping Insets](#swapping-insets)
        - [Color Ranking](#color-ranking)
        - [Interacting with the Focused Sounding](#interacting-with-the-focused-sounding)
            - [Modifying the Sounding](#modifying-the-sounding)
            - [Storm Mode Functions](#storm-mode-functions)
            - [Lifting Parcels](#lifting-parcels)
            - [Saving the Data](#saving-the-data)
        - [Interacting with Multiple Soundings](#interacting-with-multiple-soundings)
    - [Known GUI Issues](#known-gui-issues)
- [Scripting with SHARPpy Libraries](#scripting-with-sharppy)
- [SHARPpy Development Team](#sharppy-development-team)

=======================================================================
#####Developer Requests:
<sup>[[Return to Top]](#sharppy)</sup>

1.) Many people have put an immeasurable amount of time into developing this software package. 
If SHARPpy is used to develop a weather product or contributes to research that leads to a 
scientific publication, please acknowledge the SHARPpy project by citing the code. You can use 
this ready-made citation entry or provide a link back to this website:
    
[Blumberg, W. G., K. T. Halbert, T. A. Supinie, P. T. Marsh, R. L. Thompson, and J. A. Hart, 2017: SHARPpy: An Open Source Sounding Analysis Toolkit for the Atmospheric Sciences. Bull. Amer. Meteor. Soc. doi:10.1175/BAMS-D-15-00309.1, in press.](http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-15-00309.1)

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

SHARPpy can be installed in one of two forms: either a pre-compiled binary executable or by downloading the code.  Binary executables are available for Windows 7 (32 and 64 bit), Windows 8.1 (64 bit only), and Mac OS X 10.6+ (Snow Leopard and later; 64 bit only).  If you do not have one of those, then you will need to download the code.

#### Installing a Pre-compiled Binary
<sup>[[Return to Top]](#sharppy)</sup>

The following pre-compiled binaries are available (click to download):

[OS X (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-osx-64.zip)

[Windows 7 (32 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-32.zip)

[Windows 7 (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-64.zip)

[Windows 8.1 and Windows 10 (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win8.1-64.zip)

Installing a pre-compiled binary *should* be as simple as downloading the .zip file and extracting it to the location of your choice.  The zip files are named for the operating system and number of bits.  Most recently-built computers (probably post-2010 or so) should have 64-bit operating systems installed.  If your computer is older and you're unsure whether it has a 32- or 64-bit operating system, you can check on Windows 7 by clicking Start, right-clicking on Computer, and selecting Properties.  All recent versions of OS X (10.6 and newer) should be 64-bit.

#### Installing the Code
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy code can be installed on _Windows_, _Mac OS X_, and _Linux_, as all these platforms can run Python programs.  SHARPpy may run on other operating systems, but this has not been tested by the developers.  Chances are if it can run Python, it can run SHARPpy.  Running the SHARPpy code requires a.) the Python interpreter and b.) additional Python libraries.  Although there are multiple ways to meet these requirements, we recommend you install the _Python 2.7_ Anaconda Python Distribution from Continuum Analytics.  SHARPpy is primarily tested using this distribution.  

The Anaconda Python Distribution can be downloaded here: https://store.continuum.io/cshop/anaconda/

Additional ways to meet these requirements may include the Enthought Python Distribution, MacPorts, or Brew, but as of this moment we cannot provide support for these methods.

__Required Python Packages/Libraries:__

- NumPy

- PySide

Since SHARPpy requires the PySide and Numpy packages, you will need to install them.  If you choose to use the Anaconda distribution, Numpy comes installed by default.  PySide can be installed through the Anaconda package manager that comes with the Anaconda distribution by opening up your command line program (Terminal in Mac OS X/Linux and Command Prompt in Windows) and typing:

    conda install -c conda-forge pyside=1.2.4


After installing all the required Python packages for SHARPpy, you now can install the SHARPpy package to your computer.  You'll need to download it to your computer first and open up a command line prompt.  You can download it as a ZIP file (link on the right) or clone the Git respository (you will need the git program) into a directory on your computer by typing this into your command line:

    git clone https://github.com/sharppy/SHARPpy.git
    
If you follow the route of cloning SHARPpy, you can update to the most recent SHARPpy package by typing the following within the folder you downloaded SHARPpy to:

    git pull origin master
    
Once the package has been downloaded to your computer, use your command line to navigate into the SHARPpy directory and type this command in to install SHARPpy:

    python setup.py install

After installing the package, you can run the SHARPpy GUI and interact with the SHARPpy libraries through Python scripts.

A video tutorial for installing on Windows: https://dl.dropboxusercontent.com/u/6375163/SHARPpy.mp4

From this point on, you will be able to access both the SHARPpy application and the libraries behind it.  If you are more interested in using the SHARPpy libraries for scripting, see the [Scripting with SHARPpy Libraries](#scripting-with-sharppy) section.  If you would like to use the SHARPpy application for viewing real-time data and interacting with soundings, continue to the [Using the SHARPpy GUI](#using-the-sharppy-gui) section.

=======================================================================
## Using the SHARPpy Application
<sup>[[Return to Top]](#sharppy)</sup>

To run the pre-compiled binary program, double click on the icon.  It may take 20-30 seconds for the window to open so please be patient.

To run SHARPpy from the code, navigate to the `runsharp/` folder contained within the SHARPpy directory you downloaded.  Once there, run the following command:

    python full_gui.py

Either of these will load the SHARPpy Sounding Picker GUI.

=======================================================================

### Using the SHARPpy Sounding Picker
<sup>[[Return to Top]](#sharppy)</sup>

Upon running SHARPpy, the "SHARPpy Sounding Picker" window should pop up displaying a list of available default and custom data sources.  This window also shows where the soundings are located for each source.  To open a sounding, select a sounding source (observed, GFS, HRRR, etc.), a cycle time, and then select profile time(s) to view in the GUI.  Next, click on your desired location on the point and click map.  Once all of these are selected, click "Generate Profiles" to view the sounding data.  After the program downloads the data, it will appear in a sounding window for use.

The map views can be altered using your mouse.  Scrolling with your mouse wheel or trackpad will zoom in and out of the map.  Clicking and dragging will change the view of the map.  Double clicking will re-center the map on your cursor (i.e. for changing from US to Europe views.)  Clicking the "Save Map View as Default" button will save this map view so each time you load the Sounding Picker, it will be centered where you want it.

If the program is unable to detect an Internet connection, it will display a message on the map for the user.  However, you can still pull up sounding data if it resides on your local hard disk.  If you are able to reconnect to the Internet, you'll need to restart the SHARPpy program in order to remove this message and access the data online.

#### Loading in Multiple Soundings

As of the 1.3.0 release, SHARPpy now supports adding additional profiles to the sounding window.  This allows the user to have a large amount of flexiblity in making comparisons between different sounding data.  For example, SHARPpy can now be used to perform visual comparsions between GFS and NAM forecast soundings, D(prog)/Dt of the HRRR forecast soundings, or compare observed soundings to model data.  Once a sounding window is open, you can change focus back to the SHARPpy Sounding Picker and add additional sounding data to your open sounding window by repeating the process to generate the first sounding window.  At this point the sounding window will have one profile that is in "focus" and other(s) that are not.

#### Loading in Archived Data Files

SHARPpy supports opening up multiple observed sounding data files in the sounding window.  While in the SHARPpy Sounding Picker, use File->Open menu to open up your text file in the sounding window.  See the OAX file in the tutorials folder for an example of the tabular format SHARPpy requires to use this function.

#### Adding Custom Data Sources
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
### Using the Sounding Window
<sup>[[Return to Top]](#sharppy)</sup>

##### Zooming and Changing Views

Your mouse wheel or trackpad will allow you to zoom on both the Hodograph and Skew-T plots within the window.  Right clicking on the Hodograph will also allow you to change where the hodograph is centered.  Currently, the hodograph can be centered on the Right Mover Storm Motion Vector, the Cloud-Layer Mean Wind Vector, or the origin of the hodograph.

##### Swapping Insets

The right 2 insets of the SHARPpy program can be changed by right clicking on either one.  Right clicking will bring up a menu that shows the different insets available for the user.  These insets exist to help the user further interrogate the data.  Below is a list of the current available insets:

1. SARS - Sounding Analog Retrieval System provides matching of the current sounding to past severe weather events.  Clicking on any of the close matches will load the sounding from that event into the sounding window for closer comparison and inspection.
2. STP STATS - Information on the significant tornado parameter with CIN (STPC) associated with the sounding.
3. SHIP - Distribution of expected hail sizes associated with the significant hail parameter (SHIP).
4. STP COND - Conditional probablities for different tornado strengths based on STPC.
5. WINTER - Information on precipitation type, melting and freezing in the profile, and the dendritic growth zone.
6. FIRE - Fire weather information such as wind speed and humidity in the boundary layer.
7. VROT - Conditional probabilities for different tornado strengths based on the 0.5 degree rotational velocity. (Double click inside the inset to input a VROT value.)

##### Color Ranking

The GUI uses color to highlight the features a forecaster ought to look at.  Most indices have a color ranking and thresholds using these colors (1, very high values to 6, very low values):

1. MAGENTA
2. RED
3. YELLOW
4. WHITE
5. LIGHT BROWN
6. DARK BROWN

The precipitable water (PW) value in the sounding window follows a different color scale, as it is based upon the precipitable water vapor climatology for each month (donated by Matthew Bunkers; NWS).  Green colors means that the PW value is moister than average, while brown values mean the PW value is drier than average.  The intensity of the color corresponds to how far outside the PW distribution the value is (by standard deviation). NOTE: This function only works for current US radiosonde stations.

#### Interacting with the Focused Sounding

The current sounding that is in "focus" in the program has the traditional "red/green" temperature and dewpoint profiles, while all other soundings in the background will be colored purple.  Below are some functions of the sounding window that are specific to the sounding that is in focus.

##### Modifying the Sounding

The sounding that is in focus can be modified by clicking and dragging the points of the temperature/dewpoint/hodograph lines.  Recalculations of all indices will take place when this is done.  To reset the Skew-T or hodograph back to the original data, right click on either the Skew-T or the hodograph and look for the option to reset the data.

New in version 1.3.0 is the ability to interpolate the profile to 25-mb intervals.  This can be done by either pressing the 'I' key on the keyboard or by selecting Profiles->Interpolate on the menu bar. Interpolating the profile will take into account any modifications you've done to the original profile.  Pressing the 'I' key again or selecting Profiles->Reset Interpolation will reset the profile, undoing all modifications, so be sure you want to reset the profile before doing so.

##### Storm Mode Functions

Right clicking on the hodograph will open up a menu that includes some functions that allow further inspection of the type of storm mode that can be expected from the focused sounding.  In particular, the Storm Motion Cursor and the Boundary Cursor can be used.  Using the Storm Motion Cursor will allow you to deteremine the 0-1 km, 0-3 km, and effective storm-relative helicity for differen storm motions than the supercell right mover motion plotted on the hodograph.  The Boundary Cursor, allows you to plot a boundary on the hodograph in order to determine how long convective updrafts may stay within a zone of ascent.  Clicking on the hodograph with the Boundary Cursor will plot a boundary in orange on the hodograph and will also plot the 0-6 km shear (blue) and the 9-11 km storm relative wind (pink) vectors on the hodograph.  This allows you to visualize if the environment is favorable for storms growing upscale.  Clicking on the hodograph again will remove the boundary.

##### Lifting Parcels

By default, soundings opened up in the GUI show these 4 parcels in the lower left inset window:

1.) Surface-based Parcel

2.) 100 mb Mixed-layer Parcel

3.) Forecasted Surface Parcel

4.) Most-Unstable Parcel

Double clicking on this inset will allow you to swap out these parcels for two others:

1.) Effective Inflow Layer Mean Parcel

2.) User Defined Parcel

The current parcel shown in the Skew-T is highlighed by a brown box within the Thermo inset.  Clicking on any of the 4 parcels in the inset will change the a) the parcel trace drawn on the Skew-T and b) change the parcel used in the parcel trajectory calculation (aka Storm Slinky.)  To lift custom parcels, double click on the Thermo (lower left) inset and select the "User Parcel".  Then, right click on the Skew-T and select the "Readout Cursor".  Once you find the location in your profile you wish to lift, right click again and look under the "Lift Parcel" menu to select a parcel lifting routine.  If you are lifting a layer averaged parcel, the location of the cursor selects the level (or bottom of the layer) you are lifting.

##### Saving the Data

When the sounding window is up, you can select to either save the sounding as an image or save the current focused sounding as a text file that can be loaded back into SHARPpy.  These functions are found underneath the File->Save Text or File->Save Image functions.

#### Interacting with Multiple Soundings

After adding other soundings into the sounding window, the user can change which sounding is the "focus" by accessing the list of available profiles.  This list is kept underneath the "Profiles" menu on the menu bar.   SHARPpy keeps track of the time aspect of all data loaded into the sounding window and attempts to show all profiles valid at a given time.  For the given sounding source that is in focus, the right and left buttons on your keyboard will step through the data in time and will attempt to show any other data sources available.  When observed or user selected data is loaded into the sounding window, SHARPpy will not overlay soundings from different times unless the "Collect Observed" function is checked.  This can be accessed through underneath the "Profiles" menu item or by pressing "C" on your keyboard.

The space bar on your keyboard is used to swap the focus between the profiles shown in the sounding window.  Additionally, to swap between the SHARPpy Sounding Picker and sounding window, hit "W" on your keyboard.  With this change, the right and left arrow keys now will step through the profiles available from the sounding data source that is active.  SHARPpy will match up other.  

=======================================================================

### Known GUI Issues
<sup>[[Return to Top]](#sharppy)</sup>

Known Issues:
- Some of our sounding data sources (HRRR, GFS, etc.) can sometimes go down.  This is outside of our control. (All OSes)
- Moving through time with model profiles may be slow in the Windows binaries because of a backend bug. Running from the code should be fine.
- Text can sometimes overlap. (Windows and Linux)
- The program’s menu bar does not display on Windows (Fixed as of 1.3.0 release)
- Some observed soundings will be unable to be loaded into the program due to data quality issues.  This is a preventative measure taken by the program that checks the sounding data for a.) incorrect ordering of the data such as in the height or pressure arrays or b.) unrealistic data values. (All OSes)

=======================================================================
### Scripting with SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

To learn more about interacting with the SHARPpy libraries using the Python
programming language, see the tutorial listed in tutorials/ and check out the link:

http://nbviewer.ipython.org/github/sharppy/SHARPpy/blob/master/tutorials/SHARPpy_basics.ipynb

To write scripts interacting with the SHARPpy libraries, you do NOT have to have the PySide package installed.

=======================================================================

### SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (OU School of Meteorology)
- Greg Blumberg (OU/CIMMS)
- Tim Supinie (OU School of Meteorology)

Questions and concerns not related to bug reports or feature requests should be may be directed to the team through this email: sharppy.project@gmail.com

