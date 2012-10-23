#!/bin/sh
# Prompt for versions
# Clean-up release artifact
# Bump version and tag it
# Build a source distrbution and upload on PyPI
# Update version for new develpoment cycle
VERSION_FILE=djangojs/__init__.py

CURRENT=$(grep __version__ $VERSION_FILE | sed "s/__version__ = '\(.*\)'/\1/")
echo -n "Current version is $CURRENT, what version do you want to release ? "
read RELEASE


python setup.py clean
rm -rf *egg-info build dist
sed -i "s/$CURRENT/$RELEASE/" $VERSION_FILE
git commit $VERSION_FILE -m "Bump version $RELEASE"
git tag $RELEASE
python setup.py register sdist upload

echo -n "Version $RELEASE released, what version do you want for next development cycle ? "
read NEXT

sed -i "s/$RELEASE/$NEXT/" $VERSION_FILE
git commit $VERSION_FILE -m "Updated to version $NEXT for next development cycle"

echo "--------------------------------------------------------------"
echo "Released version $RELEASE and prepare $NEXT development cycle."
