import click

from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgRemove(PkgBase):
    def execute(self, category, subdir, version, force, package):
        self._check_release()

        category, subdir, package, version = self._process_param(package, category, subdir, version)

        if not force and not click.confirm('Proceed with package removing?', err=True):
            return

        self._bsm.remove_package(package, category, subdir, version)
        _logger.info('Package removed successfully')

        pkg_path = self._bsm.package_path(package, category, subdir, version)
        _logger.info('The main directory could be removed manually: {0}'.format(pkg_path['main_dir']))
