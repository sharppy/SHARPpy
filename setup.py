import os, sys
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
packages = find_packages()
package_data = {"": ["*.md", "*.txt", "*.png"],}
include_package_data = True
classifiers = ["Development Status :: 2 - Pre-Alpha"]


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
