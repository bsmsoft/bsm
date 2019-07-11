import copy

from bsm.config.package_base import PackageBase
from bsm.config.util import ConfigPackageParamError
from bsm.config.util import package_param_from_identifier, transform_package
from bsm.config.util import package_path, expand_package_path, expand_package_env
from bsm.config.util import install_status, install_step

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class PackageInstall(PackageBase):
    def _init_package(self, handler, config):
        reinstall = config['entry'].get('reinstall', False)

        category_install = [
            ctg for ctg, ctg_cfg in config['category'].items() if ctg_cfg['install']]

        _logger.debug('Category for install: %s', category_install)

        for identifier, pkg_cfg in config['release_package'].items():
            try:
                category_name, subdir, pkg_name = package_param_from_identifier(identifier, pkg_cfg)
            except ConfigPackageParamError:
                continue

            if category_name not in category_install:
                _logger.debug(
                    'Package "%s" could not be installed with category "%s"',
                    pkg_name, category_name)
                continue

            version = ensure_list(pkg_cfg.get('version', []))

            version_dir = config['category'][category_name]['version_dir']
            if (not version_dir) and len(version) > 1:
                _logger.warning(
                    'Only one version could be installed when category version_dir is false')
                version = version[:1]

            if not version:
                _logger.warning(
                    'No version is specified for category "%s", package "%s"',
                    category_name, pkg_name)

            for ver in version:
                self.setdefault(category_name, {})
                self[category_name].setdefault(subdir, {})
                self[category_name][subdir].setdefault(pkg_name, {})
                if ver in self[category_name][subdir][pkg_name]:
                    _logger.warning(
                        'Duplicated package found: '
                        'category "%s", subdir "%s", package "%s", version "%s"',
                        category_name, subdir, pkg_name, ver)
                self[category_name][subdir][pkg_name].setdefault(ver, {})
                final_config = self[category_name][subdir][pkg_name][ver]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)
                final_config['config_origin']['version'] = ver

                pkg_path = package_path(
                    config['app'], config['category'], category_name, subdir, pkg_name, ver)

                final_config['config'] = transform_package(
                    handler, 'install',
                    category_name, subdir, pkg_name, ver, pkg_cfg, pkg_path, config)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name
                final_config['config']['subdir'] = subdir
                if 'version' not in final_config['config']:
                    final_config['config']['version'] = ver

                final_config['package_path'] = package_path(
                    config['app'], config['category'],
                    category_name, subdir, pkg_name, final_config['config']['version'])
                expand_package_path(
                    final_config['package_path']['main_dir'], final_config['config'])
                expand_package_env(final_config['config'])

                final_config['install_status'] = install_status(
                    final_config['package_path']['status_install_file'])

                final_config['step'] = install_step(
                    config['release_install'], final_config['config'],
                    final_config['install_status'], reinstall)
