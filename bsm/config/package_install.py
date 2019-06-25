import os
import copy

from bsm.config.package_base import PackageBase
from bsm.config.util import ConfigPackageParamError
from bsm.config.util import package_param_from_identifier, transform_package, package_path, expand_package_path, expand_package_env, install_status, install_step

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class PackageInstall(PackageBase):
    def __init__(self, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
        super(PackageInstall, self).__init__(config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority)

    def _init_package(self, handler, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
        reinstall = config_entry.get('reinstall', False)

        category_install = [ctg for ctg, ctg_cfg in config_category.items() if ctg_cfg['install']]

        _logger.debug('Category for install: {0}'.format(category_install))

        for identifier, pkg_cfg in config_release.get('package', {}).items():
            try:
                category_name, subdir, pkg_name = package_param_from_identifier(identifier, pkg_cfg)
            except ConfigPackageParamError:
                continue

            if category_name not in category_install:
                _logger.debug('Package "{0}" could not be installed with category "{1}"'.format(pkg_name, category_name))
                continue

            version = ensure_list(pkg_cfg.get('version', []))

            version_dir = config_category[category_name]['version_dir']
            if (not version_dir) and len(version) > 1:
                _logger.warn('Only one version could be installed when category version_dir is false')
                version = version[:1]

            if not version:
                _logger.warn('No version is specified for category({0}), package({1})'.format(category_name, pkg_name))

            for ver in version:
                self.setdefault(category_name, {})
                self[category_name].setdefault(subdir, {})
                self[category_name][subdir].setdefault(pkg_name, {})
                if ver in self[category_name][subdir][pkg_name]:
                    _logger.warn('Duplicated package found: category({0}), subdir({1}), package({2}), version({3})'.format(category_name, subdir, pkg_name, ver))
                self[category_name][subdir][pkg_name].setdefault(ver, {})
                final_config = self[category_name][subdir][pkg_name][ver]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)
                final_config['config_origin']['version'] = ver

                pkg_path = package_path(config_app, config_category, category_name, subdir, pkg_name, ver)

                final_config['config'] = transform_package(handler, 'install', category_name, subdir, pkg_name, ver, pkg_cfg, pkg_path,
                        config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name
                final_config['config']['subdir'] = subdir
                if 'version' not in final_config['config']:
                    final_config['config']['version'] = ver

                final_config['package_path'] = package_path(config_app, config_category, category_name, subdir, pkg_name, final_config['config']['version'])
                expand_package_path(final_config['package_path']['main_dir'], final_config['config'])
                expand_package_env(final_config['config'])

                final_config['install_status'] = install_status(final_config['package_path']['status_install_file'])

                final_config['step'] = install_step(config_release_install, final_config['config'], final_config['install_status'], reinstall)
