import os

from bsm.util import is_str

from bsm.util.config import load_config, ConfigError

from bsm.logger import get_logger
_logger = get_logger()


class ConfigReleaseVersionError(Exception):
    pass


class ReleaseVersion(object):
    def __init__(self, config):
        config_dir = config['release_path']['config_dir']

        config_file = None
        for version_file in ['version.yml', 'version.yaml']:
            config_file = os.path.join(config_dir, version_file)
            if os.path.isfile(config_file):
                break
        if config_file is None:
            raise ConfigReleaseVersionError('Release version file not found')

        try:
            release_version = load_config(config_file)
        except ConfigError as e:
            raise ConfigReleaseVersionError('Release version file not valid: {0}'.format(e))
        if not is_str(release_version):
            raise ConfigReleaseVersionError(
                'Release version is not a string: {0}'.format(release_version))

        self.__data = release_version

        self.__check_version_consistency(config['scenario'])

    def __check_version_consistency(self, config_scenario):
        version = config_scenario.get('version')
        version_in_release = self.__data
        if version != version_in_release:
            _logger.warning(
                'Version inconsistency found. Request %s but receive %s',
                version, version_in_release)

    @property
    def data(self):
        return self.__data
