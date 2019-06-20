from bsm.config.util import find_package
from bsm.config.util import package_path

from bsm.handler import Handler

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class PackagePathError(Exception):
    pass


class PackagePath(Base):
    def execute(self, package, category=None, subdir=None, version=None, must_exist=False):
        category_priority = self._config['category']['priority']
        _logger.debug('Package path category priority: {0}'.format(category_priority))

        if must_exist or category is None or subdir is None or version is None:
            with Handler(self._config['release_path']['handler_python_dir']) as h:
                ctg, sd, ver = find_package(h, category_priority, self._config['package_runtime'], package, category, subdir, version)

            _logger.debug('Find package result for "{0}": category "{1}", subdir "{2}", version "{3}"'.format(package, ctg, sd, ver))

            if ctg is None:
                raise PackagePathError('Specified package "{0}" not found for category "{1}", subdir "{2}", version "{3}"'.format(package, category, subdir, version))
        else:
            ctg, sd, ver = category, subdir, version

        return package_path(self._config['app'], self._config['category'], ctg, sd, package, ver)
