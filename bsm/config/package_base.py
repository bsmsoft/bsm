from bsm.config.common import Common

from bsm.handler import Handler

from bsm.util import safe_mkdir

from bsm.util.config import dump_config

from bsm.logger import get_logger
_logger = get_logger()


class ConfigPackageError(Exception):
    pass

class ConfigPackageParamError(Exception):
    pass


class PackageBase(Common):
    def __init__(self, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category):
        super(PackageBase, self).__init__()

        if not ('version' in config_scenario and config_scenario['version']):
            _logger.debug('"version" not specified in config package')
            return

        with Handler(config_release_path['handler_python_dir']) as h:
            self._init_package(h, config_entry, config_app, config_output, config_scenario, config_option, config_release_path, config_attribute, config_release, config_release_install, config_category)

    def package_config(self, category, subdir, name, version):
        if category not in self or subdir not in self[category] or name not in self[category][subdir] or version not in self[category][subdir][name]:
            _logger.error('Package not found: {0}.{1}.{2}.{3}'.format(category, name, subdir, version))
            raise ConfigPackageError
        return self[category][subdir][name][version]

    def save_install_status(self, category, subdir, name, version):
        pkg_install_cfg = self.package_config(category, subdir, name, version)
        safe_mkdir(pkg_install_cfg['package_path']['status_dir'])
        dump_config(pkg_install_cfg['install_status'], pkg_install_cfg['package_path']['status_install_file'])

    def save_package_config(self, category, subdir, name, version):
        pkg_install_cfg = self.package_config(category, subdir, name, version)
        safe_mkdir(pkg_install_cfg['package_path']['config_dir'])
        dump_config(pkg_install_cfg['config_origin'], pkg_install_cfg['package_path']['config_file'])
