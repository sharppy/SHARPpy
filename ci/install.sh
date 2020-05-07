#!/bin/bash
echo $PYTHON_VERSION
which python

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    echo "OSX OS"
    if [[ "$PYTHON_VERSION" == "2.7" ]]; then
        curl https://repo.anaconda.com/miniconda/Miniconda2-latest-MacOSX-x86_64.sh -o miniconda.sh;
    else
        curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o miniconda.sh;
    fi 
else 
    echo "NON OSX OS"
    if [[ "$PYTHON_VERSION" == "2.7" ]]; then 
        wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh; 
    else 
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; 
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
conda env create -f environment.yml
source activate devel
conda install -c conda-forge -q pytest-cov conda-build anaconda-client

if [[ "$COVERALLS" == "YES" ]]; then
    echo "Installing coveralls ..."
    conda install -c conda-forge -q coveralls
fi

# If we're building on OSX, we need to download python.app to get around the qt_menu.nib problem.
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
    conda install -q python.app;
fi
