.. _Installation_Guide_:

Installation Guide
==================

SHARPpy can be installed in one of two forms: either a pre-compiled binary executable or by downloading the code and installing it using a separate Python interpreter.  Binary executables are available for Windows 7 (32 and 64 bit), Windows 8.1 (64 bit only), and Mac OS X 10.6+ (Snow Leopard and later; 64 bit only).  If you do not have one of those, then you will need to download the code.

Installing a Pre-compiled Binary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following pre-compiled binaries are available (click to download):

[OS X (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-osx-64.zip)

[Windows 7 (32 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-32.zip)

[Windows 7 (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win7-64.zip)

[Windows 8.1 and Windows 10 (64 Bit)](https://github.com/sharppy/SHARPpy/releases/download/v1.3.0-Xenia-beta/sharppy-win8.1-64.zip)

Installing a pre-compiled binary *should* be as simple as downloading the .zip file and extracting it to the location of your choice.  The zip files are named for the operating system and number of bits.  Most recently-built computers (probably post-2010 or so) should have 64-bit operating systems installed.  If your computer is older and you're unsure whether it has a 32- or 64-bit operating system, you can check on Windows 7 by clicking Start, right-clicking on Computer, and selecting Properties.  All recent versions of OS X (10.6 and newer) should be 64-bit.

Installing the Code from Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SHARPpy code can be installed on *Windows, Mac OS X, and Linux*, as all these platforms can run Python programs.  SHARPpy may run on other operating systems, but this has not been tested by the developers.  Chances are if it can run Python, it can run SHARPpy.  Running the SHARPpy code requires a.) the Python interpreter and b.) additional Python libraries.  Although there are multiple ways to meet these requirements, we recommend you install the *Python 3.6* version of the Anaconda Python distribution.  SHARPpy is primarily tested using this distribution.

The Anaconda Python Distribution can be downloaded here: https://store.continuum.io/cshop/anaconda/

Additional ways to meet these requirements may include the Enthought Python Distribution, MacPorts, or Brew, but as of this moment we cannot provide support for these methods.

*Required Python Packages/Libraries:*

- NumPy

- PySide

Since SHARPpy requires the PySide and Numpy packages, you will need to install them.  If you choose to use the Anaconda distribution, Numpy comes installed by default.  PySide can be installed through the Anaconda package manager that comes with the Anaconda distribution by opening up your command line program (Terminal in Mac OS X/Linux and Command Prompt in Windows) and typing:

    ``conda install -c conda-forge pyside=1.2.4``


After installing all the required Python packages for SHARPpy, you now can install the SHARPpy package to your computer.  You'll need to download it to your computer first and open up a command line prompt.  You can download it as a ZIP file (link on the right) or clone the Git respository (you will need the git program) into a directory on your computer by typing this into your command line:

    ``git clone https://github.com/sharppy/SHARPpy.git``

If you follow the route of cloning SHARPpy, you can update to the most recent SHARPpy package by typing the following within the folder you downloaded SHARPpy to:

    ``git pull origin master``

Once the package has been downloaded to your computer, use your command line to navigate into the SHARPpy directory and type this command in to install SHARPpy:

    ``python setup.py install``

After installing the package, you can run the SHARPpy GUI and interact with the SHARPpy libraries through Python scripts.
