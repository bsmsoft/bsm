from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Current(Base):
    def execute(self):
        current_release = self._bsm.current()

        result = {}

        if 'release_version' not in current_release:
            _logger.warn('No release loaded currently')
            return result

        result['software_root'] = current_release.get('software_root', '')
        result['version'] = current_release.get('release_version', '')

        return result
