import os
import copy

from bsm.logger import get_logger
_logger = get_logger()


BSMCLI_BIN_NAME = 'BSM_BSMCLI_BIN'
#APP_ENV_NAME = 'BSM_APP'
SOFTWARE_ROOT_ENV_NAME = 'BSM_SOFTWARE_ROOT'
RELEASE_VERSION_ENV_NAME = 'BSM_RELEASE_VERSION'
PACKAGE_INFO_ENV_NAME = 'BSM_PACKAGE_INFO'
ENV_LIST_ENV_NAME = 'BSM_ENV_LIST'
PATH_LIST_ENV_NAME = 'BSM_PATH_LIST'

PATH_ENV_PREFIX = 'BSM_PATH_ENV_'


def _parse_path(path_str):
    return path_str.split(os.pathsep)

def _emit_path(path_list):
    return os.pathsep.join(path_list)

def _parse_package_info(pkg_info_str):
    pkg_info = {}
    for pkg_info_line in pkg_info_str.split(':'):
        pkg_fraction = pkg_info_line.split('@')
        if len(pkg_fraction) != 4:
            continue

        pkg_name = pkg_fraction[0]
        pkg_info[pkg_name] = {
            'category': pkg_fraction[1],
            'subdir': pkg_fraction[2],
            'version': pkg_fraction[3],
        }
    return pkg_info

def _emit_package_info(pkg_info):
    pkg_info_list = []
    for pkg_name, info in pkg_info.items():
        info_str = pkg_name + '@' + info['category'] + '@' + info['subdir'] + '@' + info['version']
        pkg_info_list.append(info_str)
    return ':'.join(pkg_info_list)


class Env(object):
    def __init__(self, initial_env=None):
        if initial_env is None:
            initial_env = os.environ
        self.__initial_env = initial_env.copy()

        self.__init_release()
        self.__init_package_info()
        self.__init_path()
        self.__init_os_path()
        self.__init_solo()

        self.__software_root = self.__initial_software_root
        self.__release_version = self.__initial_release_version
        self.__pkg_info = copy.deepcopy(self.__initial_pkg_info)
        self.__path = copy.deepcopy(self.__initial_path)
        self.__solo = copy.deepcopy(self.__initial_solo)


    def __init_release(self):
        self.__initial_software_root = None
        if SOFTWARE_ROOT_ENV_NAME in self.__initial_env:
            self.__initial_software_root = self.__initial_env[SOFTWARE_ROOT_ENV_NAME]
        self.__initial_release_version = None
        if RELEASE_VERSION_ENV_NAME in self.__initial_env:
            self.__initial_release_version = self.__initial_env[RELEASE_VERSION_ENV_NAME]

    def __init_package_info(self):
        self.__initial_pkg_info = {}
        if PACKAGE_INFO_ENV_NAME in self.__initial_env:
            self.__initial_pkg_info = _parse_package_info(self.__initial_env[PACKAGE_INFO_ENV_NAME])

    def __init_path(self):
        self.__initial_path = {}
        if PATH_LIST_ENV_NAME in self.__initial_env:
            for path_name in self.__initial_env[PATH_LIST_ENV_NAME].split():
                path_str = self.__initial_env.get(PATH_ENV_PREFIX+path_name, '')
                self.__initial_path[path_name] = _parse_path(path_str)

    def __init_os_path(self):
        self.__initial_os_path = {}
        for k, v in self.__initial_path.items():
            if k not in self.__initial_env:
                continue

            os_path = _parse_path(self.__initial_env[k])
            for p in v:
                if p in os_path:
                    os_path.remove(p)

            self.__initial_os_path[k] = os_path

    def __init_solo(self):
        self.__initial_solo = {}
        if ENV_LIST_ENV_NAME in self.__initial_env:
            for env_name in self.__initial_env[ENV_LIST_ENV_NAME].split():
                self.__initial_solo[env_name] = self.__initial_env.get(env_name, '')


    @property
    def software_root(self):
        return self.__software_root

    @property
    def release_version(self):
        return self.__release_version

    @property
    def package_info(self):
        return self.__pkg_info


    def clean(self):
        self.__software_root = None
        self.__release_version = None
        self.__pkg_info = {}

        # Do not use "self.__path = {}, self.__solo = {}" here
        # We need to know which paths and envs ever exist
        for k in self.__path:
            self.__path[k] = []
        for k in self.__solo:
            self.__solo[k] = None

    def set_release(self, rel_root, rel_ver):
        self.__software_root = rel_root
        self.__release_version = rel_ver

    def set_global(self, env):
        self.__solo.update(env)

    # TODO: delete old_pkg env
    def remove_package(self, path_def, pkg_info):
        pass

    def set_package(self, path_def, pkg_info):
        pkg_name = pkg_info['name']
        pkg_config = pkg_info.get('config', {})
        pkg_dir = pkg_info.get('dir', {})

        self.__set_package_info(pkg_name, pkg_config)
        self.__set_package_path(path_def, pkg_name, pkg_config, pkg_dir)
        self.__set_package_env(path_def, pkg_name, pkg_config, pkg_dir)

    def __set_package_info(self, pkg_name, pkg_config):
        if pkg_name not in self.__pkg_info:
            self.__pkg_info[pkg_name] = {}
        self.__pkg_info[pkg_name]['category'] = pkg_config.get('category', 'unknown')
        self.__pkg_info[pkg_name]['subdir'] = pkg_config.get('subdir', '')
        self.__pkg_info[pkg_name]['version'] = pkg_config.get('version', 'empty')

    def __set_package_path(self, path_def, pkg_name, pkg_config, pkg_dir):
        all_path = pkg_config.get('path', {})
        for k, v in all_path.items():
            path_env_path_name = path_def.get('path_env', {})
            if k in path_env_path_name:
                path_name = path_env_path_name[k]
                if path_name not in self.__path:
                    self.__path[path_name] = []
                self.__path[path_name].insert(0, v.format(**pkg_dir))

    def __set_package_env(self, path_def, pkg_name, pkg_config, pkg_dir):
#        all_path = pkg_config.get('path', {})
#        for k, v in all_path.items():
#            solo_env_path_name = path_def.get('solo_env', {})
#            if k in solo_env_path_name:
#                env_name = solo_env_path_name[k].format(package=pkg_name)
#                self.__solo[env_name] = v.format(**pkg_dir)

        all_solo = pkg_config.get('env', {})
        for k, v in all_solo.items():
            self.__solo[k] = v.format(**pkg_dir)


    def __env_release(self):
        env = {}
        env[SOFTWARE_ROOT_ENV_NAME] = self.__software_root
        env[RELEASE_VERSION_ENV_NAME] = self.__release_version
        return env

    def __env_package_info(self):
        env = {}
        if self.__pkg_info:
            env[PACKAGE_INFO_ENV_NAME] = _emit_package_info(self.__pkg_info)
        else:
            env[PACKAGE_INFO_ENV_NAME] = None
        return env

    def __env_path(self):
        env = {}

        for k in self.__initial_path:
            if k not in self.__path:
                if k in self.__initial_os_path and self.__initial_os_path[k]:
                    env[k] = _emit_path(self.__initial_os_path[k])
                else:
                    env[k] = None
                env[PATH_ENV_PREFIX+k] = None

        path_list = []
        for k, v in self.__path.items():
            if k in self.__initial_os_path:
                path_full = v + self.__initial_os_path[k]
            elif k in self.__initial_env:
                path_full = v + _parse_path(self.__initial_env[k])
            else:
                path_full = v

            if v:
                path_list.append(k)
                env[PATH_ENV_PREFIX+k] = _emit_path(v)
            else:
                env[PATH_ENV_PREFIX+k] = None

            if path_full:
                env[k] = _emit_path(path_full)
            else:
                env[k] = None

        if path_list:
            env[PATH_LIST_ENV_NAME] = ' '.join(path_list)
        else:
            env[PATH_LIST_ENV_NAME] = None

        return env

    def __env_solo(self):
        env = {}

        env_list = []
        for k, v in self.__solo.items():
            if v is not None:
                env_list.append(k)
            env[k] = v

        if env_list:
            env[ENV_LIST_ENV_NAME] = ' '.join(env_list)
        else:
            env[ENV_LIST_ENV_NAME] = None

        return env

    def env_bsm(self):
        env_bsm = {}
        env_bsm.update(self.__env_release())
        env_bsm.update(self.__env_package_info())
        env_bsm.update(self.__env_path())
        env_bsm.update(self.__env_solo())
        return env_bsm

    def env_final(self):
        env_to_update = self.env_bsm()

        final = self.__initial_env.copy()
        for k, v in env_to_update.items():
            if v is not None:
                final[k] = v
            else:
                if k in final:
                    del final[k]
        return final

    def env_change(self):
        env_origin = self.__initial_env
        env_to_update = self.env_bsm()
        _logger.debug('Original env: {0}'.format(env_origin))
        _logger.debug('Updated env: {0}'.format(env_to_update))

        set_env = {}
        unset_env = []
        for k, v in env_to_update.items():
            if v is not None:
                if k not in env_origin or v != env_origin[k]:
                    set_env[k] = v
            else:
                if k in env_origin:
                    unset_env.append(k)

        _logger.debug('Changed set_env: {0}'.format(set_env))
        _logger.debug('Changed unset_env: {0}'.format(unset_env))

        return set_env, unset_env
