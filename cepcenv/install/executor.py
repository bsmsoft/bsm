import os
import datetime

from cepcenv.env import Env
from cepcenv.package_manager import PackageManager

from cepcenv.loader import load_func
from cepcenv.util import safe_mkdir

from cepcenv.config.config_version import HANDLER_MODULE_NAME

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
        handler = self.__pkg_mgr.package_info(pkg)['install'].get(action, {}).get('handler')
        if handler:
            par['action_handler'] = handler
            par['action_param'] = self.__pkg_mgr.package_info(pkg)['install'][action].get('param', {})

        par['config'] = self.__config

        par['def_dir'] = self.__config_version.def_dir

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

        safe_mkdir(param['pkg_info']['dir']['log'])

        module_name = HANDLER_MODULE_NAME + '.install.' + param['action_handler']
        f = load_func(module_name, 'run')
        result_action = f(param)

        if result_action is not None and not result_action:
            _logger.critical('"{0} - {1}" execution error. Find log in "{2}"'.format(pkg, action, param['log_file']))
            raise InstallExecutorError('"{0} - {1}" execution error'.format(pkg, action))

        result['log_file'] = param['log_file']
        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def report_finish(self, vertice_result):
        for vertex, result in vertice_result:
            pkg, action = vertex

            # TODO: post_compile may be absent, find out a secure way
            if action == 'post_compile':
                path_usage = self.__config_release.config['setting'].get('path_usage', {})
                pkg_info = self.__pkg_mgr.package_info(pkg)
                self.__env.set_package(path_usage, pkg_info)

            if result:
                _logger.info(' > {0} {1} finished'.format(pkg, action))
                safe_mkdir(self.__pkg_mgr.package_info(pkg)['dir']['status'])
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
