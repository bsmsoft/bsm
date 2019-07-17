import copy

from bsm.env import Env

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class CheckMissing(Base):
    def execute(self, check_type):
        env = Env(initial_env=self._env.env_final(), env_prefix=self._prop['app']['env_prefix'])
        env.unload_packages()
        env.unload_release()
        env.unload_app()
        env.load_app(self._prop['app'])
        env.load_release(self._prop['scenario'],
                         self._prop['option_release'], self._prop['release_setting'])

        missing = {}

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            for category in self._prop['packages_check']:
                for package, value in self._prop['packages_check'][category].items():
                    if not self.__check_package(h, env.env_final(), value['prop'], check_type):
                        missing.setdefault(package, [])
                        missing[package].append(category)

            self.__check_summary(h, missing, check_type)

        return missing

    def __check_package(self, handler, env, pkg_prop, check_type):
        param = {}

        param['env'] = env.copy()
        param['type'] = check_type

        param['prop'] = copy.deepcopy(pkg_prop)

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority',
                'packages_check']:
            param['prop_'+n] = self._prop[n].data_copy()

        try:
            return handler.run('check.package', param)
        except HandlerNotFoundError:
            _logger.debug('Check package handler not found')

        return True

    def __check_summary(self, handler, missing, check_type):
        param = {}

        param['type'] = check_type
        param['missing_package'] = missing

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority',
                'packages_check']:
            param['prop_'+n] = self._prop[n].data_copy()

        try:
            return handler.run('check.summary', param)
        except HandlerNotFoundError:
            _logger.debug('Check summary handler not found')
