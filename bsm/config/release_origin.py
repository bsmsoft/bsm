import os

from bsm.util import walk_rel_dir
from bsm.util.config import load_config, ConfigError

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()

_AVAILABLE_RELEASE_CONFIG = ('version', 'setting')


class ConfigReleaseOriginError(Exception):
    pass


class ReleaseOrigin(CommonDict):
    def __init__(self, config_app, config_output, config_scenario, config_release_path):
        super(ReleaseOrigin, self).__init__()

        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config release origin')
            return

        self.__load_config(config_scenario, config_release_path)

    def __load_config(self, config_scenario, config_release_path):
        config_dir = os.path.join(config_release_path['config_dir'])
        if not os.path.isdir(config_dir):
            raise ConfigReleaseOriginError('Release version "{0}" not found'.format(config_scenario['version']))

        for k in _AVAILABLE_RELEASE_CONFIG:
            config_file = os.path.join(config_dir, k+'.yaml')
            if not os.path.isfile(config_file):
                config_file = os.path.join(config_dir, k+'.yml')

            try:
                self[k] = load_config(config_file)
            except ConfigError as e:
                _logger.warn('Fail to load config file "{0}": {1}'.format(config_file, e))

        package_dir = os.path.join(config_dir, 'package')
        self.__load_package_config(package_dir)

    def __load_package_config(self, package_dir):
        self['package'] = {}
        for full_path, rel_dir, f in walk_rel_dir(package_dir):
            if not f.endswith('.yml') and not f.endswith('.yaml'):
                continue
            pkg_name = os.path.splitext(f)[0]
            try:
                self['package'][os.path.join(rel_dir, pkg_name)] = load_config(full_path)
            except ConfigError as e:
                _logger.warn('Fail to load package config file "{0}": {1}'.format(full_path, e))
