import os

from bsm.util.config import load_config, ConfigError

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()

_AVAILABLE_RELEASE_CONFIG = ('version', 'setting')


class ConfigReleaseOriginError(Exception):
    pass


class ReleaseOrigin(CommonDict):
    def __init__(self, **config):
        super(ReleaseOrigin, self).__init__()

        if not ('version' in config['scenario'] and config['scenario']['version']):
            raise ConfigReleaseOriginError('"version" not specified in config')

        self.__load_config(config['scenario'], config['release_path'])

    def __load_config(self, config_scenario, config_release_path):
        config_dir = config_release_path['config_dir']
        if not os.path.isdir(config_dir):
            raise ConfigReleaseOriginError('Release version "{0}" not found'.format(config_scenario['version']))

        for k in _AVAILABLE_RELEASE_CONFIG:
            config_file = os.path.join(config_dir, k+'.yaml')
            if not os.path.isfile(config_file):
                config_file = os.path.join(config_dir, k+'.yml')

            try:
                self[k] = load_config(config_file)
            except ConfigError as e:
                _logger.warning('Fail to load config file "{0}": {1}'.format(config_file, e))
