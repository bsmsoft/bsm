import os
import copy
import datetime
import traceback

from bsm.env import Env

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util import safe_mkdir

from bsm.logger import get_logger
_logger = get_logger()


class InstallExecutorError(Exception):
    pass


class Executor(object):
    def __init__(self, config):
        self.__config = config
        self.__init_env()
        self.__current_running = set()

    # Create independent env for installation
    def __init_env(self):
        self.__env = Env()
        self.__env.unload_packages()
        self.__env.unload_release()
        self.__env.unload_app()
        self.__env.load_app(self.__config['app'])
        self.__env.load_release(self.__config['scenario'], self.__config['release'])

    def param(self, vertex):
        ctg, subdir, pkg, version, step, sub_step = vertex

        par = {}

        par['category'] = ctg
        par['subdir'] = subdir
        par['package'] = pkg
        par['version'] = version
        par['step'] = step
        par['sub_step'] = sub_step

        pkg_install_cfg = self.__config['package_install'].package_install_config(ctg, subdir, pkg, version)

        step_info = pkg_install_cfg['step'][step][sub_step]
        par['action'] = step_info.get('handler')
        par['action_param'] = step_info.get('param')
        par['action_install'] = step_info.get('install', False)

        pkg_path = pkg_install_cfg['package_path']
        par['package_path'] = copy.deepcopy(pkg_path)
        par['log_file'] = os.path.join(pkg_path['log_dir'], '{0}_{1}_{2}.log'.format(pkg, step, sub_step))
        par['env'] = copy.deepcopy(self.__env.env_final())

        par['config_package'] = copy.deepcopy(pkg_install_cfg['config'])
        par['config_app'] = self.__config['app'].data_copy()
        par['config_output'] = self.__config['output'].data_copy()
        par['config_scenario'] = self.__config['scenario'].data_copy()
        par['config_release_path'] = self.__config['release_path'].data_copy()
        par['config_attribute'] = self.__config['attribute'].data_copy()
        par['config_release'] = self.__config['release'].data_copy()
        par['config_category'] = self.__config['category'].data_copy()
        par['config_package_install_path'] = self.__config['package_install_path'].data_copy()

        return par

    # This method must be thread safe
    # Do NOT access or modify any variables outside this function (global and member variables)
    # All parameters are passed by "param" argument
    def execute(self, param):
        pkg = param['package']
        step = param['step']
        sub_step = param['sub_step']

        if sub_step == 0:
            step_full_name = '{0} - {1}'.format(pkg, step)
        else:
            step_full_name = '{0} - {1} - {2}'.format(pkg, step, sub_step)

        if not param['action_install']:
            _logger.debug('Skip step: {0}'.format(step_full_name))
            return {'success': True, 'skip': True}

        result = {}

        result['start'] = datetime.datetime.utcnow()

        safe_mkdir(os.path.dirname(param['log_file']))

        try:
            with Handler() as h:
                result_action = h.run('install', param)
        except HandlerNotFoundError as e:
            _logger.error('Install handler not found for "{0}"'.format(step_full_name))
            raise
        except Exception as e:
            _logger.error('"{0}" install handler error: {1}'.format(step_full_name, e))
            if param['config_output']['verbose']:
                _logger.error('\n{0}'.format(traceback.format_exc()))
            raise

        if isinstance(result_action, bool):
            result['success'] = result_action
        elif isinstance(result_action, dict):
            result['success'] = result_action.get('success', False)
        else:
            result['success'] = False

        if not result['success']:
            if isinstance(result_action, dict) and 'message' in result_action:
                _logger.error('"{0}" execution error: {1}'.format(step_full_name, result_action['message']))
            _logger.error('"{0}" execution error. Find log in "{1}"'.format(step_full_name, param['log_file']))
            raise InstallExecutorError('"{0}" execution error'.format(step_full_name))

        result['action'] = result_action
        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def report_finish(self, vertice_result):
        steps = self.__config['release_install']['steps']
        atomic_start = self.__config['release_install']['atomic_start']
        atomic_end = self.__config['release_install']['atomic_end']

        for vertex, result in vertice_result:
            ctg, subdir, pkg, version, step, sub_step = vertex

            pkg_install_cfg = self.__config['package_install'].package_install_config(ctg, subdir, pkg, version)

            if step == atomic_end and sub_step == (len(pkg_install_cfg['step'][step]) - 1):
                _logger.debug('Load package env for {0}'.format(pkg))
                self.__env.load_package(pkg_install_cfg['config'])

            if result['success']:
                if not result.get('skip'):
                    _logger.info(' > {0} {1} {2} finished'.format(pkg, step, sub_step))
                    if sub_step == (len(pkg_install_cfg['step'][step]) - 1):
                        _logger.debug('Save install status for {0}'.format(pkg))
                        pkg_install_cfg['install_status'].setdefault('steps', {})
                        pkg_install_cfg['install_status']['steps'][step] = {}
                        pkg_install_cfg['install_status']['steps'][step]['finished'] = True
                        pkg_install_cfg['install_status']['steps'][step]['start'] = result['start']
                        pkg_install_cfg['install_status']['steps'][step]['end'] = result['end']
                        self.__config['package_install'].save_install_status(ctg, subdir, pkg, version)
                if step == steps[-1] and sub_step == (len(pkg_install_cfg['step'][step]) - 1):
                    _logger.debug('Save package config for {0}'.format(pkg))
                    pkg_install_cfg['install_status']['finished'] = True
                    self.__config['package_install'].save_install_status(ctg, subdir, pkg, version)
                    self.__config['package_install'].save_package_config(ctg, subdir, pkg, version)

    def report_running(self, vertice):
        if not vertice:
            return

        new_running = set()
        for v in vertice:
            ctg, subdir, pkg, version, step, sub_step = v
            pkg_install_cfg = self.__config['package_install'].package_install_config(ctg, subdir, pkg, version)
            if not pkg_install_cfg['step'][step][sub_step].get('install'):
                continue
            new_running.add(v)

        if new_running == self.__current_running:
            return

        self.__current_running = new_running

        running_vertice = []
        for v in self.__current_running:
            ctg, subdir, pkg, version, step, sub_step = v
            if sub_step == 0:
                step_full_name = '{2}({4})'
            else:
                step_full_name = '{2}({4}.{5})'
            running_vertice.append(step_full_name.format(*v))
        _logger.info('Running: ' + ', '.join(running_vertice))

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
