import copy

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class BuildPackage(Base):
    def execute(self, package, category, subdir, version, rebuild=False):
        pkg_props = self._prop['packages_runtime'].package_props(category, subdir, package, version)

        param = {}
        param['type'] = 'rebuild' if rebuild else 'build'

        param['name'] = package
        param['category'] = category
        param['subdir'] = subdir
        param['version'] = version

        param['prop_package'] = copy.deepcopy(pkg_props['prop'])
        param['package_path'] = copy.deepcopy(pkg_props['package_path'])

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority',
                'packages_runtime', 'packages_runtime_path']:
            param['prop_'+n] = self._prop[n].data_copy()

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            try:
                return h.run('build_package', param)
            except HandlerNotFoundError:
                _logger.error(
                    'Could not find out how to build '
                    'package "%s", category "%s", subdir "%s", version "%s"',
                    package, category, subdir, version)
                raise
