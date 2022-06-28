cp ../LICENSE.rst source/license.rst
cp ../CONTRIBUTING.rst source/contributing.rst
cp ../CHANGELOG.rst source/changelog.rst

rm -r build
make html
