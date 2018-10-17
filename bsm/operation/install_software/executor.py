import os
import copy
import datetime
import traceback

from bsm.env import Env
from bsm.package_manager import PackageManager

from bsm.loader import load_func
from bsm.util import safe_mkdir

from bsm import HANDLER_MODULE_NAME

from bsm.logger import get_logger
_logger = get_logger()


class InstallExecutorError(Exception):
    pass


class Executor(object):
    def __init__(self, config_user, config_version, config_release, step_info):
        self.__config_user = config_user
        self.__config_version = config_version
        self.__config_release = config_release
        self.__step_info = step_info

        # Create independent env for installation
        self.__env = Env()
        self.__env.clean()

        self.__pkg_mgr = PackageManager(config_version, config_release)

    def param(self, vertex):
        pkg, action, sub_action = vertex

        par = {}

        par['package'] = pkg
        par['action'] = action
        par['sub_action'] = sub_action

        step = self.__step_info.package_step(pkg, action, sub_action)
        par['action_handler'] = step.get('handler')
        par['action_param'] = step.get('param')

        par['log_file'] = os.path.join(self.__pkg_mgr.package_info(pkg)['dir']['log'], '{0}_{1}_{2}.log'.format(pkg, action, sub_action))
        par['env'] = copy.deepcopy(self.__env.env_final())

        par['config_user'] = copy.deepcopy(self.__config_user)
        par['def_dir'] = self.__config_version.def_dir
        par['pkg_info'] = copy.deepcopy(self.__pkg_mgr.package_info(pkg))
        par['pkg_dir_list'] = copy.deepcopy(self.__pkg_mgr.package_dir_list())

        return par

    # Do NOT access or modify any variables outside this function (global and member variables)
    def execute(self, param):
        pkg = param['package']
        action = param['action']
        sub_action = param['sub_action']

        if sub_action == 0:
            action_full_name = '{0} - {1}'.format(pkg, action)
        else:
            action_full_name = '{0} - {1} - {2}'.format(pkg, action, sub_action)

        result = {}

        result['start'] = datetime.datetime.utcnow()

        safe_mkdir(param['pkg_info']['dir']['log'])

        try:
            result_action = run_handler('install.'+param['action_handler'], param)
        except Exception as e:
            _logger.critical('"{0}" install handler error: {1}'.format(action_full_name, e))
            if param['config_user']['verbose']:
                _logger.critical('\n{0}'.format(traceback.format_exc()))
            raise

        result['success'] = False
        if isinstance(result_action, bool) and result_action:
            result['success'] = True
        if isinstance(result_action, dict) and 'success' in result_action and result_action['success']:
            result['success'] = True
        if not result['success']:
            if isinstance(result_action, dict) and 'message' in result_action:
                _logger.error('"{0}" execution error: {1}'.format(action_full_name, result_action['message']))
            _logger.critical('"{0}" execution error. Find log in "{1}"'.format(action_full_name, param['log_file']))
            raise InstallExecutorError('"{0}" execution error'.format(action_full_name))

        result['action'] = result_action
        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def report_finish(self, vertice_result):
        for vertex, result in vertice_result:
            pkg, action, sub_action = vertex

            if isinstance(result['action'], dict) and 'env_package' in result['action'] and result['action']['env_package']:
                path_def = self.__config_release.config['setting'].get('path_def', {})
                pkg_info = self.__pkg_mgr.package_info(pkg)
                self.__env.set_package(path_def, pkg_info)

            if isinstance(result['action'], dict) and 'save_release_status' in result['action'] and result['action']['save_release_status']:
                self.__pkg_mgr.save_release_status(pkg, result['end'])

            if result['success']:
                _logger.info(' > {0} {1} {2} finished'.format(pkg, action, sub_action))
                if self.__step_info.is_last_sub_action(pkg, action, sub_action):
                    self.__pkg_mgr.save_action_status(pkg, action, result['start'], result['end'])

    def report_running(self, vertice):
        if not vertice:
            return

        running_vertice = []
        for v in vertice:
            if v[2] == 0:
                action_full_name = '{0}({1})'
            else:
                action_full_name = '{0}({1}.{2})'
            running_vertice.append(action_full_name.format(*v))
        _logger.info('Running: ' + ', '.join(running_vertice))

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
