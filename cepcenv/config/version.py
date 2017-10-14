import random
import string
import datetime

from cepcenv.util import expand_path

from cepcenv.sw import Platform


__VERSION_ITEMS = ('version', 'release_root', 'release_status_root', 'work_root',
        'version_dir', 'version_repo',
        'platform', 'os', 'arch', 'compiler')

__PATH_ITEMS = ('release_root', 'release_status_root', 'work_root', 'version_dir')

__DEFAULT_ITEMS = {
        'version_repo': 'https://github.com/cepc/cepcsoft',
        'release_status_root': '{release_root}/_cepcenv/{version}',
}


__TEMP_VERSION_PREFIX = ''
__TEMP_VERSION_LENGTH = 6

def __temp_version():
    return __TEMP_VERSION_PREFIX \
            + datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f') + '_' \
            + ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(__TEMP_VERSION_LENGTH))


def __filter_version_config(config):
    version_config = {}

    for k, v in config.items():
        if v is None:
            continue

        if k in __VERSION_ITEMS:
            version_config[k] = v

    return version_config


class Version(object):
    def __init__(self, config, version_name=None, version_config_cmd={}):
        self.__config = config
        self.__version_name = version_name
        self.__version_config_cmd = version_config_cmd

        self.__load_config()


    def __process_platform(self):
        sp = Platform(self.__version_config.get('arch'), self.__version_config.get('os'), self.__version_config.get('compiler'))
        if 'arch' not in self.__version_config or not self.__version_config['arch']:
            self.__version_config['arch'] = sp.arch
        if 'os' not in self.__version_config or not self.__version_config['os']:
            self.__version_config['os'] = sp.os
        if 'compiler' not in self.__version_config or not self.__version_config['compiler']:
            self.__version_config['compiler'] = sp.compiler
        if 'platform' not in self.__version_config or not self.__version_config['platform']:
            self.__version_config['platform'] = sp.platform

    def __process_default(self):
        for k, v in __DEFAULT_ITEMS.items():
            if k not in self.__version_config or not self.__version_config[k]:
                self.__version_config[k] = v

    def __format_config(self):
        for k, v in self.__version_config.items():
            self.__version_config[k] = v.format(**self.__version_config)

    def __expand_path(self):
        for k in __PATH_ITEMS:
            self.__version_config[k] = expand_path(self.__version_config[k])

    def __process_config(self):
        self.__process_platform()
        self.__process_default()
        self.__format_config()
        self.__expand_path()

        if 'version' not in self.__version_config:
            self.__version_config['version'] = __temp_version()


    def __config_global(self):
        return __filter_version_config(self.__config)

    def __config_specific(self):
        config_temp = {}

        if 'versions' in self.__config and self.__version_name in self.__config['versions']:
            config_temp.update(__filter_version_config(self.__config['versions'][self.__version_name]))

        if 'version' not in config_temp:
            config_temp['version'] = self.__version_name

        return config_temp

    def __config_cmd(self):
        return __filter_version_config(self.__version_config_cmd)


    def __load_config(self):
        self.__version_config = self.__config_global()

        if self.__version_name is not None:
            self.__version_config.update(self.__config_specific())

        self.__version_config.update(self.__config_cmd())

        self.__process_config()

    @property
    def config(self):
        return self.__version_config
