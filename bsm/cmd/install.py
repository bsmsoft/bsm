from bsm.cmd import Base

from bsm.config.release import ConfigReleaseError

from bsm.logger import get_logger
_logger = get_logger()


class Install(Base):
    def execute(self, reinstall, update, no_software, force, yes):
        if update or not self.__release_exist():
            self._bsm.install_release()
            self._bsm.reload_config()

        if not no_software:
            pass

        return self._bsm.config('scenario')['version']

    def __release_exist(self):
        try:
            self._bsm.config('release')
        except ConfigReleaseError as e:
            _logger.debug('Release load error: {0}'.format(e))
            return False
        return True
