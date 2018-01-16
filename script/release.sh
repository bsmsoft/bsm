#!/bin/sh

cd $(dirname "$0")/..

version=$(cat bsm/BSM_VERSION)

git commit -a -m "Release version $version"

git tag -a "v$version" -m "Version $version"

git push origin
git push origin "v$version"
