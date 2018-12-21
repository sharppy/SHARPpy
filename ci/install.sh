#!/bin/bash
echo $PYTHON_VERSION

if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; 
else
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O miniconda.sh; 
fi

bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r

conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda install -n -q root _license

conda config --add channels conda-forge
conda env create -f ci/environment-$PYTHON_VERSION.yml
source activate testenv

pip install --upgrade pip

# If we're building on OSX, we need to download python.app to get around the qt_menu.nib problem.
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    conda install -q python.app;
fi
