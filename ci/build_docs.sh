#!/bin/bash
# Adapted from the ci/build_docs.sh file from the pandas and pyart project
# https://github.com/pydata/pandas
set -e
conda init bash

echo "Installing sphinx, etc. to build the documentation ..."
cd "$TRAVIS_BUILD_DIR"

# Swap out conda environments for one that supports building the documentation
conda deactivate
conda env create -f ci/docs_env.yml
conda activate docs-env

echo "Adding the SSH key ..."
cd ci/
openssl aes-256-cbc -K $encrypted_08ee84f00b5d_key -iv $encrypted_08ee84f00b5d_iv -in deploy_key.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key


# Build the documentation
cd ..
echo "Building Docs"
cd docs

# Move the license and other stuff to the docs folder
echo "Copying over some of the files to be included in the documentation ..."
cp ../LICENSE.rst ../docs/source/license.rst
cp ../CONTRIBUTING.rst ../docs/source/contributing.rst
cp ../CHANGELOG.rst ../docs/source/changelog.rst

# Run sphinx
echo "Running Sphinx ..."
make html

#echo "ENDING BUILD OF DOCS EARLY BECAUSE OF TESTING"
#exit 0

# upload to pyart-docs-travis repo is this is not a pull request and
# secure token is available (aka in the ARM-DOE repository.
#if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ $TRAVIS_SECURE_ENV_VARS == 'true' ]; then
#if [[ $TRAVIS_SECURE_ENV_VARS == 'true' ]]; then
cd build/html
pwd
git config --global user.email "sharppy-docs-bot@example.com"
git config --global user.name "sharppy-docs-bot"

# Save some useful information
REPO=https://github.com/sharppy/SHARPpy.git
SSH_REPO=git@github.com:sharppy/SHARPpy.git
SHA=`git rev-parse --verify HEAD`

cd ../..
pwd
# Clone the existing gh-pages for this repo into out/
# Create a new empty branch if gh-pages doesn't exist yet (should only happen on first deply)
git clone $REPO out
cd out
ls -l
pwd
git checkout gh-pages || git checkout --orphan gh-pages
cd ..
pwd
rm -rf out/**/*
cp -r build/html/* out/
rm -rf out/.gitignore
touch out/.nojekyll
cd out
pwd
ls -l
git add --all .
git add .nojekyll
echo "ADDING FILES"
git commit -m "Deploy to GitHub Pages: ${SHA}"
git push $SSH_REPO gh-pages

exit 0
