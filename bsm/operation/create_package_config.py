import os

from bsm.config.util import package_path
from bsm.config.util import check_conflict_package

from bsm.util import safe_mkdir

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class CreatePackageConfigError(Exception):
    pass


class CreatePackageConfig(Base):
    def execute(self, package, category, subdir, version):
        pkg_path = package_path(self._config['app'], self._config['category'], category, subdir, package, version)

        ctg_cf, sd_cf, pkg_cf, ver_cf = check_conflict_package(pkg_path['main_dir'], self._config['package_runtime'])
        if ctg_cf:
            raise CreatePackageConfigError('Package path conflicts with package "{0}", category "{1}", subdir "{2}", version "{3}"'.format(pkg_cf, ctg_cf, sd_cf, ver_cf))

        safe_mkdir(pkg_path['config_dir'])

        if not os.path.exists(pkg_path['config_file']):
            open(pkg_path['config_file'], 'w').close()

        self._config.reset()
