import os
import time
import random
import datetime

from cepcenv.loader import load_func

from cepcenv.config.util import load_config
from cepcenv.config.util import dump_config

from cepcenv.util import safe_mkdir

class Executor(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

        self.__load_status_info()
        self.__prepare_packages()
        self.__package_path()

        self.__extra_path = {}
        self.__extra_env = {}

    def __load_status_info(self):
        status_file = os.path.join(self.__version_config['release_status_root'], 'status.yml')
        try:
            self.__status_info = load_config(status_file)
            if not isinstance(self.__status_info, dict):
                self.__status_info = {}
        except:
            self.__status_info = {}

    def __prepare_packages(self):
        self.__exe_config = {}
        for pkg, cfg in self.__release_config['package'].items():
            exe_config = {}

            package_version = cfg.get('version')
            exe_config['version'] = package_version

            if (cfg['category']+'_root') in self.__version_config:
                package_root = os.path.join(self.__version_config[cfg['category']+'_root'], cfg['path'], pkg)
                exe_config['package_root'] = package_root

                location = self.__release_config['attribute'][pkg]['location']
                exe_config['log_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'log')
                exe_config['download_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'download')
                exe_config['extract_dir'] = os.path.join(package_root, '_cepcenv', package_version, 'extract')
                exe_config['source_dir'] = os.path.join(package_root, package_version, location['source']).rstrip(os.sep)
                exe_config['build_dir'] = os.path.join(package_root, package_version, location['build']).rstrip(os.sep)
                exe_config['install_dir'] = os.path.join(package_root, package_version, location['install']).rstrip(os.sep)

                safe_mkdir(exe_config['package_root'])
                safe_mkdir(exe_config['log_dir'])
                safe_mkdir(exe_config['download_dir'])
                safe_mkdir(exe_config['extract_dir'])
                safe_mkdir(exe_config['source_dir'])
                safe_mkdir(exe_config['build_dir'])
                safe_mkdir(exe_config['install_dir'])

            self.__exe_config[pkg] = exe_config

    def __package_path(self):
        self.__pkg_path = {}
        for pkg in self.__release_config['package']:
            if pkg not in self.__release_config['attribute']:
                continue

            pkg_root_key = pkg.lower() + '_root_dir'
            self.__pkg_path[pkg_root_key] = self.__exe_config[pkg]['install_dir']

            if 'path' not in self.__release_config['attribute'][pkg]:
                continue
            for k, v in self.__release_config['attribute'][pkg]['path'].items():
                if k not in ['bin', 'inc', 'lib']:
                    continue
                path_key = '{0}_{1}_dir'.format(pkg.lower(), k)
                self.__pkg_path[path_key] = v.format(**self.__exe_config[pkg])

    def param(self, vertex):
        pkg, action = vertex

        par = {}

        par['package'] = pkg
        par['action'] = action
        if action in self.__release_config['install'][pkg]:
            par['action_handler'] = self.__release_config['install'][pkg][action].get('handler', 'default')
            par['action_param'] = self.__release_config['install'][pkg][action].get('param', {})
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

        par['finished'] = False
        if pkg in self.__status_info and action in self.__status_info[pkg] and \
                'finished' in self.__status_info[pkg][action] and self.__status_info[pkg][action]['finished']:
            par['finished'] = True

        return par

    # Do NOT access or modify any variables outside this function (global and member variables)
    def execute(self, param):
        pkg = param['package']
        action = param['action']

        if param['finished']:
            print('Skip doing: {0} {1}'.format(pkg, action))
            return None

        result = {}

        result['start'] = datetime.datetime.utcnow()

        f = load_func('_cepcenv_handler_run_avoid_conflict.'+param['action_handler'], param['action'])
        result['action'] = f(param)

        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def __setup_env(self, pkg):
        if pkg not in self.__release_config['attribute']:
            return

        PATH_NAME = {'bin': 'PATH', 'lib': 'LD_LIBRARY_PATH', 'man': 'MANPATH', 'info': 'INFOPATH', 'cmake': 'CMAKE_PREFIX_PATH'}
        if 'path' in self.__release_config['attribute'][pkg]:
            for k, v in self.__release_config['attribute'][pkg]['path'].items():
                if k in PATH_NAME:
                    path_env_name = PATH_NAME[k]
                    if path_env_name not in self.__extra_path:
                        self.__extra_path[path_env_name] = []
                    full_path = v.format(**self.__exe_config[pkg])
                    if full_path not in self.__extra_path[path_env_name]:
                        self.__extra_path[path_env_name].append(full_path)

        if 'env' in self.__release_config['attribute'][pkg]:
            for k, v in self.__release_config['attribute'][pkg]['env'].items():
                self.__extra_env[k] = v.format(**self.__exe_config[pkg])

    def report_finish(self, vertice_result):
        for vertex, result in vertice_result:
            pkg, action = vertex

            # TODO: post_check may be absent, find out a secure way
            if action == 'post_check':
                self.__setup_env(pkg)

            if result and result['action']:
                print('Package "{0}" {1} finished'.format(pkg, action))

                if 'log' in result['action']:
                    log_dir = self.__exe_config[pkg]['log_dir']
                    with open(os.path.join(log_dir, action+'.out'), 'w') as f:
                        f.write(result['action']['log']['stdout'])
                    with open(os.path.join(log_dir, action+'.err'), 'w') as f:
                        f.write(result['action']['log']['stderr'])


            if result:
                if pkg not in self.__status_info:
                    self.__status_info[pkg] = {}
                if action not in self.__status_info[pkg]:
                    self.__status_info[pkg][action] = {}
                self.__status_info[pkg][action]['finished'] = True
                self.__status_info[pkg][action]['start'] = result['start']
                self.__status_info[pkg][action]['end'] = result['end']

                status_file = os.path.join(self.__version_config['release_status_root'], 'status.yml')
                dump_config(self.__status_info, status_file)

    def report_running(self, vertice):
        if not vertice:
            return
        running_vertice = ', '.join(['{0}({1})'.format(*v) for v in vertice])
        print('Running: ' + running_vertice)

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
