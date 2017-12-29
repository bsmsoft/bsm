#!/bin/sh

cd $(dirname "$0")/..

version=$(cat cepcenv/CEPCENV_VERSION)

git commit -a -m "Release version $version"

git tag -a "v$version" -m "Version $version"

git push origin
git push origin "v$version"
