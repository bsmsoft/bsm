import os
import sys

from cepcenv.loader import load_func
from cepcenv.loader import LoadError

from cepcenv.config import load_config
from cepcenv.config import ConfigError
from cepcenv.config.config_version import HANDLER_MODULE_NAME

from cepcenv.logger import get_logger
_logger = get_logger()

_AVAILABLE_RELEASE_CONFIG = ('version', 'setting', 'package', 'attribute', 'install', 'check')


class ConfigReleaseError(Exception):
    pass

class ConfigReleaseTransformError(ConfigReleaseError):
    pass


class ConfigRelease(object):
    def __init__(self, config_version):
        self.__config_version = config_version

        self.__load_config()

        self.__pre_transform()

        self.__check_version()

    def __load_config(self):
        self.__config_release = {}

        config_dir = os.path.join(self.__config_version.def_dir, 'config')
        if not os.path.exists(config_dir):
            raise ConfigReleaseError('Release definition directory "{0}" not found'.format(config_dir))

        for k in _AVAILABLE_RELEASE_CONFIG:
            config_file = os.path.join(config_dir, k+'.yml')
            try:
                self.__config_release[k] = load_config(config_file)
            except ConfigError as e:
                raise ConfigReleaseError('Fail to load config file "{0}": {1}'.format(config_file, e))

    def __pre_transform(self):
        for transformer in self.__config_release.get('setting', {}).get('pre_transform', []):
            self.transform(transformer)

    def __check_version(self):
        version = self.__config_version.get('version')
        version_in_release = self.__config_release.get('version')
        if version != version_in_release:
            _logger.warn('Version inconsistency found. Request {0} but receive {1}'.format(version, version_in_release))

    def transform(self, transformer):
        param = {}
        param['config_release'] = self.__config_release

        sys.path.insert(0, self.__config_version.handler_dir)

        module_name = HANDLER_MODULE_NAME + '.transform.' + transformer
        try:
            f = load_func(module_name, 'run')
            result = f(param)
            if result:
                self.__config_release = result
        except LoadError as e:
            _logger.error('Load transformer "{0}" error: {1}'.format(transformer, e))
            raise ConfigReleaseTransformError('Load transformer "{0}" error'.format(transformer))
        except Exception as e:
            _logger.error('Transformer "{0}" error: {1}'.format(transformer, e))
            raise

        sys.path.remove(self.__config_version.handler_dir)

    def get(self, key, default_value=None):
        return self.__config_release.get(key, default_value)

    @property
    def config(self):
        return self.__config_release
