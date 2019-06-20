import os

from bsm.config.util import package_path

from bsm.util import safe_mkdir

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class CreatePackageConfig(Base):
    def execute(self, package, category, subdir, version):
        pkg_path = package_path(self._config['app'], self._config['category'], category, subdir, package, version)

        safe_mkdir(pkg_path['config_dir'])

        if not os.path.exists(pkg_path['config_file']):
            open(pkg_path['config_file'], 'w').close()

        self._config.reset()
