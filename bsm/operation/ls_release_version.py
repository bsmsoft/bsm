import os

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class LsReleaseVersion(Base):
    def execute(self):
        local_versions = []

        try:
            release_dir = self._config['release_path']['release_dir']
            version_dirs = os.listdir(release_dir)
            for version_dir in version_dirs:
                try:
                    with open(os.path.join(release_dir, version_dir, 'content', 'config', 'version.yml')) as f:
                        version_in_def = f.read().strip()

                    local_versions.append(version_dir)

                    if version_in_def != version_dir:
                        _logger.warn('Version inconsistent for "{0}": Defined as "{1}"'.format(version_dir, version_in_def))
                except:
                    continue
        except:
            pass

        local_versions.sort()
        return local_versions
