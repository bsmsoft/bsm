import os

from paradag import Dag
from paradag import dag_run

from cepcenv.env import Env
from cepcenv.util import ensure_list

class Use(object):
    def __init__(self, config, config_version, config_release):
        self.__config = config
        self.__config_version = config_version
        self.__config_release = config_release

        self.__build_dag()

        self.__prepare_packages()

    def __build_dag(self):
        self.__dag = Dag()

        package_config = self.__config_release.get('package', {})
        attribute_config = self.__config_release.get('attribute', {})

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

            self.__exe_config[pkg] = exe_config

    def run(self):
        sorted_pkgs = dag_run(self.__dag)

        env = Env()
        env.clean()
        env.set_release(self.__config_version.config['software_root'], self.__config_version.config['version'])

        for pkg in sorted_pkgs:
            if pkg not in self.__config_release.config['attribute']:
                continue

            path_mode = self.__config_release.config['main'].get('path_mode', {})
            pkg_config = {
                'name': pkg,
                'package': self.__config_release.config['package'].get(pkg, {}),
                'attribute': self.__config_release.config['attribute'].get(pkg, {}),
                'format': self.__exe_config[pkg],
            }
            env.set_package(path_mode, pkg_config)

        return env.final_all_env()
