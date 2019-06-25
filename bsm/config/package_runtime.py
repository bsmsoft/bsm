import copy

from bsm.config.package_base import PackageBase
from bsm.config.util import ConfigPackageParamError
from bsm.config.util import config_from_file, package_param_from_rel_dir
from bsm.config.util import transform_package, package_path, expand_package_path, expand_package_env, install_status, install_step

from bsm.util import walk_rel_dir

from bsm.logger import get_logger
_logger = get_logger()


class PackageRuntime(PackageBase):
    def __init__(self, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
        super(PackageRuntime, self).__init__(config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority)

    def _init_package(self, handler, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority):
        reinstall = config_entry.get('reinstall', False)

        category_runtime = [ctg for ctg, cfg in config_category.items() if cfg.get('root') and not cfg.get('pre_check')]

        _logger.debug('Category for runtime: {0}'.format(category_runtime))

        for category in category_runtime:
            version_dir = config_category[category]['version_dir']
            config_package_dir = config_category[category]['config_package_dir']

            for full_path, rel_dir, f in walk_rel_dir(config_package_dir):
                if f != config_app['config_package_file']:
                    continue

                try:
                    subdir, package, version = package_param_from_rel_dir(rel_dir, version_dir)
                except ConfigPackageParamError:
                    continue

                pkg_cfg = config_from_file(full_path)

                pkg_path = package_path(config_app, config_category, category, subdir, package, version)

                final_pkg_cfg = transform_package(handler, 'runtime', category, subdir, package, version, pkg_cfg, pkg_path,
                        config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category, config_category_priority)

                if not version_dir:
                    if 'version' in final_pkg_cfg and final_pkg_cfg['version']:
                        version = final_pkg_cfg['version']
                    else:
                        version = 'unknown'

                self.setdefault(category, {})
                self[category].setdefault(subdir, {})
                self[category][subdir].setdefault(package, {})
                self[category][subdir][package].setdefault(version, {})

                final_config = self[category][subdir][package][version]

                final_config['config_origin'] = copy.deepcopy(pkg_cfg)

                final_config['config'] = final_pkg_cfg
                final_config['config']['name'] = package
                final_config['config']['category'] = category
                final_config['config']['subdir'] = subdir
                final_config['config']['version'] = version

                final_config['package_path'] = package_path(config_app, config_category, category, subdir, package, final_config['config']['version'])
                expand_package_path(final_config['package_path']['main_dir'], final_config['config'])
                expand_package_env(final_config['config'])

                final_config['install_status'] = install_status(final_config['package_path']['status_install_file'])

                final_config['step'] = install_step(config_release_install, final_config['config'], final_config['install_status'], reinstall)
