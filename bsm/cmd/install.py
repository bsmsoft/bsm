import click

from bsm.cmd import Base

from bsm.config.release import ConfigReleaseError

from bsm.logger import get_logger
_logger = get_logger()


def _output_preview_lines(config_package_install):
    max_package_length = 1
    max_category_length = 1
    max_subdir_length = 1
    max_version_length = 1

    packages = {}

    for category in config_package_install:
        for subdir in config_package_install[category]:
            for package in config_package_install[category][subdir]:
                for version, value in config_package_install[category][subdir][package].items():
                    packages.setdefault(package, [])
                    packages[package].append((category, subdir, version, value['package_path']['main_dir']))

                    package_length = len(package)
                    if max_package_length < package_length:
                        max_package_length = package_length

                    category_length = len(category)
                    if max_category_length < category_length:
                        max_category_length = category_length

                    subdir_length = len(subdir)
                    if max_subdir_length < subdir_length:
                        max_subdir_length = subdir_length

                    version_length = len(str(version))
                    if max_version_length < version_length:
                        max_version_length = version_length

    for package, value in packages.items():
        for l in value:
            line = ' - {0:{pkg_width}} | {1:{ctg_width}} | {2:{sd_width}} | {3:{ver_width}} | {4}'\
                    .format(package, *l, pkg_width=max_package_length, ctg_width=max_category_length, sd_width=max_subdir_length, ver_width=max_version_length)
            click.echo(line, err=True)
    click.echo('', err=True)


class Install(Base):
    def execute(self, update, without_package, force, yes):
        result = {}
        result['software_root'] = self._bsm.config('scenario').get('software_root', '')
        result['version'] = self._bsm.config('scenario').get('version', '')

        if update or not self.__release_exist():
            self._bsm.install_release()

        if without_package:
            return result

        if not force:
            missing_pkg = self._bsm.check_missing_install()
            if missing_pkg:
                _logger.warn('Missing package found for installation: {0}'.format(', '.join(missing_pkg.keys())))

        _logger.info('The following packages will be installed:\n')
        _output_preview_lines(self._bsm.config('package_install'))

        if not yes and not click.confirm('Proceed with installation?', default=True, err=True):
            return

        self._bsm.install_release_packages()

        _logger.info('Installation finished successfully')

        return result

    def __release_exist(self):
        try:
            self._bsm.config('release')
        except ConfigReleaseError as e:
            _logger.debug('Release can not be loaded and should be installed: {0}'.format(e))
            return False
        return True
