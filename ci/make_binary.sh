#!/bin/bash
# Build the binaries

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    conda install -q python.app
    pyinstaller runsharp/SHARPpy-osx.spec --onefile --noconsole; 
#else 
#     pyinstaller runsharp/SHARPpy-linux-redhat5.spec;
fi

ls -lht dist/

