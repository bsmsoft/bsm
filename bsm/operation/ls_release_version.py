import os

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsReleaseVersion(Base):
    def execute(self):
        local_versions = []

        release_dir = self._config['release_path']['release_dir']
        _logger.debug('Search local versions under release directory: {0}'.format(release_dir))

        if not os.path.isdir(release_dir):
            _logger.debug('Release directory does not exist: {0}'.format(release_dir))
            return local_versions

        version_dirs = os.listdir(release_dir)
        for version_dir in version_dirs:
            try:
                version_file = os.path.join(release_dir, version_dir, 'content', 'config', 'version.yml')
                if not os.path.isfile(version_file):
                    _logger.debug('Version directory "{0}" does not contain the version file'.format(version_dir))
                    continue

                with open(version_file) as f:
                    version_in_file = f.read().strip()

                local_versions.append(version_dir)

                if version_in_file != version_dir:
                    _logger.warn('Version inconsistent for "{0}": Defined as "{1}"'.format(version_dir, version_in_file))
            except:
                continue

        local_versions.sort()

        return local_versions
