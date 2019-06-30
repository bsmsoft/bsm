from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Use(Base):
    def execute(self, default=False, without_package=False):
        if not self._bsm.config('release_status').get('install', {}).get('finished'):
            _logger.warn('Release version {0} is not fully installed'.format(self._bsm.config('scenario')['version']))

        missing_pkg = self._bsm.check_missing_runtime()
        if missing_pkg:
            _logger.warn('Missing package found for runtime: {0}'.format(', '.join(missing_pkg.keys())))

        self._bsm.load_release()
        if not without_package:
            self._bsm.load_release_packages()

        if default:
            self._bsm.save_as_default()

        result = {}
        result['software_root'] = self._bsm.config('scenario').get('software_root', '')
        result['version'] = self._bsm.config('scenario').get('version', '')
        return result
