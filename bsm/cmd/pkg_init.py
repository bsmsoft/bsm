import os
import click

from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgInit(PkgBase):
    def execute(self, package_root, yes):   # pylint: disable=inconsistent-return-statements
        if not package_root:
            package_root = os.getcwd()

        self._check_release()

        ctg, subd, package, ver = self._bsm.detect_package_param(package_root)
        _logger.debug('Detect package param for "%s": category "%s", subdir "%s", version "%s"',
                      package, ctg, subd, ver)

        _logger.info('Will create package "%s" to category "%s", subdir "%s", version "%s"',
                     package, ctg, subd, ver)
        if not yes and not click.confirm('Proceed with package initialization?',
                                         default=True, err=True):
            return

        self._bsm.create_package_prop(package, ctg, subd, ver)
        _logger.info('Package "%s" initialized successfully', package)

        pkg_path = self._bsm.package_path(package, ctg, subd, ver)

        result = {}
        result['category'] = ctg
        result['subdir'] = subd
        result['name'] = package
        result['version'] = ver
        result['main_dir'] = pkg_path['main_dir']
        return result
