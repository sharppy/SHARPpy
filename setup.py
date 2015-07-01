import os, sys, shutil, glob, getpass, platform
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
author = "Patrick Marsh, Kelton Halbert, Greg Blumberg, and Tim Supinie"
author_email = "patrick.marsh@noaa.gov, keltonhalbert@ou.edu, wblumberg@ou.edu, tsupinie@ou.edu"
description = "Sounding/Hodograph Analysis and Research Program for Python"
long_description = ""
license = "BSD"
keywords = "meteorology soundings analysis"
url = "https://github.com/sharppy/SHARPpy"
packages = ['sharppy', 'sharppy.databases', 'sharppy.io', 'sharppy.sharptab', 'sharppy.viz', 'utils']
package_data = {"": ["*.md", "*.txt", "*.png", "databases/sars/hail/*", "databases/sars/supercell/*",
                     "databases/shapefiles/*"],}
include_package_data = True
classifiers = ["Development Status :: 4 - Beta"]

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
    shutil.copy(os.path.join(HOME_DSDIR, "data_source.py"),
                os.path.join(HOME_DSDIR, "data_source.py.old"))
 
    shutil.copy(os.path.join(SRC_DSDIR, "available.py"),
                os.path.join(HOME_DSDIR, "available.py"))
    shutil.copy(os.path.join(SRC_DSDIR, "data_source.py"),
                os.path.join(HOME_DSDIR, "data_source.py"))

if platform.system() in [ 'Darwin', 'Linux' ] and getpass.getuser() == 'root':
    # If we're running with sudo, chown the directories and files to the user actually running the process.
    uid = int(os.environ['SUDO_UID'])
    gid = int(os.environ['SUDO_GID'])

    os.chown(HOME_PATH, uid, gid)

    for root, dirs, files in os.walk(HOME_PATH):
        for dirname in dirs:
            os.chown(os.path.join(root, dirname), uid, gid)

        for filename in files:
            os.chown(os.path.join(root, filename), uid, gid)

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
