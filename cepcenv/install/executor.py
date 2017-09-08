import os
import time
import random

from cepcenv.loader import load_func

from cepcenv.util import safe_mkdir

class Executor(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

    def param(self, vertex):
        pkg, action = vertex

        par = {}

        par['action'] = action
        par['action_handler'] = self.__release_config['install'][pkg][action]['handler']
        par['action_param'] = self.__release_config['install'][pkg][action].get('param', {})

        # TODO: prepare pkg_config for each pkg only once
        par['pkg_config'] = {}

        category = self.__release_config['package'][pkg]['category']

        if category != 'system':
            package_version = self.__release_config['package'][pkg].get('version')
            par['pkg_config']['version'] = package_version

            package_root = os.path.join(self.__version_config[category+'_root'], self.__release_config['package'][pkg]['path'], pkg)
            par['pkg_config']['package_root'] = package_root

            par['pkg_config']['log_dir'] = os.path.join(package_root, '.cepcenv', package_version, 'log')
            par['pkg_config']['download_dir'] = os.path.join(package_root, '.cepcenv', package_version, 'download')
            par['pkg_config']['source_dir'] = os.path.join(package_root, package_version)
            par['pkg_config']['install_dir'] = os.path.join(package_root, package_version, 'build')

            safe_mkdir(par['pkg_config']['log_dir'])
            safe_mkdir(par['pkg_config']['download_dir'])
            safe_mkdir(par['pkg_config']['source_dir'])
            safe_mkdir(par['pkg_config']['install_dir'])

        return par

    def execute(self, param):
        f = load_func('cepcenv_handler_run_avoid_conflict.{0}'.format(param['action_handler']), param['action'])
        result = f(param)
        if result and 'log' in result:
            with open(os.path.join(param['pkg_config']['log_dir'], param['action']+'.out'), 'w') as f:
                f.write(result['log']['stdout'])
            with open(os.path.join(param['pkg_config']['log_dir'], param['action']+'.err'), 'w') as f:
                f.write(result['log']['stderr'])
        return None

    def report(self, vertex, result):
        if isinstance(result, Exception):
            print('Vertex {0} finished with exception: {1}'.format(vertex, result))
        else:
            pass
#            print('Vertex {0} finished with result: {1}'.format(vertex, result))

    def deliver(self, vertex, result):
        pass

    def abort(self, vertice):
        pass
