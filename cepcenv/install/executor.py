import os
import time
import random
import datetime

from cepcenv.loader import load_func
from cepcenv.logger import get_logger
from cepcenv.util import safe_mkdir

from cepcenv.config import load_config
from cepcenv.config import dump_config


_logger = get_logger()


class InstallExecutorError(Exception):
    pass


class Executor(object):
    def __init__(self, config, config_version, config_release):
        self.__config = config
        self.__config_version = config_version
        self.__config_release = config_release

        self.__prepare_packages()
        self.__package_path()

        self.__extra_path = {}
        self.__extra_env = {}

    def __load_install_status(self, pkg, action):
        if 'status_dir' not in self.__exe_config[pkg]:
            return {}

        status_file = os.path.join(self.__exe_config[pkg]['status_dir'], 'install.yml')

        try:
            install_status = load_config(status_file)
            if not isinstance(install_status, dict):
                return {}
            return install_status
        except:
            return {}

    def __is_ready(self, pkg, action):
        install_status = self.__load_install_status(pkg, action)
        return action in install_status and \
                'finished' in install_status[action] and \
                install_status[action]['finished']

    def __save_action_status(self, pkg, action, start, end):
        if 'status_dir' not in self.__exe_config[pkg]:
            return

        install_status = self.__load_install_status(pkg, action)

        if action not in install_status:
            install_status[action] = {}
        install_status[action]['finished'] = True
        install_status[action]['start'] = start
        install_status[action]['end'] = end

        status_file = os.path.join(self.__exe_config[pkg]['status_dir'], 'install.yml')
        dump_config(install_status, status_file)

    def __prepare_packages(self):
        self.__exe_config = {}

        for pkg, cfg in self.__config_release.config['package'].items():
            exe_config = {}

            package_version = cfg.get('version')
            exe_config['version'] = package_version

            package_root = self.__config_release.package_root(pkg)
            if package_root:
                exe_config['package_root'] = package_root

                location = self.__config_release.config['attribute'][pkg]['location']
                exe_config['status_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'status')
                exe_config['log_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'log')
                exe_config['download_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'download')
                exe_config['extract_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'extract')
                exe_config['source_dir'] = os.path.join(package_root, package_version, location['source']).rstrip(os.sep)
                exe_config['build_dir'] = os.path.join(package_root, package_version, location['build']).rstrip(os.sep)
                exe_config['install_dir'] = os.path.join(package_root, package_version, location['install']).rstrip(os.sep)

                safe_mkdir(exe_config['package_root'])
                safe_mkdir(exe_config['status_dir'])
                safe_mkdir(exe_config['log_dir'])
                safe_mkdir(exe_config['download_dir'])
                safe_mkdir(exe_config['extract_dir'])
                safe_mkdir(exe_config['source_dir'])
                safe_mkdir(exe_config['build_dir'])
                safe_mkdir(exe_config['install_dir'])

            self.__exe_config[pkg] = exe_config

    def __package_path(self):
        self.__pkg_path = {}
        for pkg in self.__config_release.config['package']:
            if pkg not in self.__config_release.config['attribute']:
                continue

            pkg_root_key = pkg.lower() + '_root_dir'
            self.__pkg_path[pkg_root_key] = self.__exe_config[pkg]['install_dir']

            if 'path' not in self.__config_release.config['attribute'][pkg]:
                continue
            for k, v in self.__config_release.config['attribute'][pkg]['path'].items():
                if k not in ['bin', 'inc', 'lib']:
                    continue
                path_key = '{0}_{1}_dir'.format(pkg.lower(), k)
                self.__pkg_path[path_key] = v.format(**self.__exe_config[pkg])

    def param(self, vertex):
        pkg, action = vertex

        par = {}

        par['package'] = pkg
        par['action'] = action
        if action in self.__config_release.config['install'][pkg]:
            par['action_handler'] = self.__config_release.config['install'][pkg][action].get('handler', 'default')
            par['action_param'] = self.__config_release.config['install'][pkg][action].get('param', {})
        else:
            par['action_handler'] = 'default'
            par['action_param'] = {}

        par['config'] = self.__config

        par['pkg_config'] = self.__exe_config[pkg]

        par['pkg_path'] = self.__pkg_path

        # Make a copy in order to avoid change of extra_env when action executing
        env_final = os.environ.copy()
        env_final.update(self.__extra_env)
        for k, v in self.__extra_path.items():
            env_final[k] = os.pathsep.join(v)
            if k in os.environ:
                env_final[k] += (os.pathsep + os.environ[k])
        par['env'] = env_final

        par['finished'] = self.__is_ready(pkg, action)

        return par

    # Do NOT access or modify any variables outside this function (global and member variables)
    def execute(self, param):
        pkg = param['package']
        action = param['action']

        if param['finished']:
            _logger.debug('Skip doing: {0} {1}'.format(pkg, action))
            return None

        result = {}

        result['start'] = datetime.datetime.utcnow()

        f = load_func('_cepcenv_handler_run_avoid_conflict.'+param['action_handler'], param['action'])
        result_action = f(param)
        if result_action is not None and not result_action:
            _logger.critical('{0}.{1} execution error. Find log in "{2}"'.format(pkg, action, param['pkg_config']['log_dir']))
            raise InstallExecutorError('{0}.{1} execution error'.format(pkg, action))

        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def __setup_env(self, pkg):
        if pkg not in self.__config_release.config['attribute']:
            return

        PATH_NAME = {'bin': 'PATH', 'lib': 'LD_LIBRARY_PATH', 'man': 'MANPATH', 'info': 'INFOPATH', 'cmake': 'CMAKE_PREFIX_PATH'}
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

            # TODO: post_check may be absent, find out a secure way
            if action == 'post_check':
                self.__setup_env(pkg)

            if result:
                _logger.info('Package "{0}" {1} finished'.format(pkg, action))
                self.__save_action_status(pkg, action, result['start'], result['end'])

    def report_running(self, vertice):
        if not vertice:
            return
        running_vertice = ', '.join(['{0}({1})'.format(*v) for v in vertice])
        _logger.info('Running: ' + running_vertice)

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
