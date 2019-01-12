# SHARPpy

###### Sounding/Hodograph Analysis and Research Program in Python

[![Build status](https://travis-ci.org/sharppy/SHARPpy.svg?branch=andover)](https://travis-ci.org/sharppy)
[![Build status](https://ci.appveyor.com/api/projects/status/f7ahm2l5cdyibswc/branch/andover?svg=true)](https://ci.appveyor.com/project/sharppy/sharppy/branch/andover)
[![Build Status](https://dev.azure.com/sharppy/SHARPpy/_apis/build/status/sharppy.SHARPpy?branchName=andover)](https://dev.azure.com/sharppy/SHARPpy/_build/latest?definitionId=1?branchName=andover)
[![Anaconda-Server Badge](https://anaconda.org/sharppy/sharppy/badges/downloads.svg)](https://anaconda.org/sharppy/sharppy)
[![Anaconda-Server Badge](https://anaconda.org/sharppy/sharppy/badges/license.svg)](https://anaconda.org/sharppy/sharppy)
[![](https://img.shields.io/github/downloads/sharppy/SHARPpy/total.svg?style=popout)](https://github.com/sharppy/SHARPpy/releases)
[![Coverage Status](https://coveralls.io/repos/github/sharppy/SHARPpy/badge.svg?branch=andover)](https://coveralls.io/github/sharppy/SHARPpy?branch=andover)
[![Anaconda-Server Badge](https://anaconda.org/sharppy/sharppy/badges/platforms.svg)](https://anaconda.org/sharppy/sharppy)

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

### Important links:
* HTML Documentation: http://sharppy.github.io/SHARPpy/index.html
* GitHub repository: https://github.com/sharppy/SHARPpy
* Issue tracker: https://github.com/sharppy/SHARPpy/issues
* Google Groups: https://groups.google.com/forum/#!forum/sharppy

**Table of Contents**

- [Developer Requests](#developer-requests)
- [Installing SHARPpy](#installing-sharppy)
- [Running SHARPpy](#using_the_sharppy_application)
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

We wish to acknowledge Jeff Whitaker, who created the [Basemap](https://matplotlib.org/basemap/) package, and from which we have borrowed data and code to develop the SHARPpy data Picker.  We also wish to acknowledge [MetPy](https://github.com/Unidata/MetPy), who we have borrowed their Matplotlib skew-t code from to illustrate some SHARPpy examples. 

2.) All bug reports and feature requests should be submitted through the Github issues page in order to assist the developers in tracking the issues noted by the users.  Before you open a new issue, please check to see if your issue (or a similar one) has already been opened.  If your issue already exists, please add a comment to the issue comment thread explaining your bug report or feature request with as much detail as possible.  More detail will help the developers fix the issue (in the case of a bug report).  The issues page for the SHARPpy project can be found here:

https://github.com/sharppy/SHARPpy/issues

=======================================================================
### Installing SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy code can be installed on _Windows_, _Mac OS X_, and _Linux_, as all these platforms can run Python programs.  SHARPpy may run on other operating systems, but this has not been tested by the developers.  Chances are if it can run Python, it can run SHARPpy.  

If you would like to run SHARPpy from a binary (if you don't want to do scripting), look for the most recent release here: https://github.com/sharppy/SHARPpy/releases

For those wishing to run both the GUI and do scripting, we recommend you install the _Python 3_ Anaconda Python Distribution from Continuum Analytics. You can install SHARPpy from `conda` or `pip` by using either:

    conda install -c sharppy sharppy

 or
    
    pip install sharppy

The Anaconda Python Distribution can be downloaded here: https://www.anaconda.com/download/

__Required Python Packages/Libraries:__

* NumPy v1.15
* PySide v1.2.4
* requests
* python-dateutil

Since SHARPpy requires these packages, you will need to install them.  If you choose to use the Anaconda distribution, Numpy comes installed by default.  PySide, requests, and python-dateutil can be installed through the Anaconda package manager that comes with the Anaconda distribution by opening up your command line program (Terminal in Mac OS X/Linux and Command Prompt in Windows) and typing:

    conda install -c conda-forge pyside=1.2.4 requests python-dateutil

After installing all the required Python packages for SHARPpy, you now can install the SHARPpy package to your computer.  You'll need to download it to your computer first and open up a command line prompt.  You can download it as a ZIP file (link on the right) or clone the Git respository (you will need the git program) into a directory on your computer by typing this into your command line:

    git clone https://github.com/sharppy/SHARPpy.git
    
If you follow the route of cloning SHARPpy, you can update to the most recent SHARPpy package by typing the following within the folder you downloaded SHARPpy to:

    git pull origin master
    
Once the package has been downloaded to your computer, use your command line to navigate into the SHARPpy directory and type this command in to install SHARPpy:

    python setup.py install

After installing the package, you can run the SHARPpy GUI and interact with the SHARPpy libraries through Python scripts.

**REMINDER: You must re-run the "python setup.py install" script for updates to take hold**

=======================================================================
## Running SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

To run the pre-compiled binary program, double click on the icon.  It may take 20-30 seconds for the window to open so please be patient.

To run SHARPpy from the command line after installing the code, run the following command:

    $ sharppy

Either of these will load the SHARPpy Sounding Picker GUI.

### Known GUI Issues
<sup>[[Return to Top]](#sharppy)</sup>

Known Issues:
- Moving through time with model profiles may be slow in the Windows binaries because of a backend bug. Running from the code should be fine.

### SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (UW-Madison)
- Greg Blumberg (OU/CIMMS)
- Tim Supinie (OU School of Meteorology)


