#!/bin/bash
# Inspired by: https://gist.github.com/zshaheen/fe76d1507839ed6fbfbccef6b9c13ed9

# Deactivate the current environment
source deactivate

# Download conda-build
echo "Download conda-build and anaconda-client"
conda install -q conda-build anaconda-client
conda install -q jinja2 setuptools
conda config --add channels conda-forge

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
conda build conda-recipe/

# Convert the conda package to support other operating systems
echo "Convert the recipe to other OSes"
conda convert -q -p win-32 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/osx-64/*.tar.bz2
conda convert -q -p win-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/osx-64/*.tar.bz2
conda convert -q -p linux-32 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/osx-64/*.tar.bz2
conda convert -q -p linux-64 -o $CONDA_BLD_PATH $CONDA_BLD_PATH/osx-64/*.tar.bz2

# Upload to the conda package manager
anaconda -t $CONDA_UPLOAD_TOKEN upload -u sharppy $CONDA_BLD_PATH/*/*.tar.bz2 --force
#rm -rf ~/conda-bld
