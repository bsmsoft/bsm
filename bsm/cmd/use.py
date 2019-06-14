from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Use(Base):
    def execute(self, default=False, without_package=False):
        if not self._bsm.config('release_status').get('install', {}).get('finished'):
            _logger.warn('Release version {0} is not fully installed'.format(self._bsm.config('scenario')['version']))

        self._bsm.use(without_package)

        if default:
            self._bsm.save_as_default()

        return self._bsm.config('scenario')['version']
