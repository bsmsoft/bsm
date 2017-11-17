#!/bin/sh

pypy_url='http://cepcsoft.ihep.ac.cn/package/cepcenv/pypy/pypy-current-linux_x86_64-portable.tar.bz2'
pypy_origin_url='https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.9-linux_x86_64-portable.tar.bz2'

retry_time=5

download_http() {
  if which curl >/dev/null 2>&1; then
    curl --retry $retry_time -L "$1"
  elif which wget >/dev/null 2>&1; then
    wget -t $retry_time -O - "$1"
  else
    echo >&2 "Please install curl or wget first"
    exit 1
  fi
}

main() {
  if [ $# -gt 1 ]; then
    echo >&2 "Only one parameter allowed"
    exit 2
  fi

  if [ $# -eq 0 ]; then
    install_dir='.'
  else
    install_dir="$1"
  fi

  mkdir -p "$install_dir"

  cd "$install_dir"
  install_full_dir="$(pwd)"

  echo >&2 "Install cepcenv in the directory: \"$install_full_dir\""

  rm -rf pypy*

  download_http "$pypy_url" | tar xj

  cd pypy*
  pypy_dir_name=$(basename "$(pwd)")
  cd ..
  mv "$pypy_dir_name" pypy

  pypy/bin/pypy -m ensurepip
  pypy/bin/pip install -U pip wheel

  pypy/bin/pip install cepcenv

  echo "eval \"\$('${install_full_dir}/pypy/bin/cepcenv_cmd' init)\"" > setup.sh
}

main "$@"
