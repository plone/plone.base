#!/bin/sh
# This script works best when run in GitHub Actions or using tox:
# then it will take the correct Python version.
BASEDIR=$(dirname $(realpath $0))
python -m pip install --upgrade pip
pip install wheel mxdev libvcs==0.11.1
mxdev -c sources.ini
pip install -r${BASEDIR}/requirements-mxdev.txt
python -V
pip list
