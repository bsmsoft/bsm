from bsm.config.util import find_package
from bsm.config.util import package_path

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.handler import Handler

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackageConfigError(Exception):
    pass


class InstallPackageConfig(Base):
    def execute(self, package, category=None, subdir=None, version=None, category_origin=None, subdir_origin=None, version_origin=None, from_install=False):
        config_package_name = 'package_install' if from_install else 'package_runtime'

        category_priority = self._config['category']['priority']

        pkg_cfg_origin = self._config[config_package_name].package_config(category_origin, subdir_origin, package, version_origin)['config_origin']

        pkg_path = package_path(self._config['app'], self._config['category'], category, subdir, package, version)
        safe_mkdir(pkg_path['config_dir'])
        dump_config(pkg_cfg_origin, pkg_path['config_file'])

        self._config.reset()
