#!/bin/sh

cd $(dirname "$0")/..

rm -rf dist

python setup.py sdist || { echo >&2 'sdist failed. Aborting.'; exit 1; }
python setup.py bdist_wheel || { echo >&2 'bdist failed. Aborting.'; exit 1; }

twine upload dist/*
