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

        self.__prepare_packages()

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
                exe_config['source_dir'] = os.path.join(package_root, package_version, location['source'])
                exe_config['build_dir'] = os.path.join(package_root, package_version, location['build'])
                exe_config['install_dir'] = os.path.join(package_root, package_version, location['install'])

                safe_mkdir(exe_config['package_root'])
                safe_mkdir(exe_config['log_dir'])
                safe_mkdir(exe_config['download_dir'])
                safe_mkdir(exe_config['extract_dir'])
                safe_mkdir(exe_config['source_dir'])
                safe_mkdir(exe_config['build_dir'])
                safe_mkdir(exe_config['install_dir'])

            self.__exe_config[pkg] = exe_config

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

        par['pkg_config'] = self.__exe_config[pkg]

        return par

    def execute(self, param):
        status_file = os.path.join(self.__version_config['release_status_root'], 'status.yml')
        try:
            status_info = load_config(status_file)
        except:
            status_info = {}

        pkg = param['package']
        action = param['action']
        if pkg in status_info and action in status_info[pkg] and \
                'finished' in status_info[pkg][action] and status_info[pkg][action]['finished']:
            print('::::::::::: not doing: {0} {1}'.format(pkg, action))
            return None


        result = {}

        result['start'] = datetime.datetime.utcnow()

        f = load_func('cepcenv_handler_run_avoid_conflict.{0}'.format(param['action_handler']), param['action'])
        result['action'] = f(param)

        result['end'] = datetime.datetime.utcnow()

        return result

    def report_start(self, vertice):
        pass

    def report_finish(self, vertice_result):
        for vertex, result in vertice_result:
            pkg, action = vertex

            if result and result['action']:
                print('Package "{0}" {1} finished with result'.format(pkg, action))

                if 'log' in result['action']:
                    log_dir = self.__exe_config[pkg]['log_dir']
                    with open(os.path.join(log_dir, action+'.out'), 'w') as f:
                        f.write(result['action']['log']['stdout'])
                    with open(os.path.join(log_dir, action+'.err'), 'w') as f:
                        f.write(result['action']['log']['stderr'])


                status_file = os.path.join(self.__version_config['release_status_root'], 'status.yml')
                try:
                    status_info = load_config(status_file)
                except:
                    status_info = {}

                if pkg not in status_info:
                    status_info[pkg] = {}
                if action not in status_info[pkg]:
                    status_info[pkg][action] = {}
                status_info[pkg][action]['finished'] = True
                status_info[pkg][action]['start'] = result['start']
                status_info[pkg][action]['end'] = result['end']

                dump_config(status_info, status_file)

    def report_running(self, vertice):
        if not vertice:
            return
        running_vertice = ', '.join(['{0}({1})'.format(*v) for v in vertice])
        print('Running: ' + running_vertice)

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
