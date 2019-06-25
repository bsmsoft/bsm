import copy

from bsm.config.util import package_path
from bsm.config.util import check_conflict_package

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackageConfigError(Exception):
    pass


class InstallPackageConfig(Base):
    def execute(self, package, category, subdir, version, category_origin, subdir_origin, version_origin, from_install=False):
        config_package_name = 'package_install' if from_install else 'package_runtime'

        pkg_cfg_origin = copy.deepcopy(self._config[config_package_name].package_config(category_origin, subdir_origin, package, version_origin)['config_origin'])
        pkg_cfg_origin['version'] = version

        pkg_path = package_path(self._config['app'], self._config['category'], category, subdir, package, version)

        ctg_cf, sd_cf, pkg_cf, ver_cf = check_conflict_package(pkg_path['main_dir'], self._config['package_runtime'])
        if ctg_cf:
            raise InstallPackageConfigError('Package path conflicts with package "{0}", category "{1}", subdir "{2}", version "{3}"'.format(pkg_cf, ctg_cf, sd_cf, ver_cf))

        safe_mkdir(pkg_path['config_dir'])
        dump_config(pkg_cfg_origin, pkg_path['config_file'])

        self._config.reset()
