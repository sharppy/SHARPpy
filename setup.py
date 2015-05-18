import os, sys, shutil, glob
from setuptools import setup, find_packages


pkgname = "SHARPpy"


### GET VERSION INFORMATION ###
setup_path = os.path.split(os.path.abspath(__file__))[0]
sys.path.append(os.path.join(setup_path, pkgname.lower()))
import version
version.write_git_version()
ver = version.get_version().split("+")[0]
sys.path.pop()


### ACTUAL SETUP VALUES ###
name = pkgname
version = ver
author = "Patrick Marsh, Kelton Halbert, and Greg Blumberg"
author_email = "patrick.marsh@noaa.gov, keltonhalbert@ou.edu, wblumberg@ou.edu"
description = "Sounding/Hodograph Analysis and Research Program for Python"
long_description = ""
license = "BSD"
keywords = "meteorology soundings analysis"
url = "https://github.com/sharppy/SHARPpy"
packages = ['sharppy', 'sharppy.databases', 'sharppy.io', 'sharppy.sharptab', 'sharppy.viz']
package_data = {"": ["*.md", "*.txt", "*.png", "databases/sars/hail/*", "databases/sars/supercell/*",
                     "databases/shapefiles/*"],}
include_package_data = True
classifiers = ["Development Status :: 4 - Beta"]

HOME_PATH = os.path.join(os.path.expanduser("~"), ".sharppy")

## if the settings directory does not exist, create it and copy the necessary resources
if not os.path.exists(HOME_PATH):
    os.makedirs(HOME_PATH)
    shutil.copytree(os.path.join(os.path.dirname(__file__), "datasources"), os.path.join(HOME_PATH, "datasources"))

## if a datasource XML file exits, we don't want to overwrite it, so copy it to a different file first
if os.path.exists(os.path.join(HOME_PATH, "datasources", "standard.xml")):
    shutil.copy(os.path.join(HOME_PATH, "datasources", "standard.xml"),
                os.path.join(HOME_PATH, "datasources", "standard.xml.old"))

    ## copy over the new file
    shutil.copy(os.path.join(os.path.dirname(__file__), "datasources", "standard.xml"),
                os.path.join(HOME_PATH, "datasources", "standard.xml"))

    ## copy over the standard CSV files
    CSVs = glob.glob(os.path.join(os.path.dirname(__file__), "datasources", "*.csv"))
    for csv in CSVs:
        shutil.copy(csv, os.path.join(HOME_PATH, "datasources", os.path.basename(csv)))


setup(
    name = name,
    version = version,
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
    classifiers = classifiers
)
