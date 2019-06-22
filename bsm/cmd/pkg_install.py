import click

from bsm.cmd import CmdError
from bsm.cmd.pkg_base import PkgBase

from bsm.logger import get_logger
_logger = get_logger()

class PkgInstall(PkgBase):
    def execute(self, category, subdir, version, category_origin, subdir_origin, version_origin, package, yes):
        self._check_release()

        ctg, sd, ver, ctg_org, sd_org, ver_org, from_install = self._bsm.match_install_package(package, category, subdir, version, category_origin, subdir_origin, version_origin)
        _logger.debug('Matched install package: To category "{0}", subdir "{1}", version "{2}", from category "{3}", subdir "{4}", version "{5}", from_install "{6}"'.format(ctg, sd, ver, ctg_org, sd_org, ver_org, from_install))

        if ctg is None:
            raise CmdError('Could not find out how to install the package "{0}"'.format(package))

        pkg_path = self._bsm.package_path(package, ctg, sd, ver)
        _logger.info('Will install package "{0}" to category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))
        _logger.info('The package directory will be: {0}"'.format(pkg_path['main_dir']))

        if not yes and not click.confirm('Proceed with installation?', default=True, err=True):
            return

        # Install package config if not exist
        if ctg_org is not None:
            _logger.debug('Install package config for "{0}"'.format(package))
            self._bsm.install_package_config(package, ctg, sd, ver, ctg_org, sd_org, ver_org, from_install)

        self._bsm.install_package(package, ctg, sd, ver)

        _logger.info('Package "{0}" installed successfully'.format(package))

        result = {}
        result['category'] = ctg
        result['subdir'] = sd
        result['name'] = package
        result['version'] = ver
        result['main_dir'] = pkg_path['main_dir']

        return result
