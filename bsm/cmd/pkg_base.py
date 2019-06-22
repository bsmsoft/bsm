import os

from bsm.cmd import Base
from bsm.cmd import CmdError

from bsm.logger import get_logger
_logger = get_logger()

class PkgBase(Base):
    def _check_release(self):
        if 'version' not in self._bsm.config('scenario'):
            raise CmdError('No release loaded currently')

    def _process_param(self, package=None, category=None, subdir=None, version=None):
        if package is None:
            category, subdir, package, version = self._bsm.detect_package(os.getcwd())
            if package is None:
                raise CmdError('Can not tell which package to use')
            _logger.info('Found current package "{0}": category "{1}", subdir "{2}", version "{3}"'.format(package, category, subdir, version))
        elif category is None or subdir is None or version is None:
            category, subdir, version = self._bsm.find_package(package, category, subdir, version)
            if category is None:
                raise CmdError('Can not find package: {0}'.format(package))
            _logger.info('Found package "{0}": category "{1}", subdir "{2}", version "{3}"'.format(package, category, subdir, version))
        return category, subdir, package, version
