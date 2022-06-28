#!/bin/bash
# Adapted from the ci/build_docs.sh file from the pandas and pyart project
# https://github.com/pydata/pandas
set -e

echo "**************************************************************************************"
echo "Step 0: Installing sphinx, etc. to build the documentation ..."
echo "**************************************************************************************"
cd "$TRAVIS_BUILD_DIR"

# Swap out conda environments for one that supports building the documentation
cd ci/
conda env create -f docs_env.yml
source activate docs-env

cd ..
pip install -e .
cd ci/

echo "**************************************************************************************"
echo "Step 1: Adding the SSH key ..."
echo "**************************************************************************************"
openssl aes-256-cbc -K $encrypted_08ee84f00b5d_key -iv $encrypted_08ee84f00b5d_iv -in deploy_key.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

# Build the documentation
echo "**************************************************************************************"
echo "Step 2: Building Docs"
echo "**************************************************************************************"
cd ../docs

# Move the license and other stuff to the docs folder
echo "**************************************************************************************"
echo "Step 3: Copying over some of the files to be included in the documentation ..."
echo "**************************************************************************************"
cp ../LICENSE.rst ../docs/source/license.rst
cp ../CONTRIBUTING.rst ../docs/source/contributing.rst
cp ../CHANGELOG.rst ../docs/source/changelog.rst

# Run sphinx
echo "**************************************************************************************"
echo "Step 4: Running Sphinx ..."
echo "**************************************************************************************"
make html

#echo "ENDING BUILD OF DOCS EARLY BECAUSE OF TESTING"
#exit 0

# upload to pyart-docs-travis repo is this is not a pull request and
# secure token is available (aka in the ARM-DOE repository.
#if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ $TRAVIS_SECURE_ENV_VARS == 'true' ]; then
#if [[ $TRAVIS_SECURE_ENV_VARS == 'true' ]]; then
echo "**************************************************************************************"
echo "Step 5: Preparing built documentation to be uploaded to Github"
echo "**************************************************************************************"
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
echo "**************************************************************************************"
echo "Step 6: Pushing documentation to Github Pages."
echo "**************************************************************************************"
git commit -m "Deploy to GitHub Pages: ${SHA}"
git push $SSH_REPO gh-pages --force

exit 0
