#!/bin/bash
# Inspired by: https://gist.github.com/zshaheen/fe76d1507839ed6fbfbccef6b9c13ed9

# Download conda-build
echo "Download conda-build and anaconda-client"
#conda install -q conda-build anaconda-client

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
conda convert -p all -o $CONDA_BLD_PATH $CONDA_BLD_PATH/*-*/*.tar.bz2

# Upload to the conda package manager
anaconda -t $CONDA_UPLOAD_TOKEN upload -u sharppy -l release $CONDA_BLD_PATH/*/*.tar.bz2 --force
#rm -rf ~/conda-bld
