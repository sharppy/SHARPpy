import os, sys, shutil, glob, getpass, platform
from setuptools import setup, find_packages
import versioneer
pkgname = "SHARPpy"


### GET VERSION INFORMATION ###
setup_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(setup_path, pkgname.lower()))
#import _sharppy_version as version
#version.write_git_version()
#ver = version.get_version().split("+")[0]

sys.path.pop()


### ACTUAL SETUP VALUES ###
name = pkgname
#version = ver
author = "Patrick Marsh, Kelton Halbert, Greg Blumberg, and Tim Supinie"
author_email = "patrick.marsh@noaa.gov, keltonhalbert@ou.edu, wblumberg@ou.edu, tsupinie@ou.edu"
description = "Sounding/Hodograph Analysis and Research Program for Python"
long_description = "SHARPpy is a collection of open source sounding and hodograph analysis routines, a sounding plotting package, and an interactive, cross-platform application for analyzing real-time soundings all written in Python. It was developed to provide the atmospheric science community a free and consistent source of sounding analysis routines. SHARPpy is constantly updated and vetted by professional meteorologists and climatologists within the scientific community to help maintain a standard source of sounding routines."
license = "BSD"
keywords = "meteorology soundings analysis"
url = "https://github.com/sharppy/SHARPpy"
packages = ['sharppy', 'sharppy.databases', 'sharppy.io', 'sharppy.sharptab', 'sharppy.viz', 'utils', 'datasources', 'sharppy.plot', 'runsharp']
package_data = {"": ["*.md", "*.txt", "*.png", "databases/sars/hail/*", "databases/sars/supercell/*",
                     "databases/shapefiles/*", "../rc/*"],}
include_package_data = True

install_requires = ['python-dateutil', 'requests', 'numpy==1.15.*']
# Because pip doesn't recognize it when PySide is installed by conda from conda-forge
# Try to import PySide.  If it fails, add the PySide to the install_requires
try:
    import PySide
    print("Success importing PySide")
except:
    install_requires.append("PySide==1.2.*")    

entry_pts = {"console_scripts": ['sharppy = runsharp.full_gui:main'] }
# Create some directory variables to shorten the lines.
HOME_PATH = os.path.join(os.path.expanduser("~"), ".sharppy")
HOME_DSDIR = os.path.join(HOME_PATH, "datasources")
SRC_DSDIR = os.path.join(os.path.dirname(__file__), "datasources")

## if the settings directory does not exist, create it and copy the necessary resources
if not os.path.exists(HOME_PATH):
    os.makedirs(HOME_PATH)
    shutil.copytree(SRC_DSDIR, HOME_DSDIR)

## if a datasource XML file exits, we don't want to overwrite it, so copy it to a different file first
if os.path.exists(os.path.join(HOME_DSDIR, "standard.xml")):
    shutil.copy(os.path.join(HOME_DSDIR, "standard.xml"),
                os.path.join(HOME_DSDIR, "standard.xml.old"))

## copy over other XML files
XMLs = glob.glob(os.path.join(SRC_DSDIR, "*.xml"))
for xml in XMLs:
    shutil.copy(xml, os.path.join(HOME_DSDIR, os.path.basename(xml)))

## copy over the standard CSV files
CSVs = glob.glob(os.path.join(SRC_DSDIR, "*.csv"))
for csv in CSVs:
    shutil.copy(csv, os.path.join(HOME_DSDIR, os.path.basename(csv)))

if os.path.exists(os.path.join(HOME_DSDIR, "available.py")):
    # Copy over available.py and data_source.py
    shutil.copy(os.path.join(HOME_DSDIR, "available.py"),
                os.path.join(HOME_DSDIR, "available.py.old"))
 
shutil.copy(os.path.join(SRC_DSDIR, "available.py"),
            os.path.join(HOME_DSDIR, "available.py"))


ver = versioneer.get_version()
ver = ver.split('-')[0]
if 'a' in ver:
    classifiers = ["Development Status :: 3 - Alpha"]
elif 'b' in ver:
    classifiers = ["Development Status :: 4 - Beta"]
else:
    classifiers = ["Development Status :: 5 - Production/Stable"]

setup(
    name = name,
    author = author,
    author_email = author_email,
    description = description,
    long_description = long_description,
    license = license,
    keywords = keywords,
    url = url,
    packages = packages,
    package_data = package_data,
    include_package_data = include_package_data,
    classifiers = classifiers,
    version=ver,
    cmdclass=versioneer.get_cmdclass(),
    install_requires=install_requires,
    entry_points = entry_pts
)
