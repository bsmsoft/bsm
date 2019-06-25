import copy

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class BuildPackage(Base):
    def execute(self, package, category, subdir, version, rebuild=False):
        pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)

        param = {}
        param['type'] = 'rebuild' if rebuild else 'build'

        param['name'] = package
        param['category'] = category
        param['subdir'] = subdir
        param['version'] = version

        param['config_package'] = copy.deepcopy(pkg_cfg['config'])
        param['package_path'] = copy.deepcopy(pkg_cfg['package_path'])

        param['config_app'] = self._config['app'].data_copy()
        param['config_output'] = self._config['output'].data_copy()
        param['config_scenario'] = self._config['scenario'].data_copy()
        param['config_option'] = self._config['option'].data_copy()
        param['config_release_path'] = self._config['release_path'].data_copy()
        param['config_attribute'] = self._config['attribute'].data_copy()
        param['config_release'] = self._config['release'].data_copy()
        param['config_category'] = self._config['category'].data_copy()
        param['config_category_priority'] = self._config['category_priority'].data_copy()
        param['config_package_runtime'] = self._config['package_runtime'].data_copy()
        param['config_package_runtime_path'] = self._config['package_runtime_path'].data_copy()

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            try:
                return h.run('build_package', param)
            except HandlerNotFoundError as e:
                _logger.error('Could not find out how to build package "{0}", category "{1}", subdir "{2}", version "{3}"'.format(package, category, subdir, version))
                raise
