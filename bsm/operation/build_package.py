import copy

from bsm.handler import Handler

from bsm.operation import Base


class BuildPackageError(Exception):
    pass


class BuildPackage(Base):
    def execute(self, package, category, subdir, version):
        pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)['config']

        param = {}
        param['name'] = package
        param['category'] = category
        param['subdir'] = subdir
        param['version'] = version

        param['config_package'] = copy.deepcopy(pkg_cfg)
        param['config_app'] = self.__config['app'].data_copy()
        param['config_output'] = self.__config['output'].data_copy()
        param['config_scenario'] = self.__config['scenario'].data_copy()
        param['config_option'] = self.__config['option'].data_copy()
        param['config_release_path'] = self.__config['release_path'].data_copy()
        param['config_attribute'] = self.__config['attribute'].data_copy()
        param['config_release'] = self.__config['release'].data_copy()
        param['config_category'] = self.__config['category'].data_copy()
        param['config_package_runtime'] = self.__config['package_runtime'].data_copy()
        param['config_package_runtime_path'] = self.__config['package_runtime_path'].data_copy()

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            return h.run('build_package', category, subdir, package, version)
