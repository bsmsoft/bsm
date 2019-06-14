import os
import copy

from bsm.config.common import Common
from bsm.config.util.install import transform_package, package_path, expand_package_path, expand_package_env

from bsm.handler import Handler

from bsm.util import walk_rel_dir
from bsm.util.config import load_config, ConfigError

from bsm.logger import get_logger
_logger = get_logger()


class ConfigPackageRuntimeParamError(Exception):
    pass


def _package_param(rel_dir, version_dir):
    frag = rel_dir.split(os.sep)
    if version_dir:
        if len(frag) < 3 or frag[-2] != 'versions':
            _logger.warn('Package config path is not valid: {0}'.format(rel_dir))
            raise ConfigPackageRuntimeParamError
        version = frag[-1]
        frag = frag[:-2]
    else:
        if len(frag) < 2 or frag[-1] != 'head':
            _logger.warn('Package config path is not valid: {0}'.format(rel_dir))
            raise ConfigPackageRuntimeParamError
        version = ''
        frag = frag[:-1]

    package = frag[-1]

    frag = frag[:-1]
    if frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (subdir, package, version)


class PackageRuntime(Common):
    def __init__(self, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_category):
        super(PackageRuntime, self).__init__()

        category_runtime = [ctg for ctg, cfg in config_category['content'].items() if cfg.get('root')]

        _logger.debug('Category for runtime: {0}'.format(category_runtime))

        with Handler(config_release_path['handler_python_dir']) as h:
            for category in category_runtime:
                version_dir = config_category['content'][category]['version_dir']
                config_package_dir = config_category['content'][category]['config_package_dir']

                for full_path, rel_dir, f in walk_rel_dir(config_package_dir):
                    if f != config_app['config_package_file']:
                        continue

                    try:
                        subdir, package, version = _package_param(rel_dir, version_dir)
                    except ConfigPackageRuntimeParamError:
                        continue

                    try:
                        pkg_cfg = load_config(full_path)
                    except ConfigError as e:
                        _logger.warn('Fail to load package config file "{0}": {1}'.format(full_path, e))
                        continue

                    final_pkg_cfg = transform_package(h, 'runtime', category, subdir, package, version, pkg_cfg,
                            config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_category)

                    if not version_dir:
                        if 'version' in final_pkg_cfg and final_pkg_cfg['version']:
                            version = final_pkg_cfg.get['version']
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

                    final_config['package_path'] = package_path(config_app, config_category, final_config['config'])
                    expand_package_path(final_config['package_path']['main_dir'], final_config['config'])
                    expand_package_env(final_config['config'])
