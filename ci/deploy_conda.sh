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
echo "Build the conda recipe"
conda build conda-recipe/ --python=3.6
conda build conda-recipe/ --python=3.7

# Convert the conda package to support other operating systems
echo "Convert the recipe to other OSes"
ls $CONDA_BLD_PATH
echo "Coverting to Windows 64"
conda convert -q -p win-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*.tar.bz2
echo "Coverting to Linux 64"
conda convert -q -p linux-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*.tar.bz2
echo "Coverting to OS X 64"
conda convert -q -p osx-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/$OS/*.tar.bz2
ls $CONDA_BLD_PATH

#echo "ENDING BUILD CONDA SCRIPT EARLY BECAUSE TESTING"
#exit 0

echo "Which anaconda"
which anaconda
# Upload to the conda package manager
anaconda -t $CONDA_UPLOAD_TOKEN upload -u sharppy $CONDA_BLD_PATH/*/*.tar.bz2 --force
#rm -rf ~/conda-bld
