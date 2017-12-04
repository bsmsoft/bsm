import os

from paradag import Dag
from paradag import dag_run

from cepcenv.package_manager import PackageManager

from cepcenv.env import Env
from cepcenv.util import ensure_list

from cepcenv.logger import get_logger
_logger = get_logger()

class Use(object):
    def __init__(self, config, config_version, config_release):
        self.__config = config
        self.__config_version = config_version
        self.__config_release = config_release

        self.__pkg_mgr = PackageManager(config_version, config_release)

        self.__build_dag()

    def __build_dag(self):
        self.__dag = Dag()

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('set_env'):
                continue
            self.__dag.add_vertex(pkg)

        basic_pkgs = []
        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('set_env'):
                continue
            if pkg_info.get('attribute', {}).get('basic'):
                basic_pkgs.append(pkg)

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('set_env'):
                continue

            if pkg not in basic_pkgs:
                for bp in basic_pkgs:
                    self.__dag.add_edge(bp, pkg)

            pkgs_dep = ensure_list(pkg_info.get('category', {}).get('dep', []))
            for pkg_dep in pkgs_dep:
                self.__dag.add_edge(pkg_dep, pkg)

    def run(self):
        sorted_pkgs = dag_run(self.__dag)

        software_root = self.__config_version.config['software_root']
        release_version = self.__config_version.config['version']

        env = Env()
        env.clean()
        env.set_release(software_root, release_version)

        for pkg in sorted_pkgs:
            if pkg not in self.__config_release.config['attribute']:
                continue

            path_usage = self.__config_release.config['setting'].get('path_usage', {})
            pkg_info = self.__pkg_mgr.package_info(pkg)
            env.set_package(path_usage, pkg_info)

        env_change = env.env_change()

        _logger.info('From software root "{0}"'.format(software_root))
        _logger.info('Using version {0}'.format(release_version))

        return env_change
