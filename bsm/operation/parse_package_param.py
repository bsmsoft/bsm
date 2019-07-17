import os

from bsm.error import OperationParsePackageParamError

from bsm.prop.util import detect_category

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class ParsePackageParam(Base):
    def execute(self, package_dir):
        category, rest_dir = detect_category(self._prop['category'], package_dir)
        if category is None:
            raise OperationParsePackageParamError(
                'Category not found for the directory: {0}'.format(package_dir))

        _logger.debug('Category found: %s', category)

        version_dir = self._prop['category'][category]['version_dir']

        frag = rest_dir.split(os.sep)

        version = None
        if version_dir:
            if not frag:
                raise OperationParsePackageParamError(
                    'Impossible to find version under category "{0}": {1}'
                    .format(category, package_dir))
            version = frag[-1]
            frag = frag[:-1]

        if not frag:
            raise OperationParsePackageParamError(
                'Impossible to find package name under category "{0}": {1}'
                .format(category, package_dir))
        package = frag[-1]
        frag = frag[:-1]

        subdir = ''
        if frag:
            subdir = os.path.join(*frag)

        return category, subdir, package, version
