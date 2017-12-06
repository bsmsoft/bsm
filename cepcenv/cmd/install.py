from cepcenv.config.config_release import ConfigReleaseTransformError
from cepcenv.install import Install as CepcenvInstall

from cepcenv.logger import get_logger
_logger = get_logger()

class Install(object):
    def execute(self, config, config_version, source, force):
        transformer = []
        if source:
            transformer = [source + '_source']

        obj = CepcenvInstall(config, config_version, transformer)
        try:
            obj.run(force)
        except ConfigReleaseTransformError as e:
            _logger.critical('Install source error: {0}'.format(source))

        _logger.info('Installed successfully for version: {0}'.format(config_version.get('version')))
        _logger.info('Software root: {0}'.format(config_version.get('software_root')))
