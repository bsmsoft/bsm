import os
import sys
import copy

from bsm.config.common import Common
from bsm.config.util.install import transform_package, package_path, expand_package_path, expand_package_env, install_status, install_step

from bsm.util import ensure_list
from bsm.util import safe_mkdir

from bsm.util.config import dump_config

from bsm.logger import get_logger
_logger = get_logger()


class ConfigPackageInstallError(Exception):
    pass

class ConfigPackageInstallParamError(Exception):
    pass


def _package_param(identifier, pkg_cfg):
    frag = identifier.split(os.sep)

    # Use the last part as default package name
    if 'name' in pkg_cfg:
        pkg_name = pkg_cfg['name']
    elif frag[-1]:
        pkg_name = frag[-1]
    else:
        _logger.error('Package name not found for {0}'.format(identifier))
        raise ConfigPackageInstallParamError

    frag = frag[:-1]

    # Use the first part as default category name
    if 'category' in pkg_cfg:
        category_name = pkg_cfg['category']
    elif len(frag) > 0:
        category_name = frag[0]
    else:
        _logger.warn('Category not specified for {0}'.format(identifier))
        raise ConfigPackageInstallParamError

    frag = frag[1:]

    # Use the middle part as default subdir
    if 'subdir' in pkg_cfg:
        subdir = pkg_cfg['subdir']
    elif frag:
        subdir = os.path.join(*frag)
    else:
        subdir = ''

    return (category_name, pkg_name, subdir)


class PackageInstall(Common):
    def load(self, config_entry, config_app, config_output, config_scenario, config_release_path, config_attribute, config_release, config_release_install, config_category):
        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config install')
            return

        reinstall = config_entry.get('reinstall', False)

        category_install = [ctg for ctg, ctg_cfg in config_category.items() if ctg_cfg['install']]

        sys.path.insert(0, config_release_path['handler_python_dir'])

        for identifier, pkg_cfg in config_release.get('package', {}).items():
            try:
                category_name, pkg_name, subdir = _package_param(identifier, pkg_cfg)
            except ConfigPackageInstallParamError:
                continue

            if category_name not in category_install:
                _logger.warn('Category "{0}" could not be installed for package "{1}"'.format(category_name, pkg_name))
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

                final_config['config'] = transform_package('install', category_name, subdir, pkg_name, ver, pkg_cfg,
                        config_app, config_output, config_scenario, config_release_path, config_attribute, config_release, config_release_install, config_category)
                final_config['config']['name'] = pkg_name
                final_config['config']['category'] = category_name
                final_config['config']['subdir'] = subdir
                if 'version' not in final_config['config']:
                    final_config['config']['version'] = ver

                final_config['package_path'] = package_path(config_app, config_category, final_config['config'])
                expand_package_path(final_config['package_path']['main_dir'], final_config['config'])
                expand_package_env(final_config['config'])

                final_config['install_status'] = install_status(final_config['package_path']['status_install_file'])

                final_config['step'] = install_step(config_release_install, final_config['config'], final_config['install_status'], reinstall)

        sys.path.remove(config_release_path['handler_python_dir'])

    def package_install_config(self, category, subdir, name, version):
        if category not in self or subdir not in self[category] or name not in self[category][subdir] or version not in self[category][subdir][name]:
            _logger.error('Package not found for installation: {0}.{1}.{2}.{3}'.format(category, name, subdir, version))
            raise ConfigPackageInstallError
        return self[category][subdir][name][version]

    def save_install_status(self, category, subdir, name, version):
        pkg_install_cfg = self.package_install_config(category, subdir, name, version)
        safe_mkdir(pkg_install_cfg['package_path']['status_dir'])
        dump_config(pkg_install_cfg['install_status'], pkg_install_cfg['package_path']['status_install_file'])

    def save_package_config(self, category, subdir, name, version):
        pkg_install_cfg = self.package_install_config(category, subdir, name, version)
        safe_mkdir(pkg_install_cfg['package_path']['config_dir'])
        dump_config(pkg_install_cfg['config_origin'], pkg_install_cfg['package_path']['config_file'])

