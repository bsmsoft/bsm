import os
import time
import random
import datetime

from cepcenv.env import Env
from cepcenv.package_manager import PackageManager

from cepcenv.loader import load_func
from cepcenv.util import safe_mkdir

from cepcenv.config import load_config
from cepcenv.config import dump_config

from cepcenv.logger import get_logger
_logger = get_logger()


class InstallExecutorError(Exception):
    pass


class Executor(object):
    def __init__(self, config, config_version, config_release):
        self.__config = config
        self.__config_version = config_version
        self.__config_release = config_release

        self.__env = Env()
        self.__env.clean()

        self.__pkg_mgr = PackageManager(config_version, config_release)

    def param(self, vertex):
        pkg, action = vertex

        par = {}

        par['package'] = pkg
        par['action'] = action
        if pkg in self.__config_release.config['install'] and action in self.__config_release.config['install'][pkg]:
            par['action_handler'] = self.__config_release.config['install'][pkg][action].get('handler', 'default')
            par['action_param'] = self.__config_release.config['install'][pkg][action].get('param', {})

        par['config'] = self.__config

        par['pkg_info'] = self.__pkg_mgr.package_info(pkg)

        par['pkg_dir_list'] = self.__pkg_mgr.package_dir_list()

        par['log_file'] = os.path.join(self.__pkg_mgr.package_info(pkg)['dir']['log'], '{0}_{1}.log'.format(action, pkg))

        par['env'] = self.__env.env_final()

        par['finished'] = self.__pkg_mgr.is_ready(pkg, action)

        return par

    # Do NOT access or modify any variables outside this function (global and member variables)
    def execute(self, param):
        pkg = param['package']
        action = param['action']

        if 'action_handler' not in param:
            _logger.debug('No handler: {0} - {1}'.format(pkg, action))
            return None

        if param['finished']:
            _logger.debug('Skip doing: {0} - {1}'.format(pkg, action))
            return None

        result = {}

        result['start'] = datetime.datetime.utcnow()

        f = load_func('_cepcenv_handler_run_avoid_conflict.'+param['action_handler'], 'run')
        result_action = f(param)
        if result_action is not None and not result_action:
            _logger.critical('"{0} - {1}" execution error. Find log in "{2}"'.format(pkg, action, param['log_file']))
            raise InstallExecutorError('"{0} - {1}" execution error'.format(pkg, action))

        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def __setup_env(self, pkg):
        if pkg not in self.__config_release.config['attribute']:
            return

        PATH_NAME = {'bin': 'PATH', 'library': 'LD_LIBRARY_PATH', 'man': 'MANPATH', 'info': 'INFOPATH', 'cmake': 'CMAKE_PREFIX_PATH'}
        if 'path' in self.__config_release.config['attribute'][pkg]:
            for k, v in self.__config_release.config['attribute'][pkg]['path'].items():
                if k in PATH_NAME:
                    path_env_name = PATH_NAME[k]
                    if path_env_name not in self.__extra_path:
                        self.__extra_path[path_env_name] = []
                    full_path = v.format(**self.__exe_config[pkg])
                    if full_path not in self.__extra_path[path_env_name]:
                        self.__extra_path[path_env_name].append(full_path)

        if 'env' in self.__config_release.config['attribute'][pkg]:
            for k, v in self.__config_release.config['attribute'][pkg]['env'].items():
                self.__extra_env[k] = v.format(**self.__exe_config[pkg])

    def report_finish(self, vertice_result):
        for vertex, result in vertice_result:
            pkg, action = vertex

            # TODO: post_compile may be absent, find out a secure way
            if action == 'post_compile':
                path_usage = self.__config_release.config['setting'].get('path_usage', {})
                pkg_info = self.__pkg_mgr.package_info(pkg)
                self.__env.set_package(path_usage, pkg_info)

            if result:
                _logger.info('Package "{0} - {1}" finished'.format(pkg, action))
                self.__pkg_mgr.save_action_status(pkg, action, result['start'], result['end'])

    def report_running(self, vertice):
        if not vertice:
            return
        running_vertice = ', '.join(['{0}({1})'.format(*v) for v in vertice])
        _logger.info('Running: ' + running_vertice)

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
