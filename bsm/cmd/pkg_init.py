import os
import click

from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgInit(PkgBase):
    def execute(self, package_root, yes):
        if not package_root:
            package_root = os.getcwd()

        self._check_release()

        ctg, sd, package, ver = self._bsm.detect_package_param(package_root)
        _logger.debug('Detect package param for "{0}": category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))

        _logger.info('Will create package "{0}" to category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))
        if not yes and not click.confirm('Proceed with package initialization?', default=True, err=True):
            return

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
