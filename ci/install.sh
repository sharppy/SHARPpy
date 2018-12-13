#!/bin/bash
echo $PYTHON_VERSION

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    if [[ "$PYTHON_VERSION" == "2.7" ]]; then
        curl https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh -o miniconda.sh;
    else
        curl https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o miniconda.sh;
    fi 
  else 
    if [[ "$PYTHON_VERSION" == "2.7" ]]; then 
        wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh; 
    else 
        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; 
  fi
fi

bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a
conda create -q -n test-environment python=$PYTHON_VERSION numpy nose 
source activate test-environment
conda install -q pyside pyinstaller

# If we're building on OSX, we need to download python.app to get around the qt_menu.nib problem.
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then conda install python.app; fi
