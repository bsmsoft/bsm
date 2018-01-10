import click

try:
    input = raw_input
except NameError:
    pass

from cepcenv.config.config_release import ConfigRelease
from cepcenv.config.config_release import ConfigReleaseTransformError
from cepcenv.install import Install as CepcenvInstall

from cepcenv.logger import get_logger
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

def _install(config, config_version, source, force, yes, no_clean):
    transformer = []
    if source:
        transformer.append(source + '_source')
    if no_clean:
        transformer.append('no_clean')

    install = CepcenvInstall(config, config_version, None, transformer)

    if not force:
        missing_pkg, install_cmd, pkg_install_name = install.check()
        if missing_pkg:
            _logger.warn('Missing package(s): {0}'.format(', '.join(missing_pkg)))
            _logger.info('If you are confirmed these packages are available and would like to skip installing them, try to use "cepcenv install --force"')
            _logger.info('The missing package(s) could be installed with the following command:\n' + ' '.join(install_cmd+pkg_install_name))
            return


    click.echo('CEPCEnv is going to install the following packages:')
    click.echo('')

    _output_preview_lines(install.package_list())

    click.echo('')
    click.echo('Version: {0}'.format(config_version.get('version')))
    click.echo('Software root: {0}'.format(config_version.get('software_root')))
    click.echo('')


    if not yes and not click.confirm('Proceed with installation?', default=True):
        return


    try:
        install.install_packages()
    except ConfigReleaseTransformError as e:
        _logger.critical('Install source error: {0}'.format(source))
        raise

    click.echo('')
    click.echo('Installation finished successfully')
    click.echo('Version: {0}'.format(config_version.get('version')))
    click.echo('Software root: {0}'.format(config_version.get('software_root')))

def _clean_only(config, config_version):
    transformer = ['clean_only']
    config_release = ConfigRelease(config_version)
    install = CepcenvInstall(config, config_version, config_release, transformer)
    install.install_packages()


class Install(object):
    def execute(self, config, config_version, source, force, yes, no_clean, clean_only):
        if clean_only:
            _clean_only(config, config_version)
        else:
            _install(config, config_version, source, force, yes, no_clean)
