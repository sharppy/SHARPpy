#!/bin/bash
# Inspired by: https://gist.github.com/zshaheen/fe76d1507839ed6fbfbccef6b9c13ed9

# Download conda-build
echo "Download conda-build and anaconda-client"
#conda install -q -c anaconda conda-build
#conda install -q -c anaconda anaconda-client
#conda install -q jinja2 setuptools

# Set environmental variables 
USER=sharppy
OS=$TRAVIS_OS_NAME-64

# Make the build output directory
echo "Make the build output directory"
mkdir ~/conda-bld
conda config --set anaconda_upload no

# Set the build path and the current version
export CONDA_BLD_PATH=~/conda-bld

# Build the conda recipe
echo "Build the conda recipe for Python 3.6"
conda build --python 36 conda-recipe/

# Convert the conda package to support other operating systems
echo "*** Coverting to Windows 64 ***"
conda convert -q -p win-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py36*.tar.bz2
#echo "*** Coverting to Linux 64 ***"
#conda convert -q -p linux-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py36*.tar.bz2
echo "*** Coverting to OS X 64 ***"
conda convert -q -p osx-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py36*.tar.bz2
echo "*** LIST PACKAGES ***"
ls $CONDA_BLD_PATH

echo "Uploading Python 3.6 packages to anaconda.org"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u sharppy $CONDA_BLD_PATH/*/*py36*.tar.bz2 --force

echo "Build the conda recipe for Python 3.7"
conda build --python 37 conda-recipe/
echo "*** Coverting to Windows 64 ***"
conda convert -q -p win-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py37*.tar.bz2
#echo "*** Coverting to Linux 64 ***"
#conda convert -q -p linux-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py37*.tar.bz2
echo "*** Coverting to OS X 64 ***"
conda convert -q -p osx-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*py37*.tar.bz2

echo "*** LIST PACKAGES ***"
ls $CONDA_BLD_PATH

echo "Uploading Python 3.7 packages to anaconda.org"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u sharppy $CONDA_BLD_PATH/*/*py37*.tar.bz2 --force


#echo "ENDING BUILD CONDA SCRIPT EARLY BECAUSE TESTING"
#exit 0

# Upload to the conda package manager
#rm -rf ~/conda-bld
