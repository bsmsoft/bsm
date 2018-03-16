import click

try:
    input = raw_input
except NameError:
    pass

from bsm.config.config_release import ConfigRelease
from bsm.config.config_release import ConfigReleaseError
from bsm.install import Install as BsmInstall
from bsm.install.version import install_version

from bsm.logger import get_logger
_logger = get_logger()

def _output_preview_lines(pkg_list):
    pkg_max = 0
    version_max = 0

    for pkg_single in pkg_list:
        pkg_len = len(pkg_single[0])
        if pkg_len > pkg_max:
            pkg_max = pkg_len

        ver_len = len(pkg_single[1])
        if ver_len > version_max:
            version_max = ver_len

    for pkg_single in pkg_list:
        click.echo(' - {0:{pmax}} {1:{vmax}} : {2}'.format(*pkg_single, pmax=pkg_max, vmax=version_max))

def _get_config_release(config_user, config_version, option, update):
    config_release = None

    if not update:
        try:
            config_release = ConfigRelease(config_user, config_version, option)
        except ConfigReleaseError as e:
            pass

    if not config_release:
        install_version(config_version)
        config_release = ConfigRelease(config_user, config_version, option)

    return config_release


class Install(object):
    def execute(self, config_user, config_version, option, reinstall, update, force, yes):
        config_release = _get_config_release(config_user, config_version, option, update)

        install = BsmInstall(config_user, config_version, config_release)

        if not force:
            missing_pkg, install_cmd, pkg_install_name = install.check()
            if missing_pkg:
                _logger.warn('Missing package(s): {0}'.format(', '.join(missing_pkg)))
                _logger.info('If you are confirmed these packages are available and would like to skip installing them, try to use "bsm install --force"')
                _logger.info('The missing package(s) could be installed with the following command:\n' + ' '.join(install_cmd+pkg_install_name))
                return


        click.echo('The following packages will be installed:')
        click.echo('')

        _output_preview_lines(install.package_list())

        click.echo('')
        click.echo('Version: {0}'.format(config_version.get('version')))
        click.echo('Software root: {0}'.format(config_version.get('software_root')))
        click.echo('')


        if not yes and not click.confirm('Proceed with installation?', default=True):
            return


        install.install_packages()


        click.echo('')
        click.echo('Installation finished successfully')
        click.echo('Version: {0}'.format(config_version.get('version')))
        click.echo('Software root: {0}'.format(config_version.get('software_root')))
