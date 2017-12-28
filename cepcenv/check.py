import os
import glob
import re
import subprocess

from cepcenv.env import Env

from cepcenv.util import ensure_list
from cepcenv.util import call
from cepcenv.util import which

from cepcenv.logger import get_logger
_logger = get_logger()


PACKAGE_MANAGER = {
        'yum': ['sudo', 'yum', 'install', '-y'],
        'apt-get': ['sudo', 'apt-get', 'install', '-y'],
        'pacman': ['sudo', 'pacman', '-S'],
        'zypper': ['sudo', 'zypper', '-n', 'install'],
}


def _detect_manager_type():
    for pkg_sys in PACKAGE_MANAGER:
        if which(pkg_sys):
            return pkg_sys
    return None

def _executable_dir(env):
    return [x for x in env.get('PATH', '').split(os.pathsep) if x]

def _include_dir(env):
    inc_dir = ['/usr/include', '/usr/local/include']
    return inc_dir

def _library_dir(env):
    lib_dir = [x for x in env.get('LD_LIBRARY_PATH', '').split(os.pathsep) if x]

    try:
        env_new = env.copy()
        env_new['PATH'] = env['PATH'] + os.pathsep + os.pathsep.join(['/sbin', '/usr/sbin', '/usr/local/sbin'])
        ret, out, err = call(['ldconfig', '-v', '-N'], stderr=subprocess.PIPE, env=env_new)
        for m in re.finditer('^(.*?):', out, flags=re.MULTILINE):
            lib_dir.append(m.group(1))
    except Exception as e:
        _logger.error('Command ldconfig error: {0}'.format(e))
        lib_dir += ['/lib', '/lib64', '/usr/lib', '/usr/lib64']
    return lib_dir


class Check(object):
    def __init__(self, config_release, pkg_type):
        self.__config_release = config_release
        self.__pkg_type = pkg_type
        self.__mgr_type = _detect_manager_type()
        self.__load_check_dir()

    def __check_single_file(self, check_dirs, check_file):
        for d in check_dirs:
            dst_file = os.path.join(d, check_file)
            # Use glob in order to accept wildcards
            if glob.glob(dst_file):
                _logger.debug('Package found by: {0}'.format(dst_file))
                return True
        return False

    # Match any file in the file_list
    def __check_optional_files(self, check_dirs, file_list):
        for f in file_list:
            if self.__check_single_file(check_dirs, f):
                return True
        return False

    # Match every file_list in the check_list
    def __check_single_type(self, check_type, check_list):
        if check_type not in self.__check_dir:
            _logger.warn('Unknown check type: {0}'.format(check_type))
            return False

        for l in check_list:
            if not self.__check_optional_files(self.__check_dir[check_type], l):
                return False

        return True

    def __check_package(self, check_cfg):
        for check_type, check_list in check_cfg.items():
            if not self.__check_single_type(check_type, check_list):
                return False
        return True

    def check(self):
        missing_pkg = []
        pkg_install_name = []

        for pkg, check_cfg in self.__config_release.get('check', {}).items():
            _logger.debug('Searching package: {0}'.format(pkg))
            if not self.__check_package(check_cfg.get(self.__pkg_type, {}).get('check', {})):
                _logger.debug('Package not available: {0}'.format(pkg))
                missing_pkg.append(pkg)
                install_name = check_cfg.get(self.__pkg_type, {}).get('package_manager', {}).get(self.__mgr_type, [])
                pkg_install_name += ensure_list(install_name)

        return missing_pkg, pkg_install_name

    def __load_check_dir(self):
        env = Env()
        env.clean()
        env_final = env.env_final()

        self.__check_dir = {}
        self.__check_dir['include'] = _include_dir(env_final)
        self.__check_dir['library'] = _library_dir(env_final)
        self.__check_dir['executable'] = _executable_dir(env_final)

        _logger.debug('Package checking directories: {0}'.format(self.__check_dir))

    @property
    def install_cmd(self):
        return PACKAGE_MANAGER.get(self.__mgr_type, [])
