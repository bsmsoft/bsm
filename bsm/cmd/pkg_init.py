import os

from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgInit(PkgBase):
    def execute(self, package_root):
        if not package_root:
            package_root = os.getcwd()

        self._check_release()

        ctg, sd, package, ver = self._bsm.detect_package(package_root)
        _logger.debug('Detected package "{0}": category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))

        if self._bsm.package_exist(package, ctg, sd, ver):
            raise CmdError('Package "{0}" already exist for category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))

        self._bsm.create_package_config(package, ctg, sd, ver)
        _logger.info('Package "{0}" initialized successfully'.format(package))

        pkg_path = self._bsm.package_path(package, ctg, sd, ver)

        result = {}
        result['category'] = ctg
        result['subdir'] = sd
        result['name'] = package
        result['version'] = ver
        result['main_dir'] = pkg_path['main_dir']
        return result
