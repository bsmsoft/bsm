from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Refresh(Base):
    def execute(self):
        if 'version' not in self._bsm.config('scenario'):
            _logger.warn('No release loaded currently')
            return ''

        self._bsm.load_release()
        self._bsm.load_release_package()

        return self._bsm.config('scenario')['version']
