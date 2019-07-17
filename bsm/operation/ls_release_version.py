import os

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsReleaseVersion(Base):
    def execute(self, installed=False):
        local_versions = []

        release_dir = self._prop['release_dir']
        _logger.debug('Search local versions under release directory: %s', release_dir)

        if not os.path.isdir(release_dir):
            _logger.debug('Release directory does not exist: %s', release_dir)
            return local_versions

        version_dirs = os.listdir(release_dir)

        local_versions = self.__list_version(version_dirs, installed)

        local_versions.sort()

        return local_versions

    def __list_version(self, version_dirs, installed):
        local_versions = []

        prop_entry = self._prop['entry'].data_copy()
        for version_dir in version_dirs:
            prop_entry['version'] = version_dir
            self._prop.reset(prop_entry)

            if installed:
                if not self.__check_version_installed():
                    continue

            local_versions.append(version_dir)

            version_in_release = self._prop['release_version']
            if version_in_release != version_dir:
                _logger.warning(
                    'Version inconsistent for "%s": Defined as "%s"',
                    version_dir, version_in_release)

        return local_versions

    def __check_version_installed(self):
        return self._prop['release_status'].get('install', {}).get('finished', False)
