from bsm.config.util import find_package

from bsm.handler import Handler

from bsm.operation import Base

class FindPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None, from_install=False):
        config_package_name = 'package_install' if from_install else 'package_runtime'

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            return find_package(h, self._config['category_priority'], self._config[config_package_name], package, category, subdir, version)
