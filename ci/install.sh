#!/bin/bash
echo $PYTHON_VERSION

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; 
bash miniconda.sh -b
export PATH=/home/travis/miniconda3/bin:$PATH
conda config --set always_yes yes
conda config --set show_channel_urls true
conda update -q conda

conda env create -f ci/environment-$PYTHON_VERSION.yml
source activate testenv

pip install --upgrade pip

if [[ "$BUILD_CONDA" == "YES" ]]; then
    conda install -q conda-build
    conda install -q jinja2 setuptools
fi

# If we're building on OSX, we need to download python.app to get around the qt_menu.nib problem.
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    conda install -q python.app;
fi
