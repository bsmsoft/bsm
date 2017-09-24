import os

from paradag import Dag
from paradag import dag_run

from cepcenv.util import ensure_list

class Use(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

        self.__build_dag()

        self.__prepare_packages()

    def __build_dag(self):
        self.__dag = Dag()

        package_config = self.__release_config.get('package', {})
        attribute_config = self.__release_config.get('attribute', {})

        for pkg, cfg in package_config.items():
            self.__dag.add_vertex(pkg)

        basic_pkgs = []
        for pkg, cfg in attribute_config.items():
            if pkg in package_config:
                if 'basic' in cfg and cfg['basic']:
                    basic_pkgs.append(pkg)

        for pkg in package_config:
            if pkg not in basic_pkgs:
                for bp in basic_pkgs:
                    self.__dag.add_edge(bp, pkg)

            if pkg in attribute_config and 'dep' in attribute_config[pkg]:
                pkgs_dep = ensure_list(attribute_config[pkg]['dep'])
                for pkg_dep in pkgs_dep:
                    self.__dag.add_edge(pkg_dep, pkg)

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

            self.__exe_config[pkg] = exe_config

    def run(self):
        sorted_pkgs = dag_run(self.__dag)

        path = {}
        env = {}

        for pkg in sorted_pkgs:
            if pkg not in self.__release_config['attribute']:
                continue

            PATH_NAME = {'bin': 'PATH', 'lib': 'LD_LIBRARY_PATH', 'man': 'MANPATH', 'info': 'INFOPATH'}
            if 'path' in self.__release_config['attribute'][pkg]:
                for k, v in self.__release_config['attribute'][pkg]['path'].items():
                    if k in PATH_NAME:
                        path_env_name = PATH_NAME[k]
                        if path_env_name not in path:
                            path[path_env_name] = []
                        full_path = v.format(**self.__exe_config[pkg])
                        if full_path not in path[path_env_name]:
                            path[path_env_name].append(full_path)

            if 'env' in self.__release_config['attribute'][pkg]:
                for k, v in self.__release_config['attribute'][pkg]['env'].items():
                    env[k] = v.format(**self.__exe_config[pkg])

        return path, env
