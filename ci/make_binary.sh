#!/bin/bash
# Build the binaries
cd "$TRAVIS_BUILD_DIR"

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    if [[ "$PYTHON_VERSION" == "3.6" ]]; then 
        pyinstaller runsharp/SHARPpy-osx.spec --onefile --noconsole; 
    fi
#else 
#     pyinstaller runsharp/SHARPpy-linux-redhat5.spec;
fi

ls -lht dist/

