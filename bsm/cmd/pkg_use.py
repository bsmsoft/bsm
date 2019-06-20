from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgUse(PkgBase):
    def execute(self, category, subdir, version, package):
        self._check_release()

        category = self._current_category(category)

        ctg, sd, ver = self._bsm.use_package(package, category, subdir, version)
        _logger.info('Load package "{0}" from category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))

        pkg_path = self._bsm.package_path(package, category, subdir, version)
        _logger.info('Package directory: {0}'.format(pkg_path['main_dir']))

        return ''
