import os

from bsm.cmd import Base
from bsm.cmd import CmdError

from bsm.logger import get_logger
_logger = get_logger()

class PkgBase(Base):
    def _check_release(self):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

    def _current_category(self, category):
        if category is None:
            ctg, _ = self._bsm.detect_category(os.getcwd())
            if ctg:
                _logger.info('Using current category: {0}'.format(category))
                return ctg
        return category
