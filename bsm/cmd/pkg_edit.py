from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class PkgEdit(Base):
    def execute(self, category, subdir, version, category_origin, subdir_origin, version_origin, package):

        _logger.warn('Editor open failed. Please edit the package configuration file by yourself: {0}'.format(package))

        return ''
