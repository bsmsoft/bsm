import click

from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgInstall(PkgBase):
    def execute(self, category, subdir, version,    # pylint: disable=inconsistent-return-statements
                category_origin, subdir_origin, version_origin, package, yes):
        self._check_release()

        ctg, subd, ver, ctg_org, subd_org, ver_org, from_install = self._bsm.match_install_package(
            package, category, subdir, version, category_origin, subdir_origin, version_origin)
        _logger.debug('Matched install package: '
                      'To category "%s", subdir "%s", version "%s", '
                      'from category "%s", subdir "%s", version "%s", from_install "%s"',
                      ctg, subd, ver, ctg_org, subd_org, ver_org, from_install)

        if ctg is None:
            raise CmdError('Could not find out how to install the package "{0}"'.format(package))

        pkg_path = self._bsm.package_path(package, ctg, subd, ver)
        _logger.info('Will install package "%s" to category "%s", subdir "%s", version "%s"',
                     package, ctg, subd, ver)
        _logger.info('The package directory will be: %s"', pkg_path['main_dir'])

        if not yes and not click.confirm('Proceed with installation?', default=True, err=True):
            return

        # Install package prop if not exist
        if ctg_org is not None:
            _logger.debug('Install package prop for "%s"', package)
            self._bsm.install_package_prop(package, ctg, subd, ver,
                                           ctg_org, subd_org, ver_org, from_install)

        self._bsm.install_package(package, ctg, subd, ver)

        _logger.info('Package "%s" installed successfully', package)

        result = {}
        result['category'] = ctg
        result['subdir'] = subd
        result['name'] = package
        result['version'] = ver
        result['main_dir'] = pkg_path['main_dir']

        return result
