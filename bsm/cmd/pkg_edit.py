from bsm.cmd import Base
from bsm.cmd import CmdError

from bsm.logger import get_logger
_logger = get_logger()

class PkgEdit(Base):
    def execute(self, category, subdir, version, category_origin, subdir_origin, version_origin, package):
        if 'release_version' not in self._bsm.current():
            raise CmdError('No release loaded currently')

        _logger.warn('Editor open failed. Please edit the package configuration file by yourself: {0}'.format(package))

        return ''
