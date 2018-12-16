#!/bin/bash
# Adapted from the ci/build_docs.sh file from the pandas and pyart project
# https://github.com/pydata/pandas
set -e

cd "$TRAVIS_BUILD_DIR"

if [[ "$BUILD_DOCS" == "YES" ]]; then 
    conda install -q -c conda-forge sphinx sphinx-gallery;
    conda install -q -c anaconda sphinx_rtd_theme 
else
    exit 0
fi

openssl aes-256-cbc -K $encrypted_08ee84f00b5d_key -iv $encrypted_08ee84f00b5d_iv -in deploy_key.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

echo "Building Docs"
cd docs
make html

# upload to pyart-docs-travis repo is this is not a pull request and
# secure token is available (aka in the ARM-DOE repository.
#if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ $TRAVIS_SECURE_ENV_VARS == 'true' ]; then
#if [[ $TRAVIS_SECURE_ENV_VARS == 'true' ]]; then
cd build/html
git config --global user.email "sharppy-docs-bot@example.com"
git config --global user.name "sharppy-docs-bot"

git init
touch README
git add README
git commit -m "Initial commit" --allow-empty
git branch gh-pages
git checkout gh-pages
touch .nojekyll
git add --all .
git commit -m "Version" --allow-empty -q
git remote add origin https://github.com/sharppy/SHARPpy.git
# &> /dev/null
git push origin gh-pages -fq 
#&> /dev/null
#   fi

exit 0
