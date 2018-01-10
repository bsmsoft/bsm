import os
import copy

from cepcenv.logger import get_logger
_logger = get_logger()


SOFTWARE_ROOT_ENV_NAME = 'CEPCENV_SOFTWARE_ROOT'
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
        if len(pkg_fraction) != 4:
            continue

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
    def remove_package(self, path_usage, pkg_info):
        pass

    def set_package(self, path_usage, pkg_info):
        pkg_name = pkg_info['name']
        pkg_dir = pkg_info.get('dir', {})
        package = pkg_info.get('package', {})
        attribute = pkg_info.get('attribute', {})

        self.__set_package_info(pkg_name, package)
        self.__set_package_path(path_usage, pkg_name, attribute, pkg_dir)
        self.__set_package_env(path_usage, pkg_name, attribute, pkg_dir)

    def __set_package_info(self, pkg_name, package):
        if pkg_name not in self.__pkg_info:
            self.__pkg_info[pkg_name] = {}
        self.__pkg_info[pkg_name]['category'] = package.get('category', 'unknown')
        self.__pkg_info[pkg_name]['path'] = package.get('path', '')
        self.__pkg_info[pkg_name]['version'] = package.get('version', 'empty')

    def __set_package_path(self, path_usage, pkg_name, attribute, pkg_dir):
        all_path = attribute.get('path', {})
        for k, v in all_path.items():
            multi_env_path_name = path_usage.get('multi_env', {})
            if k in multi_env_path_name:
                path_name = multi_env_path_name[k]
                if path_name not in self.__path:
                    self.__path[path_name] = []
                self.__path[path_name].insert(0, v.format(**pkg_dir))

    def __set_package_env(self, path_usage, pkg_name, attribute, pkg_dir):
        all_path = attribute.get('path', {})
        for k, v in all_path.items():
            single_env_path_name = path_usage.get('single_env', {})
            if k in single_env_path_name:
                env_name = single_env_path_name[k].format(package=pkg_name)
                self.__solo[env_name] = v.format(**pkg_dir)

        all_solo = attribute.get('env', {})
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

    def __env_all(self):
        env_all = {}
        env_all.update(self.__env_release())
        env_all.update(self.__env_package_info())
        env_all.update(self.__env_path())
        env_all.update(self.__env_solo())
        return env_all


    def env_final(self):
        env_to_update = self.__env_all()

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
        env_to_update = self.__env_all()

        set_env = {}
        unset_env = []
        for k, v in env_to_update.items():
            if v is not None:
                if k not in env_origin or v != env_origin[k]:
                    set_env[k] = v
            else:
                if k in env_origin:
                    unset_env.append(k)
        return set_env, unset_env
