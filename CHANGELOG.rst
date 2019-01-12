Change Log
==========

SHARPpy v1.4.0 "Andover" Release
--------------------------------

NEW FEATURES

* User preferences
    * Change units for wind, surface temperature and dewpoint
    * Choice of three color schemes: standard (the usual white-on-black), inverted (black-on-white), and protanopia (white-on-black, but with colorblind-friendly colors)
* Python 3 support
* Hodograph improvements
    * Can now click and drag the storm-motion vectors, updating all the other insets
    * Double click to change which storm motion vector is used for storm-relative calculations
    * New readout on the hodograph, coupled to the readout on the Skew-T
* Improvements for southern-hemisphere users
    * Wind barbs are flipped
    * Left-mover vector is used by default
    * Storm motion vector is chosen if the SPC-formatted sounding file specifies the latitude and longitude of the input sounding (southern-hemisphere uses the left-mover, northern the right-mover).
    * Left-mover vector is used in all other storm-motion dependent functions (e.g., STP insets, SARS).
* New data sources for international and U.S. users
    * Realtime and historical U.S. and international soundings from 1946-now are accessible through the Picker. Soundings include the latitude and longitude.
    * IEM BUFKIT sounding archive (data back to 2010 from RUC, NAM, GFS, RAP)
* New documentation and API accessible through Github pages
    * Improved documentation online (no longer in README)
    * Documentation and sphinx-generated API is pushed to Github Pages with each tagged release.
* Readout cursor can be configured to output other variables (e.g., potential temperature, theta-E)
* Ability to modify surface by changing the surface temperature or dewpoint (mixed layer optional) 
* Up/down buttons on keyboard can now be used to flip through the ensemble members plotted in the SHARPpy GUI.
* Logging enabled when --debug flag is enabled.
* GUI now displays alert box when questionable data is requested to be plotted. Users now have the option to choose if they wish to still try to plot the data.
* Continuous Integration (TravisCI, Appveyor, Azure Pipelines) now enabled to test changes, GUI quality, pull requests, deploy docs, deploy binaries to Github, and deploy packages to package managers.
* New versioning system now consistent with PEP-440 (thanks to versioneer).
* Included more scripting examples in docs.
* Deployment to conda and pip with each tagged SHARPpy release.
* Added test scripts to unit test various GUI parts, decoders, and numerical routines
* GUI checks Github Releases to see if the code being run is the current version 

BUG FIXES

* Fixed issue with resizing GUI where text would not resize or plots would become decoupled
* GUI now will handle profile objects where all of the wind speed or direction data is missing.
* Fixed an issue where rounding did not happen on the Fire inset
* Fixed bug when convective temperature routine would error if SBCAPE was 0
* Adjusted SWEAT calculation due to issue #153
* Fixed SHERB calculation due to issue #151.
* MBURST was fixed to use VT instead of TT. 
* Fixed bug where masked values were getting passed to np.arange
* prof_collection was modified to handle missing ensemble members
* Fixed the incorrect matching criteria for SARS using the MLLCL
* Updated the code to stop SHARPpy from showing nans on GUI
* Fixed unhandled case where Haines index coloring was not activated
* Stopped precip_water() from extrapolating the water vapor profile if missing data is present.
* Mapping and BUFKIT decoder bugs
* Fix for MMP if there are no data points betwee 6 and 10 km.
* Corrected location of sounding data points
* Stopped crashing of program when lapse-rate was calculated using low altitude data
* Tropical projection on mapping.py fixed
* Stopped Excessive Heat hazard type from firing at South Pole soundings
* Fixed bug where user selected soundings would cause an incorrect PWV climatology calculation.
* Hodograph drawing doesn't crash on incomplete profiles
* Fixed bug where missing kwarg wasn't passed on profile copy()
* Fixed fatal bug with boundary motion cursor


SHARPpy v1.3.0 "Xenia" Release
------------------------------

SHARPpy v1.3.0, Xenia Release supports multiple profiles in the Skew-T window and features improvements to the picker map and usability of the Skew-T window.

NEW FEATURES

* Ability to add and remove any data from the sounding picker in the sounding viewer and view it simultaneously.
* Can switch focus between profiles using the spacebar.
* Ability to focus and remove profiles from the Skew-T via the menus.
* Analogue profiles can be focused and removed by the same mechanisms.
* More picker map improvements
* Tropics and Southern Hemisphere maps are now available.
* Ability to recenter the map projection by double-clicking.
* Ability to save map view as the default for when the program loads.
* Installable binaries are available for Mac OS X and Windows
* Interpolation: interpolate profiles to 25-mb intervals for easy graphical modification.
* Skew-T zooming improved.
* Program now loads profiles in the background, decreasing the load time for the Skew-T window.
* Ability to save sounding text to a file.
* New MBURST index added to the sounding window.

BUG FIXES

* Menus now work on Windows and Linux.
* Model profiles compute the correct inferred temperature advection for their latitude.
* Additional error handling for partial profiles.
* Various model forecast points relocated to their proper places.
* Error handling for opening the program without an Internet connection.
* Removed PySide dependency and unused imports for those using SHARPpy routines in scripts.

SHARPpy v1.2.0 "El Reno" Release
--------------------------------

SHARPpy v1.2.0, El Reno Release, supports and features a new and improved user interface for selecting and interacting with sounding data sources, in addition to new SARS inset interactivity, and numerous backend changes/improvements. Please note that with these changes, the runsharp and datasources folders must not be moved, and must be run in the parent SHARPpy directory.

UPDATES/FIXES

* New pan/zoom map for selecting sounding locations from observed/model data sources
* Northern hemispheric map for global data sources (tropics and southern hemisphere maps coming soon)
* County map zooming for CONUS data sources
* Cursor readout for sounding locations includes station ID, city, and state/province or country
* Map checks the server for currently available points and only displays those that are available
* Bug fixes on selecting model initialization cycles and supports non-synoptic hour observed data
* Stations with special characters now work properly
* Mapping shapefiles have been added to the databases directory
* New XML backend for managing different data sources available to the GUI
* Allows custom configuration for data urls, initialization offset, model dt, forecast range, and point click locations for configured data sources. No tutorial has been generated for this yet.
* New SARS analogue interactivity
* SARS hail and supercell analogues can now be displayed alongside soundings by left-clicking on the analogue in the SARS inset window. It can be removed by right-clicking the skew-t window and hitting reset
* Improved the UI's look and feel on the Windows platform
* Added 0-3 km MLCAPE to the thermodynamics panel
* Fixed the 0-6 km shear and 9-11 km storm-relative wind vectors that are plotted when plotting a boundary motion in the Hodograph window.
* Data decoders have been modified, consolidated, and made more customization-friendly
* Moved the existing Profile object to a BasicProfile object, and made Profile an object that makes no computations upon construction and only stores data
* The "About" menu option (currently only works on OS X) has been updated with a new description and contact info
* Removed accidental SciPy dependency
* An Issue with the PWV climatology crashing on non-US stations has been fixed
* Save image and open user sounding text file functions now default to the user's home directory.
* Microburst Composite (MBURST), Derecho Composite Parameter (DCP), Energy-Helicity Index (EHI), and Severe Weather Threat Index (SWEAT) added to params.py
* Overall stability of the program has been increased.
* Tutorial has been updated to reflect some of the internal changes of the program libraries.
* Custom user sounding text files can now be opened by pressing Ctrl+O on Windows and Linux.

SHARPpy v1.0.0 Beta (AMS 2015 Release)
--------------------------------------

Following the SHARPpy presentation in the Python Symposium at the annual American Meteorological Society meeting, SHARPpy is being released to the public in beta status. Most core functionality is present, but it is being released with a few platform specific known bugs that are still being worked on.

This release features core numerical functionality (thermodynamic and kinematic routines) for scripting and data processing, in addition to graphical user interface functionality and interactivity.

Instructions on how to install and run can be found in the readme.


