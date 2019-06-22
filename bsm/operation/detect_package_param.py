import os

from bsm.config.util import detect_category

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class DetectPackageParamError(Exception):
    pass


class DetectPackageParam(Base):
    def execute(self, package_dir):
        category, rest_dir = detect_category(self._config['category'], package_dir)
        if category is None:
            raise DetectPackageParamError('Category not found for the directory: {0}'.format(package_dir))

        _logger.debug('Category found: {0}'.format(category))

        version_dir = self._config['category'][category]['version_dir']

        frag = rest_dir.split(os.sep)

        version = None
        if version_dir:
            if len(frag) < 1:
                raise DetectPackageParamError('Impossible to find version under category "{0}": {1}'.format(category, package_dir))
            version = frag[-1]
            frag = frag[:-1]

        if len(frag) < 1:
            raise DetectPackageParamError('Impossible to find package name under category "{0}": {1}'.format(category, package_dir))
        package = frag[-1]
        frag = frag[:-1]

        subdir = ''
        if frag:
            subdir = os.path.join(*frag)

        return category, subdir, package, version
