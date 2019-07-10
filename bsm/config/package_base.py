from bsm.handler import Handler

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.config.util import ConfigPackageError

from bsm.config.common_dict import CommonDict

from bsm.logger import get_logger
_logger = get_logger()


class PackageBase(CommonDict):
    def __init__(self, **config):
        super(PackageBase, self).__init__()

        with Handler(config['release_path']['handler_python_dir']) as h:
            self._init_package(h, **config)

    def package_exist(self, category, subdir, name, version):
        return category in self and subdir in self[category] and \
                name in self[category][subdir] and version in self[category][subdir][name]

    def package_config(self, category, subdir, name, version):
        if not self.package_exist(category, subdir, name, version):
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
