import os
import copy
import datetime
import traceback

from bsm.error import OperationInstallExecutorError

from bsm.env import Env

from bsm.handler import Handler
from bsm.handler import HandlerNotFoundError

from bsm.util import safe_mkdir

from bsm.logger import get_logger
_logger = get_logger()


class InstallExecutorError(Exception):
    pass


class Executor(object):
    def __init__(self, prop, initial_env, run_type='install'):
        self.__prop = prop
        self.__env = Env(initial_env=initial_env,
                         env_prefix=self.__prop['app']['env_prefix'])
        self.__current_running = set()

        self.__run_type = run_type
        if run_type == 'runtime':
            self.__prop_packages_name = 'packages_runtime'
        else:
            self.__prop_packages_name = 'packages_install'

    def param(self, vertex):
        ctg, subdir, pkg, version, step, sub_step = vertex

        par = {}

        par['category'] = ctg
        par['subdir'] = subdir
        par['package'] = pkg
        par['version'] = version
        par['step'] = step
        par['sub_step'] = sub_step

        pkg_props = self.__prop[self.__prop_packages_name].package_props(
            ctg, subdir, pkg, version)

        step_info = pkg_props['step'][step][sub_step]
        par['action'] = step_info.get('handler')
        par['action_param'] = step_info.get('param')
        par['action_install'] = step_info.get('install', False)

        pkg_path = pkg_props['package_path']
        par['package_path'] = copy.deepcopy(pkg_path)
        par['log_file'] = os.path.join(
            pkg_path['log_dir'], '{0}_{1}_{2}.log'.format(pkg, step, sub_step))
        par['env'] = copy.deepcopy(self.__env.env_final())

        par['prop'] = copy.deepcopy(pkg_props['prop'])

        for n in [
                'app', 'output', 'scenario', 'option_release', 'release_path', 'attribute',
                'release_setting', 'release_package', 'category', 'category_priority']:
            par['prop_'+n] = self.__prop[n].data_copy()

        par['prop_packages'] = self.__prop[self.__prop_packages_name].data_copy()
        par['prop_packages_path'] = self.__prop[self.__prop_packages_name +
                                                '_path'].data_copy()

        return par

    # This method must be thread safe
    # Do NOT access or modify any variables outside this function (global and member variables)
    # All parameters are passed by "param" argument
    def execute(self, param):   # pylint: disable=no-self-use
        pkg = param['package']
        step = param['step']
        sub_step = param['sub_step']

        if sub_step == 0:
            step_full_name = '{0} - {1}'.format(pkg, step)
        else:
            step_full_name = '{0} - {1} - {2}'.format(pkg, step, sub_step)

        if not param['action_install']:
            _logger.debug('Skip step: %s', step_full_name)
            return {'success': True, 'skip': True}

        result = {}

        result['start'] = datetime.datetime.utcnow()

        safe_mkdir(os.path.dirname(param['log_file']))

        try:
            with Handler() as h:
                result_action = h.run('install', param)
        except HandlerNotFoundError as e:
            _logger.error('Install handler "%s" not found for "%s"',
                          param['action'], step_full_name)
            raise
        except Exception as e:
            _logger.error('Install handler "%s" error for %s: %s',
                          param['action'], step_full_name, e)
            if param['prop_output']['verbose']:
                _logger.error('\n%s', traceback.format_exc())
            raise

        if isinstance(result_action, bool):
            result['success'] = result_action
        elif isinstance(result_action, dict):
            result['success'] = result_action.get('success', False)
        else:
            result['success'] = False

        if not result['success']:
            if isinstance(result_action, dict) and 'message' in result_action:
                _logger.error('"%s" execution error: %s',
                              step_full_name, result_action['message'])
            _logger.error('"%s" execution error. Find log in "%s"',
                          step_full_name, param['log_file'])
            raise OperationInstallExecutorError(
                '"{0}" execution error'.format(step_full_name))

        result['action'] = result_action
        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def report_finish(self, vertice_result):
        steps = self.__prop['release_install']['steps']
        atomic_end = self.__prop['release_install']['atomic_end']

        for vertex, result in vertice_result:
            ctg, subdir, pkg, version, step, sub_step = vertex

            pkg_props = self.__prop[self.__prop_packages_name].package_props(
                ctg, subdir, pkg, version)

            if step == atomic_end and sub_step == (len(pkg_props['step'][step]) - 1):
                _logger.debug('Load package env for %s', pkg)
                self.__env.load_package(pkg_props['prop'])

            if result['success']:
                if not result.get('skip'):
                    _logger.info(' > %s %s %s finished', pkg, step, sub_step)
                    if sub_step == (len(pkg_props['step'][step]) - 1):
                        _logger.debug(
                            'Save install status for %s - %s', pkg, step)
                        pkg_props['install_status'].setdefault('steps', {})
                        pkg_props['install_status']['steps'][step] = {}
                        pkg_props['install_status']['steps'][step]['finished'] = True
                        pkg_props['install_status']['steps'][step]['start'] = result['start']
                        pkg_props['install_status']['steps'][step]['end'] = result['end']
                        self.__prop[self.__prop_packages_name].save_install_status(
                            ctg, subdir, pkg, version)
                if step == steps[-1] and sub_step == (len(pkg_props['step'][step]) - 1):
                    if not pkg_props['install_status'].get('finished'):
                        pkg_props['install_status']['finished'] = True
                        self.__prop[self.__prop_packages_name].save_install_status(
                            ctg, subdir, pkg, version)
                        if self.__run_type == 'install':
                            _logger.debug('Save package prop for %s', pkg)
                            self.__prop[self.__prop_packages_name].save_package_prop(
                                ctg, subdir, pkg, version)

    def report_running(self, vertice):
        if not vertice:
            return

        new_running = set()
        for v in vertice:
            ctg, subdir, pkg, version, step, sub_step = v
            pkg_props = self.__prop[self.__prop_packages_name].package_props(
                ctg, subdir, pkg, version)
            if not pkg_props['step'][step][sub_step].get('install'):
                continue
            new_running.add(v)

        if new_running == self.__current_running or not new_running:
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
        _logger.info('Running: %s', ', '.join(running_vertice))

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
