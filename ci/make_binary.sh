#!/bin/bash
# Build the binaries
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
     pyinstaller runsharp/SHARPpy-osx.spec --onefile --noconsole; 
else 
     pyinstaller runsharp/SHARPpy-linux-redhat5.spec;
fi

ls -lht dist/

