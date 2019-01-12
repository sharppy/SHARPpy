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
conda install -n -q root _license
conda info -a
conda config --add channels conda-forge 
conda create -q -n test-environment python=$PYTHON_VERSION pyside pyinstaller requests python-dateutil conda-build anaconda-client numpy=$NUMPY_VERSION
source activate test-environment

pip install --upgrade pip
conda install -c conda-forge -q pytest-cov
if [[ "$COVERALLS" == "YES" ]]; then
    echo "Installing coveralls ..."
    conda install -c conda-forge -q coveralls
fi

# If we're building on OSX, we need to download python.app to get around the qt_menu.nib problem.
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    conda install -q python.app;
fi
