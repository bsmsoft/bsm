import os
import sys
import re

from bsm.loader import run_handler

from bsm.config import load_config
from bsm.config import ConfigError
from bsm.config.config_version import HANDLER_MODULE_NAME

from bsm.logger import get_logger
_logger = get_logger()

from bsm import BSM_VERSION


_AVAILABLE_RELEASE_CONFIG = ('version', 'setting')


class ConfigReleaseError(Exception):
    pass


def _compare_version(ver1, ver2):
    for i in range(3):
        if len(ver1) <= i:
            c1 = -1
        else:
            c1 = ver1[i]

        if len(ver2) <= i:
            c2 = -1
        else:
            c2 = ver2[i]

        if c1 != c2:
            return c1 - c2

    return 0


class ConfigRelease(object):
    def __init__(self, config_user, config_version, option):
        self.__config_user = config_user
        self.__config_version = config_version
        self.__option = option

        self.__load_config()

        self.__transform()

        self.__check_version()

        self.__check_bsm_version()

    def __load_config(self):
        self.__config = {}

        config_dir = os.path.join(self.__config_version.def_dir, 'config')
        if not os.path.exists(config_dir):
            raise ConfigReleaseError('Release definition directory "{0}" not found'.format(config_dir))

        for k in _AVAILABLE_RELEASE_CONFIG:
            config_file = os.path.join(config_dir, k+'.yml')
            try:
                self.__config[k] = load_config(config_file)
            except ConfigError as e:
                _logger.warn('Fail to load config file "{0}": {1}'.format(config_file, e))

        package_dir = os.path.join(config_dir, 'package')
        self.__load_package_config(package_dir)

    def __load_package_config(self, package_dir):
        self.__config['package'] = {}
        for root, dirs, files in os.walk(package_dir):
            for f in files:
                if not f.endswith('.yml') and not f.endswith('.yaml'):
                    continue
                pkg_name = os.path.splitext(f)[0]
                full_path = os.path.join(root, f)
                self.__config['package'][pkg_name] = load_config(full_path)

    def __transform(self):
        param = {}
        param['config_user'] = self.__config_user
        param['config_version'] = self.__config_version.config
        param['config_release'] = self.__config
        param['option'] = self.__option

        result = run_handler('transformer', param, self.__config_version.handler_dir)
        if isinstance(result, dict):
            self.__config = result

    def __check_bsm_version(self):
        m = re.match('(\d+)\.(\d+)\.(\d+)', BSM_VERSION)
        if not m:
            raise ConfigReleaseError('Can not verify bsm version: {0}'.format(BSM_VERSION))
        major, minor, patch = m.groups()
        bsm_ver_frag = [int(major), int(minor), int(patch)]

        version_require = self.__config.get('setting', {}).get('bsm', {}).get('require', {})
        _logger.debug('Version require: {0}'.format(version_require))
        for comp, ver in version_require.items():
            ver_frag = [int(i) for i in ver.split('.')]
            result = _compare_version(bsm_ver_frag, ver_frag)
            if comp == '<' and result >= 0 or \
                    comp == '<=' and result > 0 or \
                    comp == '=' and result != 0 or \
                    comp == '>=' and result < 0 or \
                    comp == '>' and result <= 0:
                raise ConfigReleaseError('BSM version does not follow: {0} {1} {2}'.format(BSM_VERSION, comp, ver))


    def __check_version(self):
        version = self.__config_version.get('version')
        version_in_release = self.__config.get('version')
        if version != version_in_release:
            _logger.warn('Version inconsistency found. Request {0} but receive {1}'.format(version, version_in_release))

    def get(self, key, default_value=None):
        return self.__config.get(key, default_value)

    @property
    def config(self):
        return self.__config
