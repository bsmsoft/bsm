import os
import random
import string
import datetime

from cepcenv.util import expand_path
from cepcenv.util import ensure_list

from cepcenv.platform import Platform


class ConfigVersionError(Exception):
    pass


# This name is very long in order to avoid conflict with other modules
HANDLER_MODULE_NAME = '_cepcenv_handler_run_avoid_conflict'


_VERSION_ITEMS = ('version', 'software_root',
        'release_infodir', 'release_repo',
        'platform', 'os', 'arch', 'compiler')

_PATH_ITEMS = ('software_root', 'release_infodir')

_DEFAULT_ITEMS = {
        'software_root': os.getcwd(),
        'release_repo': 'https://github.com/cepc/cepc-release',
}


__TEMP_VERSION_PREFIX = ''
__TEMP_VERSION_LENGTH = 6

def _temp_version():
    return __TEMP_VERSION_PREFIX \
            + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f') + '_' \
            + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(__TEMP_VERSION_LENGTH))


class ConfigVersion(object):
    def __init__(self, config, version_name=None, version_config_cmd={}, extra_config=[]):
        self.__config = config
        self.__version_name = version_name
        self.__config_version_cmd = version_config_cmd

        self.__items = list(_VERSION_ITEMS) + ensure_list(extra_config)

        self.__load_config()


    def __process_platform(self):
        sp = Platform(self.__config_version.get('arch'), self.__config_version.get('os'), self.__config_version.get('compiler'))
        if 'arch' not in self.__config_version or not self.__config_version['arch']:
            self.__config_version['arch'] = sp.arch
        if 'os' not in self.__config_version or not self.__config_version['os']:
            self.__config_version['os'] = sp.os
        if 'compiler' not in self.__config_version or not self.__config_version['compiler']:
            self.__config_version['compiler'] = sp.compiler
        if 'platform' not in self.__config_version or not self.__config_version['platform']:
            self.__config_version['platform'] = sp.platform

    def __process_default(self):
        for k, v in _DEFAULT_ITEMS.items():
            if k not in self.__config_version or not self.__config_version[k]:
                self.__config_version[k] = v

    def __format_config(self):
        for k, v in self.__config_version.items():
            self.__config_version[k] = v.format(**self.__config_version)

    def __expand_path(self):
        for k in _PATH_ITEMS:
            if k in self.__config_version:
                self.__config_version[k] = expand_path(self.__config_version[k])

    def __process_config(self):
        if self.__version_name:
            self.__config_version['version_name'] = self.__version_name

        if 'version' not in self.__config_version:
            self.__config_version['version'] = _temp_version()

        self.__process_platform()
        self.__process_default()
        self.__format_config()
        self.__expand_path()

    def __filter_version_config(self, config):
        version_config = {}

        for k, v in config.items():
            if v is None:
                continue

            if k in self.__items:
                version_config[k] = v

        return version_config

    def __config_global(self):
        return self.__filter_version_config(self.__config)

    def __config_specific(self):
        config_temp = {}

        if 'versions' in self.__config and self.__version_name in self.__config['versions']:
            config_temp.update(self.__filter_version_config(self.__config['versions'][self.__version_name]))

        if 'version' not in config_temp:
            config_temp['version'] = self.__version_name

        return config_temp

    def __config_cmd(self):
        return self.__filter_version_config(self.__config_version_cmd)


    def __load_config(self):
        self.__config_version = self.__config_global()

        if self.__version_name:
            self.__config_version.update(self.__config_specific())

        self.__config_version.update(self.__config_cmd())

        self.__process_config()


    def get(self, key, default_value=None):
        return self.__config_version.get(key, default_value)

    @property
    def config(self):
        return self.__config_version

    @property
    def cepcenv_dir(self):
        if 'software_root' not in self.__config_version:
            raise ConfigVersionError('"software_root" not specified in configuration')
        return os.path.join(self.__config_version['software_root'], '.cepcenv')

    @property
    def main_dir(self):
        return os.path.join(self.cepcenv_dir, self.__config_version['version'])

    @property
    def def_dir(self):
        return os.path.join(self.main_dir, 'def')

    @property
    def handler_dir(self):
        return os.path.join(self.main_dir, 'handler')

    @property
    def handler_module_dir(self):
        return os.path.join(self.handler_dir, HANDLER_MODULE_NAME)

    @property
    def status_dir(self):
        return os.path.join(self.main_dir, 'status')

    @property
    def install_status_file(self):
        return os.path.join(self.status_dir, 'install.yml')
