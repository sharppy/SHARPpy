# SHARPpy

###### Sounding/Hodograph Analysis and Research Program in Python

[![Test Status](https://github.com/NUCAPS/SHARPpy/actions/workflows/pytest.yml/badge.svg?branch=master)](https://github.com/NUCAPS/SHARPpy/actions/workflows/pytest.yml)
[![Build Status](https://github.com/NUCAPS/SHARPpy/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/NUCAPS/SHARPpy/actions/workflows/build.yml)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/downloads.svg)](https://anaconda.org/conda-forge/sharppy)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/license.svg)](https://anaconda.org/conda-forge/sharppy)
[![](https://img.shields.io/github/downloads/sharppy/SHARPpy/total.svg?style=popout)](https://github.com/sharppy/SHARPpy/releases)
[![Coverage Status](https://coveralls.io/repos/github/sharppy/SHARPpy/badge.svg?branch=master)](https://coveralls.io/github/sharppy/SHARPpy?branch=master)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/sharppy/badges/platforms.svg)](https://anaconda.org/conda-forge/sharppy)

SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, __cross-platform__ application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines.

The version of SHARPpy in this repository allows users to access [NUCAPS](https://weather.msfc.nasa.gov/nucaps/), a satellite sounding product.

### Important links:
* HTML Documentation: http://sharppy.github.io/SHARPpy/index.html
* GitHub repository: https://github.com/sharppy/SHARPpy

**Table of Contents**

- [Install Pre-requisites](#install-pre-requisites)
- [Install SHARPpy](#install-sharppy)
- [Running SHARPpy from the Command Line](#running-sharppy-from-the-command-line)
- [SHARPpy Development Team](#sharppy-development-team)

=======================================================================
## Install Pre-requisites
<sup>[[Return to Top]](#sharppy)</sup>

You will need Python 3 to run SHARPpy. For instructions, visit the following websites:
* https://www.anaconda.com/products/individual for instructions on how to set-up Python.

You will need run a few simple commands in a command line program:
* Linux/MacOS: Open the Terminal application.
* Windows: Open the Anaconda Prompt application.

Note: If you are installing Anaconda for **multiple users**, [ensure these additional steps are met](https://docs.anaconda.com/anaconda/install/multi-user/), which includes checking the permissions using an administrator account.

=======================================================================
## Install SHARPpy
<sup>[[Return to Top]](#sharppy)</sup>

For those wishing to run both the GUI and do scripting, we recommend you install the Python 3 Anaconda Python Distribution from Continuum Analytics. You can install SHARPpy from conda by using:

```bash
conda install -c conda-forge sharppy
```
Skip to the 'Running SHARPpy from the Command Line' section.

### Download options
If you aren't downloading from conda forge, you can download sharppy using the following options.

### Option 1: Manual download (easy)

You can manually download the coding by clicking the "Code" button at the top right of the repository, then select "Download Zip." Unzip the files in the directory that you want to permanently store them.

### Option 2: Download using Git (intermediate)

If you have Git installed and are familiar with it, open the command line for your operating system (see above) to perform these steps.

```bash
git clone https://github.com/sharppy/SHARPpy
```

### Install SHARPpy

Open the terminal (UNIX/Linux) or Anaconda Prompt (Windows) and change your directory to where you have downloaded SHARPpy (e.g. /home/{user}/SHARPpy).

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

Run setup.py to update SHARPpy.

```bash
python setup.py install
```

Once the installation is complete, keep the terminal open and follow the steps in the next section to launch SHARPpy.

### Running SHARPpy from the Command Line

In the command line, type the command sharppy to launch the program.

```bash
sharppy
```

If successful, a window will open which will give you access to soundings from NUCAPS, RAOBS, and select models.  For instructions on using SHARPpy, see the “Display NUCAPS in SHARPpy” quick guide.

### How to run SHARPpy next time you log on

If you close the terminal window, you will have to repeat the following steps:

1. Open the terminal (Unix/Linux) or Anaconda Prompt (Windows)
2. Switch your environment to devel ("conda activate devel")
3. Type sharppy and the window should launch.

```bash
conda activate devel
sharppy
```

=======================================================================
## SHARPpy Development Team
<sup>[[Return to Top]](#sharppy)</sup>

SHARPpy is currently managed by the following co-developers (in no particular order):
- Patrick Marsh (SPC)
- Kelton Halbert (UW-Madison)
- Greg Blumberg (NASA GSFC)
- Tim Supinie (OU School of Meteorology)
- Rebekah Esmaili (Science and Technology Corp.)
- Jeff Szkodzinski (Science and Technology Corp.)
