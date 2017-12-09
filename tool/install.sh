#!/bin/sh

pypy_url='http://cepcsoft.ihep.ac.cn/package/cepcenv/pypy/pypy-current-linux_x86_64-portable.tar.gz'
pypy_origin_url='https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.9-linux_x86_64-portable.tar.bz2'
gitmini_url='http://cepcsoft.ihep.ac.cn/package/cepcenv/gitmini/gitmini.tar.gz'

retry_time=5

download_http() {
  if command -v curl >/dev/null 2>&1; then
    curl --retry $retry_time -f -L -O "$1"
  elif command -v wget >/dev/null 2>&1; then
    wget -t $retry_time "$1"
  else
    echo >&2 "Please install curl or wget first"
    exit 1
  fi
}

download_and_extract() {
  url=$1
  download_http "$url" || { echo >&2 "Download pypy failed: ${url}"; return 1; }

  fn=$(basename "$url")
  tar -xf "$fn" || { echo >&2 "Extract pypy failed: ${fn}"; return 1; }
  rm -rf "$fn"
}

install_pypy() {
  rm -rf pypy*

  download_and_extract "$pypy_url" || download_and_extract "$pypy_origin_url" || { echo >&2 "Download or extract pypy failed. Aborting."; exit 1; }

  cd pypy*
  pypy_dir_name=$(basename "$(pwd)")
  cd ..
  mv "$pypy_dir_name" pypy

  pypy/bin/pypy -m ensurepip
  pypy/bin/pip install -U pip wheel

  pypy/bin/pip install cepcenv
}

install_gitmini() {
  mkdir -p gitmini
  cd gitmini

  if ! download_http "$gitmini_url" >/dev/null 2>&1; then
    cd ..
    rm -rf gitmini
    return 1
  fi

  fn=$(basename "$gitmini_url")
  if ! tar -xf "$fn" >/dev/null 2>&1; then
    cd ..
    rm -rf gitmini
    return 1
  fi

  rm -rf "$fn"

  cd ..
  return $gitmini_exit
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

  mkdir -p "$install_dir" || { echo >&2 "Can not create directory ${install_dir}. Aborting."; exit 1; }

  cd "$install_dir"
  install_full_dir="$(pwd)"

  echo >&2 "Install CEPCEnv in the directory: \"$install_full_dir\""

  install_pypy

  rm -f setup.sh setup.csh

  if install_gitmini; then
    echo "export _CEPCENV_GITTEMP='${install_full_dir}/gitmini/gitmini'\n" >> setup.sh
    echo "setenv _CEPCENV_GITTEMP '${install_full_dir}/gitmini/gitmini'\n" >> setup.csh
  fi

  echo "eval \"\$('${install_full_dir}/pypy/bin/cepcenv_cmd' --shell sh init)\"" >> setup.sh
  echo "eval \"\`'${install_full_dir}/pypy/bin/cepcenv_cmd' --shell csh init\`\"" >> setup.csh

  echo "CEPCEnv installed successfully in \"$install_dir\""
}

main "$@"
