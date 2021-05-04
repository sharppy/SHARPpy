# SHARPpy

###### Sounding/Hodograph Analysis and Research Program in Python

[![Build status](https://travis-ci.org/sharppy/SHARPpy.svg?branch=master)](https://travis-ci.org/sharppy)
[![Build Status](https://dev.azure.com/sharppy/SHARPpy/_apis/build/status/sharppy.SHARPpy?branchNammasterr)](https://dev.azure.com/sharppy/SHARPpy/_build/latest?definitionId=1?branchName=master)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/downloads.svg)](https://anaconda.org/conda-forge/sharppy)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/license.svg)](https://anaconda.org/conda-forge/sharppy)
[![](https://img.shields.io/github/downloads/sharppy/SHARPpy/total.svg?style=popout)](https://github.com/sharppy/SHARPpy/releases)
[![Coverage Status](https://coveralls.io/repos/github/sharppy/SHARPpy/badge.svg?branch=master)](https://coveralls.io/github/sharppy/SHARPpy?branch=master)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/platforms.svg)](https://anaconda.org/conda-forge/sharppy)

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

### Important links:
* HTML Documentation: http://sharppy.github.io/SHARPpy/index.html
* GitHub repository: https://github.com/Jeff-Szkodzinski/SHARPpy

**Table of Contents**

- [Install Pre-requisites](#install-pre-requisites)
- [Install the NUCAPS test branch in SHARPpy](#install-the-nucaps-test-branch-in-sharppy)
- [Running SHARPpy from the Command Line](#running-sharppy-from-the-command-line)
- [SHARPpy Development Team](#sharppy-development-team)

=======================================================================
## Install Pre-requisites
<sup>[[Return to Top]](#sharppy)</sup>

You will need Python 3 to run SHARPpy. For instructions, visit the following websites:
* https://www.anaconda.com/products/individual for instructions on how to set-up Python.

You will need run a few simple commands in a command line program:
* Linux/MacOS: Open the Terminal application.
* Windows: Open the Anaconda Prompt applications.

=======================================================================
## Install the NUCAPS test branch in SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

You can now install the beta version of SHARPpy which contains NUCAPS satellite soundings. Open the command line for your operating system (see above) to perform these steps.

```bash
git clone https://github.com/Jeff-Szkodzinski/SHARPpy.git
```

Change your directory to where you have downloaded SHARPpy (e.g. /home/{user}/SHARPpy).

```bash
cd /home/<user>/SHARPpy
```

Next, we to create an isolated Anaconda environment just for running SHARPpy with all the necessary libraries (using conda env create {options}; it may take several minutes to install the libraries). If you are interested, you can open the environment.yml file to see which libraries are used.

```bash
conda env create -f environment.yml
```

After creating the environment, we need to switch to this new environment (via conda activate {env_name}) which we have named devel.

```bash
conda activate devel
```

Run setup.py to apply our NUCAPS updates to SHARPpy.

```bash
python setup.py install
```

Once the installation is complete, keep the terminal open and follow the steps in the next section to launch SHARPpy.

=======================================================================
## Running SHARPpy from the Command Line
<sup>[[Return to Top]](#sharppy)</sup>

In the command line, type the command sharppy to launch the program.

```bash
sharppy
```

If successful, a window will open which will give you access to soundings from NUCAPS, RAOBS, and select models.  For instructions on using SHARPpy, see the “Display NUCAPS in SHARPpy” quick guide.

=======================================================================
## SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (UW-Madison)
- Greg Blumberg (NASA GSFC)
- Tim Supinie (OU School of Meteorology)
- Jeff Szkodzinski (Science and Technology Corp.)
