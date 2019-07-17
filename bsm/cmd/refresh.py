from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Refresh(Base):
    def execute(self):  # pylint: disable=inconsistent-return-statements
        if 'version' not in self._bsm.prop('scenario'):
            _logger.warning('No release loaded currently, nothing to do')
            return

        self._bsm.load_release()
        self._bsm.load_release_packages()

        result = {}
        result['software_root'] = self._bsm.prop('scenario').get('software_root', '')
        result['version'] = self._bsm.prop('scenario').get('version', '')
        return result
