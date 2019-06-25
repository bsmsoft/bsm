import copy

from bsm.env import Env

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.operation import Base

class CheckMissing(Base):
    def execute(self, check_type):
        env = Env(initial_env=self._env.env_final(), env_prefix=self._config['app']['env_prefix'])
        env.unload_packages()
        env.unload_release()
        env.unload_app()
        env.load_app(self._config['app'])
        env.load_release(self._config['scenario'], self._config['option'], self._config['release'])

        missing = {}

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            for category in self._config['package_check']:
                for package, value in self._config['package_check'][category].items():
                    if not self.__check_package(h, env.env_final(), value['config'], check_type):
                        missing.setdefault(package, [])
                        missing[package].append(category)

            self.__check_summary(h, missing, check_type)

        return missing

    def __check_package(self, handler, env, config_package, check_type):
        param = {}

        param['env'] = env.copy()
        param['type'] = check_type

        param['config_package'] = copy.deepcopy(config_package)

        param['config_app'] = self._config['app'].data_copy()
        param['config_output'] = self._config['output'].data_copy()
        param['config_scenario'] = self._config['scenario'].data_copy()
        param['config_option'] = self._config['option'].data_copy()
        param['config_release_path'] = self._config['release_path'].data_copy()
        param['config_attribute'] = self._config['attribute'].data_copy()
        param['config_release'] = self._config['release'].data_copy()
        param['config_category'] = self._config['category'].data_copy()
        param['config_category_priority'] = self._config['category_priority'].data_copy()
        param['config_package_check'] = self._config['package_check'].data_copy()

        try:
            return handler.run('check.package', param)
        except HandlerNotFoundError:
            _logger.debug('Check package handler not found')

        return True

    def __check_summary(self, handler, missing, check_type):
        param = {}

        param['type'] = check_type
        param['missing_package'] = missing

        param['config_app'] = self._config['app'].data_copy()
        param['config_output'] = self._config['output'].data_copy()
        param['config_scenario'] = self._config['scenario'].data_copy()
        param['config_option'] = self._config['option'].data_copy()
        param['config_release_path'] = self._config['release_path'].data_copy()
        param['config_attribute'] = self._config['attribute'].data_copy()
        param['config_release'] = self._config['release'].data_copy()
        param['config_category'] = self._config['category'].data_copy()
        param['config_category_priority'] = self._config['category_priority'].data_copy()
        param['config_package_check'] = self._config['package_check'].data_copy()

        try:
            return handler.run('check.summary', param)
        except HandlerNotFoundError:
            _logger.debug('Check summary handler not found')
