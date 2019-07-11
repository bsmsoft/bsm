import os

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsReleaseVersion(Base):
    def execute(self, list_all=False):
        local_versions = []

        release_dir = self._config['release_dir']
        _logger.debug('Search local versions under release directory: %s', release_dir)

        if not os.path.isdir(release_dir):
            _logger.debug('Release directory does not exist: %s', release_dir)
            return local_versions

        version_dirs = os.listdir(release_dir)

        if list_all:
            local_versions = self.__simple_version(version_dirs)
        else:
            local_versions = self.__good_version(version_dirs)

        local_versions.sort()

        return local_versions

    def __good_version(self, version_dirs):
        local_versions = []

        config_entry = self._config['entry'].data()
        for version_dir in version_dirs:
            config_entry['version'] = version_dir
            self._config.reset(config_entry)
            for status in self._config['release_status']:
                match = True
                for k, v in status.get('attribute', {}).items():
                    if k not in self._config['attribute'] or v != self._config['attribute'][k]:
                        match = False
                        break
                if match:
                    local_versions.append(version_dir)
                    version_in_release = self._config['release_version']
                    if version_in_release != version_dir:
                        _logger.warning(
                            'Version inconsistent for "%s": Defined as "%s"',
                            version_dir, version_in_release)
                    break

        return local_versions

    def __simple_version(self, version_dirs):
        local_versions = []

        for version_dir in version_dirs:
            try:
                version_file = os.path.join(
                    self._config['release_dir'], version_dir, 'content', 'config', 'version.yml')
                if not os.path.isfile(version_file):
                    _logger.debug(
                        'Version directory "%s" does not contain the version file', version_dir)
                    continue

                with open(version_file) as f:
                    version_in_file = f.read().strip()

                local_versions.append(version_dir)

                if version_in_file != version_dir:
                    _logger.warning(
                        'Version inconsistent for "%s": Defined as "%s"',
                        version_dir, version_in_file)
            except IOError:
                continue

        return local_versions
