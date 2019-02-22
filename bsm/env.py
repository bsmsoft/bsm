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


class EnvCtl(object):
    def __init__(self, initial_env):
        self.__initial_env = initial_env

        self.__init_env_name(env_prefix)

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


    def __init_env_name(self, env_prefix):
#        self.__env['bsmcli_bin']      = env_prefix + '_BSMCLI_BIN'
#        self.__env['app_id']          = env_prefix + '_APP_ID'
#        self.__env['software_root']   = env_prefix + '_SOFTWARE_ROOT'
#        self.__env['release_version'] = env_prefix + '_RELEASE_VERSION'
        self.__env['app_info']        = env_prefix + '_APP_INFO'
        self.__env['release_info']    = env_prefix + '_RELEASE_INFO'
        self.__env['packages_info']   = env_prefix + '_PACKAGES_INFO'

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


    def __generate_info_env(self, env_name, info):
        return {self.__env_prefix+'_'+env_name: json.dumps(info, separators=(',',':'))}


    def set_info(self, env_name, info):
        if info:
            self.

    def set_env(self):
        pass

    def unset_env(self):
        pass

    def add_path(self):
        pass

    def remove_path(self):
        pass

    def alias(self):
        pass

    def unalias(self):
        pass


class Env(object):
    def __init__(self, initial_env=None, env_prefix='BSM'):
        if initial_env is None:
            initial_env = os.environ
        self.__initial_env = initial_env.copy()

        self.__env_prefix = env_prefix

        self.__env = EnvCtl(self.__initial_env)

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

    def __init_info(self):
        self.__app_info = self.__init_info_env('APP_INFO')
        self.__release_info = self.__init_info_env('RELEASE_INFO')
        self.__packages_info = self.__init_info_env('PACKAGES_INFO')

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


    def __set_env_info(self, info_name, info):
        env_info_name = self.__env_prefix + '_' + info_name

        if not info:
            self.__env.unset_env(env_info_name)
            return

        env_info = {}
        env_info[env_info_name] = json.dumps(info, separators=(',',':'))
        self.__env.set_env(env_info_name, info))


    def set_app_info(self, app_id, config_env):
        self.__app_info['id'] = config_app['id']

        self.__app_info['set_env'] = config_app.get('set_env', [])
        self.__app_info['unset_env'] = config_app.get('unset_env', [])
        self.__app_info['prepend_path'] = config_app.get('prepend_path', [])
        self.__app_info['append_path'] = config_app.get('append_path', [])

        self.__app_info['alias'] = config_app.get('alias', [])
        self.__app_info['unalias'] = config_app.get('unalias', [])

    def set_release_info(self, software_root, version, config_env):
        self.__release_info = {}
        self.__release_info['software_root'] = software_root
        self.__release_info['version'] = version
        self.__release_info.update(config_env)

    def add_package_info(self, name, version='UNKNOWN', category=None, subdir='', config_env={}):
        self.__package_info[name] = {}
        self.__release_info[name]['version'] = version
        if category:
            self.__release_info[name]['category'] = category
        if subdir:
            self.__release_info[name]['subdir'] = subdir
        self.__release_info[name].update(config_env)

    def remove_package_info(self, name):
        if name in self.__package_info:
            del self.__package_info[name]


    def env_bsm(self):
        env_bsm = {}
        env_bsm.update(self.__env_release())
        env_bsm.update(self.__env_package_info())
        env_bsm.update(self.__env_path())
        env_bsm.update(self.__env_solo())
        return env_bsm

    def env_final(self):
        self.__env.set_env(self.env_bsm())

        self.__set_info_env('APP_INFO', self.__app_info))
        self.__set_info_env('RELEASE_INFO', self.__release_info))
        self.__set_info_env('PACKAGES_INFO', self.__packages_info))

        return self.__env.env()

    def env_final(self):
        self.__env.set_env(self.__generate_info_env('APP_INFO', self.__app_info))
        return self.__env.env()
