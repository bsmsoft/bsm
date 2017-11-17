import os
import copy

from cepcenv.logger import get_logger
_logger = get_logger()


RELEASE_ROOT_ENV_NAME = 'CEPCENV_RELEASE_ROOT'
RELEASE_VERSION_ENV_NAME = 'CEPCENV_RELEASE_VERSION'
PACKAGE_INFO_ENV_NAME = 'CEPCENV_PACKAGE_INFO'
ENV_LIST_ENV_NAME = 'CEPCENV_ENV_LIST'
PATH_LIST_ENV_NAME = 'CEPCENV_PATH_LIST'

PATH_ENV_PREFIX = 'CEPCENV_PATH_ENV_'


def _parse_path(path_str):
    return path_str.split(os.pathsep)

def _emit_path(path_list):
    return os.pathsep.join(path_list)

def _parse_package_info(pkg_info_str):
    pkg_info = {}
    for pkg_info_line in pkg_info_str.split(':'):
        pkg_fraction = pkg_info_line.split('@')
        pkg_name = pkg_fraction[0]
        pkg_info[pkg_name] = {
            'category': pkg_fraction[1],
            'path': pkg_fraction[2],
            'version': pkg_fraction[3],
        }
    return pkg_info

def _emit_package_info(pkg_info):
    pkg_info_list = []
    for pkg_name, info in pkg_info.items():
        info_str = pkg_name + '@' + info['category'] + '@' + info['path'] + '@' + info['version']
        pkg_info_list.append(info_str)
    return ':'.join(pkg_info_list)


class Env(object):
    def __init__(self, initial_env=None):
        if initial_env is None:
            initial_env = os.environ
        self.__initial_env = initial_env.copy()

        self.__init_release()
        self.__init_package_info()
        self.__init_package_path()
        self.__init_os_path()
        self.__init_package_env()

        self.__release_root = self.__initial_release_root
        self.__release_version = self.__initial_release_version
        self.__pkg_info = copy.deepcopy(self.__initial_pkg_info)
        self.__pkg_path = copy.deepcopy(self.__initial_pkg_path)
        self.__pkg_env = copy.deepcopy(self.__initial_pkg_env)


    def __init_release(self):
        self.__initial_release_root = None
        if RELEASE_ROOT_ENV_NAME in self.__initial_env:
            self.__initial_release_root = self.__initial_env[RELEASE_ROOT_ENV_NAME]
        self.__initial_release_version = None
        if RELEASE_VERSION_ENV_NAME in self.__initial_env:
            self.__initial_release_version = self.__initial_env[RELEASE_VERSION_ENV_NAME]

    def __init_package_info(self):
        self.__initial_pkg_info = {}
        if PACKAGE_INFO_ENV_NAME in self.__initial_env:
            self.__initial_pkg_info = _parse_package_info(self.__initial_env[PACKAGE_INFO_ENV_NAME])

    def __init_package_path(self):
        self.__initial_pkg_path = {}
        if PATH_LIST_ENV_NAME in self.__initial_env:
            for path_name in self.__initial_env[PATH_LIST_ENV_NAME].split():
                path_str = self.__initial_env.get(PATH_ENV_PREFIX+path_name, '')
                self.__initial_pkg_path[path_name] = _parse_path(path_str)

    def __init_os_path(self):
        self.__initial_os_path = {}
        for k, v in self.__initial_pkg_path.items():
            if k not in self.__initial_env:
                continue

            os_path = _parse_path(self.__initial_env[k])
            for p in v:
                if p in os_path:
                    os_path.remove(p)

            self.__initial_os_path[k] = os_path

    def __init_package_env(self):
        self.__initial_pkg_env = {}
        if ENV_LIST_ENV_NAME in self.__initial_env:
            for env_name in self.__initial_env[ENV_LIST_ENV_NAME].split():
                self.__initial_pkg_env[env_name] = self.__initial_env.get(env_name, '')


    @property
    def release_root(self):
        return self.__release_root

    @property
    def release_version(self):
        return self.__release_version

    @property
    def package_info(self):
        return self.__pkg_info


    def clean(self):
        self.__release_root = None
        self.__release_version = None
        self.__pkg_info = {}
        self.__pkg_path = {}
        self.__pkg_env = {}

    def set_release(self, rel_root, rel_ver):
        self.__release_root = rel_root
        self.__release_version = rel_ver

    # TODO: global envs are from main.yml
    def set_global_env(self, env):
        for k, v in env.items():
            self.__pkg_env[k] = v.format(**pkg_format)

    # TODO: delete old_pkg env
    def remove_package(self, path_mode, pkg_config):
        pass

    def set_package(self, path_mode, pkg_config):
        pkg_name = pkg_config['name']
        pkg_format = pkg_config.get('format', {})
        package = pkg_config.get('package', {})
        attribute = pkg_config.get('attribute', {})

        self.__set_package_info(pkg_name, package)
        self.__set_package_path(path_mode, pkg_name, attribute, pkg_format)
        self.__set_package_env(path_mode, pkg_name, attribute, pkg_format)

    def __set_package_info(self, pkg_name, package):
        if pkg_name not in self.__pkg_info:
            self.__pkg_info[pkg_name] = {}
        self.__pkg_info[pkg_name]['category'] = package.get('category', 'unknown')
        self.__pkg_info[pkg_name]['path'] = package.get('path', '')
        self.__pkg_info[pkg_name]['version'] = package.get('version', 'empty')

    def __set_package_path(self, path_mode, pkg_name, attribute, pkg_format):
        all_path = attribute.get('path', {})
        for k, v in all_path.items():
            multiple_path_name = path_mode.get('multiple', {})
            if k in multiple_path_name:
                path_name = multiple_path_name[k]
                if path_name not in self.__pkg_path:
                    self.__pkg_path[path_name] = []
                self.__pkg_path[path_name].insert(0, v.format(**pkg_format))

    def __set_package_env(self, path_mode, pkg_name, attribute, pkg_format):
        all_path = attribute.get('path', {})
        for k, v in all_path.items():
            single_path_name = path_mode.get('single', {})
            if k in single_path_name:
                env_name = single_path_name[k].format(package=pkg_name)
                self.__pkg_env[env_name] = v.format(**pkg_format)

        all_env = attribute.get('env', {})
        for k, v in all_env.items():
            self.__pkg_env[k] = v.format(**pkg_format)


    def release_env(self):
        setenv = {}
        unset = []

        if self.__release_root != self.__initial_release_root:
            if self.__release_root is None:
                unset.append(RELEASE_ROOT_ENV_NAME)
            else:
                setenv[RELEASE_ROOT_ENV_NAME] = self.__release_root

        if self.__release_version != self.__initial_release_version:
            if self.__release_version is None:
                unset.append(RELEASE_VERSION_ENV_NAME)
            else:
                setenv[RELEASE_VERSION_ENV_NAME] = self.__release_version

        _logger.debug('setenv release version: {0}'.format(setenv))
        _logger.debug('unset release version: {0}'.format(unset))
        return setenv, unset

    def final_info_env(self):
        setenv = {}
        unset = []
        if self.__pkg_info:
            setenv[PACKAGE_INFO_ENV_NAME] = _emit_package_info(self.__pkg_info)
        else:
            if self.__initial_pkg_info:
                unset.append(PACKAGE_INFO_ENV_NAME)
        _logger.debug('setenv package info: {0}'.format(setenv))
        _logger.debug('unset package info: {0}'.format(unset))
        return setenv, unset

    def final_path_env(self):
        setenv = {}
        unset = []

        _logger.debug('find path env self.__initial_os_path: {0}'.format(self.__initial_os_path))
        _logger.debug('find path env self.__initial_pkg_path: {0}'.format(self.__initial_pkg_path))

        for k in self.__initial_pkg_path:
            if k not in self.__pkg_path:
                if k in self.__initial_os_path and self.__initial_os_path[k]:
                    setenv[k] = _emit_path(self.__initial_os_path[k])
                else:
                    unset.append(k)
                unset.append(PATH_ENV_PREFIX+k)

        path_list = []
        for k, v in self.__pkg_path.items():
            path_list.append(k)
            if k in self.__initial_os_path:
                path_full = v + self.__initial_os_path[k]
            elif k in self.__initial_env:
                path_full = v + _parse_path(self.__initial_env[k])
            else:
                path_full = v
            setenv[k] = _emit_path(path_full)
            setenv[PATH_ENV_PREFIX+k] = _emit_path(v)

        if path_list:
            setenv[PATH_LIST_ENV_NAME] = ' '.join(path_list)
        else:
            if self.__initial_pkg_path:
                unset.append(PATH_LIST_ENV_NAME)

        _logger.debug('setenv env path: {0}'.format(setenv))
        _logger.debug('unset env path: {0}'.format(unset))
        return setenv, unset

    def final_package_env(self):
        setenv = {}
        unset = []

        for k in self.__initial_pkg_env:
            if k not in self.__pkg_env:
                unset.append(k)

        env_list = []
        for k, v in self.__pkg_env.items():
            env_list.append(k)
            setenv[k] = v

        if env_list:
            setenv[ENV_LIST_ENV_NAME] = ' '.join(env_list)
        else:
            if self.__initial_pkg_env:
                unset.append(ENV_LIST_ENV_NAME)

        _logger.debug('setenv env: {0}'.format(setenv))
        _logger.debug('unset env: {0}'.format(unset))
        return setenv, unset

    def final_all_env(self):
        all_setenv = {}
        all_unset = []

        setenv, unset = self.release_env()
        all_setenv.update(setenv)
        all_unset = unset + all_unset

        setenv, unset = self.final_info_env()
        all_setenv.update(setenv)
        all_unset = unset + all_unset

        setenv, unset = self.final_path_env()
        all_setenv.update(setenv)
        all_unset = unset + all_unset

        setenv, unset = self.final_package_env()
        all_setenv.update(setenv)
        all_unset = unset + all_unset

        return all_setenv, all_unset
