#!/bin/bash
# Inspired by: https://gist.github.com/zshaheen/fe76d1507839ed6fbfbccef6b9c13ed9

# Download conda-build
conda install -q conda-build anaconda

# Set environmental variables 
PKG_NAME=sharppy
USER=sharppy
OS=$TRAVIS_OS_NAME-64

# Make the build output directory
mkdir ~/conda-bld
conda config --set anaconda_upload no

# Set the build path and the current version
export CONDA_BLD_PATH=~/conda-bld
export VERSION=`date +%Y.%m.%d`

# Build the conda recipe
conda build ../conda_recipe/

# Convert the conda package to support other operating systems
conda convert $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-o.tar.bz2 - p all

# Upload to the conda package manager
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-0.tar.bz2 --force

