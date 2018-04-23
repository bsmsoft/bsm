import os
import random
import string
import datetime

from bsm.util import expand_path
from bsm.util import ensure_list


class ConfigVersionError(Exception):
    pass


# This name is very long in order to avoid conflict with other modules
HANDLER_MODULE_NAME = '_bsm_handler_run_avoid_conflict'


_VERSION_ITEMS = ('version', 'software_root',
        'release_infodir', 'release_repo')

_PATH_ITEMS = ('software_root', 'release_infodir')

_DEFAULT_ITEMS = {
        'software_root': os.getcwd(),
        'release_repo': os.environ.get('BSM_RELEASE_REPO', ''),
}


__TEMP_VERSION_PREFIX = ''
__TEMP_VERSION_LENGTH = 6

def _temp_version():
    return __TEMP_VERSION_PREFIX \
            + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f') + '_' \
            + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(__TEMP_VERSION_LENGTH))


class ConfigVersion(object):
    def __init__(self, config_user, version_name=None, version_cmd={}, extra_config=[]):
        self.__config_user = config_user
        self.__version_name = version_name
        self.__version_cmd = version_cmd

        self.__items = list(_VERSION_ITEMS) + ensure_list(extra_config)

        self.__load_config()


    def __process_default(self):
        for k, v in _DEFAULT_ITEMS.items():
            if k not in self.__config or not self.__config[k]:
                self.__config[k] = v

    def __format_config(self):
        for k, v in self.__config.items():
            self.__config[k] = v.format(**self.__config)

    def __expand_path(self):
        for k in _PATH_ITEMS:
            if k in self.__config:
                self.__config[k] = expand_path(self.__config[k])

    def __process_config(self):
        if self.__version_name:
            self.__config['version_name'] = self.__version_name

        if 'version' not in self.__config:
            self.__config['version'] = _temp_version()

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
        return self.__filter_version_config(self.__config_user)

    def __config_specific(self):
        config_temp = {}

        if 'versions' in self.__config_user and self.__version_name in self.__config_user['versions']:
            config_temp.update(self.__filter_version_config(self.__config_user['versions'][self.__version_name]))

        if 'version' not in config_temp:
            config_temp['version'] = self.__version_name

        return config_temp

    def __config_cmd(self):
        return self.__filter_version_config(self.__version_cmd)


    def __load_config(self):
        self.__config = self.__config_global()

        if self.__version_name:
            self.__config.update(self.__config_specific())

        self.__config.update(self.__config_cmd())

        self.__process_config()


    def get(self, key, default_value=None):
        return self.__config.get(key, default_value)

    @property
    def config(self):
        return self.__config

    @property
    def bsm_dir(self):
        if 'software_root' not in self.__config:
            raise ConfigVersionError('"software_root" not specified in configuration')
        return os.path.join(self.__config['software_root'], '.bsm')

    @property
    def main_dir(self):
        return os.path.join(self.bsm_dir, self.__config['version'])

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