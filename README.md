# SHARPpy

###### Sounding/Hodograph Analysis and Research Program in Python

[![Build status](https://travis-ci.org/sharppy/SHARPpy.svg?branch=andover)](https://travis-ci.org/sharppy)
[![Build status](https://ci.appveyor.com/api/projects/status/f7ahm2l5cdyibswc/branch/andover?svg=true)](https://ci.appveyor.com/project/sharppy/sharppy/branch/andover)

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

**REMINDER: You must re-run the "python setup.py install" script for updates to take hold**

**NOTICE: If you have any custom data sources, you must add an "observed" flag to each data source your XML file, or SHARPpy will fail to load (see the [Adding Custom Data Sources](#adding-custom-data-sources) section).**

##Important links:
* HTML Documentation: http://sharppy.github.io/SHARPpy/index.html
* Source code reponsitory: https://github.com/sharppy/SHARPpy
* Issue tracker: https://github.com/sharppy/SHARPpy/issues

**Table of Contents**

- [Developer Requests](#developer-requests)
- [Installing SHARPpy](#installing-sharppy)
    - [Installing a pre-compiled binary](#installing-a-pre-compiled-binary)
    - [Installing from source](#installing-the-code)
- [Running the SHARPpy Application](#using_the_sharppy_application)
- [Known GUI Issues](#known-gui-issues)
- [SHARPpy Development Team](#sharppy-development-team)

=======================================================================
##### Developer Requests:
<sup>[[Return to Top]](#sharppy)</sup>

1.) Many people have put an immeasurable amount of time into developing this software package. 
If SHARPpy is used to develop a weather product or contributes to research that leads to a 
scientific publication, please acknowledge the SHARPpy project by citing the code. You can use 
this ready-made citation entry or provide a link back to this website:
    
 [Blumberg, W. G., K. T. Halbert, T. A. Supinie, P. T. Marsh, R. L. Thompson, and J. A. Hart, 2017: "SHARPpy: An Open Source Sounding Analysis Toolkit for the Atmospheric Sciences." Bull. Amer. Meteor. Soc. doi:10.1175/BAMS-D-15-00309.1, in press.](http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-15-00309.1)

We wish to acknowledge Jeff Whitaker, who created the Basemap package, and from which we have borrowed data and code to develop the SHARPpy data selector GUI.

2.) Also, please send an email letting us know where SHARPpy is being used or 
has helped your work at this address so we may track the success of the project: sharppy.project@gmail.com.

3.) All bug reports and feature requests should be submitted through the Github issues page in order to assist the developers in tracking the issues noted by the users.  Before you open a new issue, please check to see if your issue (or a similar one) has already been opened.  If your issue already exists, please add a comment to the issue comment thread explaining your bug report or feature request with as much detail as possible.  More detail will help the developers fix the issue (in the case of a bug report).  The issues page for the SHARPpy project can be found here:

https://github.com/sharppy/SHARPpy/issues

Please also consider posting to the sharppy group on Google Groups.  Other users may have encountered your problem already, and may be able to help you!

https://groups.google.com/forum/#!forum/sharppy

=======================================================================
### Installing SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy can be installed in one of two forms: either a pre-compiled binary executable or by downloading the code and installing it using a separate Python interpreter.  Binary executables are available for Windows 7 (32 and 64 bit), Windows 8.1 (64 bit only), and Mac OS X 10.6+ (Snow Leopard and later; 64 bit only).  If you do not have one of those, then you will need to download the code.

#### Installing a Pre-compiled Binary
<sup>[[Return to Top]](#sharppy)</sup>

The following pre-compiled binaries are available (click to download):

[OS X (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-osx-64.zip)

[Windows 7 (32 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-32.zip)

[Windows 7/8.1/10 (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-64.zip)

Installing a pre-compiled binary *should* be as simple as downloading the .zip file and extracting it to the location of your choice.  The zip files are named for the operating system and number of bits.  Most recently-built computers (probably post-2010 or so) should have 64-bit operating systems installed.  If your computer is older and you're unsure whether it has a 32- or 64-bit operating system, you can check on Windows 7 by clicking Start, right-clicking on Computer, and selecting Properties.  All recent versions of OS X (10.6 and newer) should be 64-bit.

#### Installing the Code from Source
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy code can be installed on _Windows_, _Mac OS X_, and _Linux_, as all these platforms can run Python programs.  SHARPpy may run on other operating systems, but this has not been tested by the developers.  Chances are if it can run Python, it can run SHARPpy.  Running the SHARPpy code requires a.) the Python interpreter and b.) additional Python libraries.  Although there are multiple ways to meet these requirements, we recommend you install the _Python 2.7_ Anaconda Python Distribution from Continuum Analytics.  SHARPpy (1.3.0 Xenia) is primarily tested using this distribution.  If you wish to use _Python 3_  we recommend downloading the [Andover branch](https://github.com/sharppy/SHARPpy/tree/andover) that is in development.  

The Anaconda Python Distribution can be downloaded here: https://www.anaconda.com/download/

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

### Known GUI Issues
<sup>[[Return to Top]](#sharppy)</sup>

Known Issues:
- Some of our sounding data sources (HRRR, GFS, etc.) can sometimes go down.  This is outside of our control. (All OSes)
- Moving through time with model profiles may be slow in the Windows binaries because of a backend bug. Running from the code should be fine.
- Text can sometimes overlap. (Windows and Linux)
- The program’s menu bar does not display on Windows (Fixed as of 1.3.0 release)
- Some observed soundings will be unable to be loaded into the program due to data quality issues.  This is a preventative measure taken by the program that checks the sounding data for a.) incorrect ordering of the data such as in the height or pressure arrays or b.) unrealistic data values. (All OSes)

### SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (OU School of Meteorology)
- Greg Blumberg (OU/CIMMS)
- Tim Supinie (OU School of Meteorology)

Questions and concerns not related to bug reports or feature requests should be may be directed to the team through this email: sharppy.project@gmail.com

