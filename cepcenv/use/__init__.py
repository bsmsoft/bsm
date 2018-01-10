import os

from paradag import Dag
from paradag import dag_run

from cepcenv.package_manager import PackageManager

from cepcenv.check import Check

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
            if not pkg_info.get('category', {}).get('auto_env'):
                continue
            self.__dag.add_vertex(pkg)

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('auto_env'):
                continue

            pkgs_dep = ensure_list(pkg_info.get('attribute', {}).get('dep', []))
            for pkg_dep in pkgs_dep:
                if not self.__pkg_mgr.package_info(pkg_dep).get('category', {}).get('auto_env'):
                    continue
                self.__dag.add_edge(pkg_dep, pkg)

    def check(self):
        check = Check(self.__config_release, 'runtime')
        missing_pkg, pkg_install_name = check.check()
        return missing_pkg, check.install_cmd, pkg_install_name

    def run(self):
        sorted_pkgs = dag_run(self.__dag)

        software_root = self.__config_version.config['software_root']
        release_version = self.__config_version.config['version']

        env = Env()
        env.clean()
        env.set_release(software_root, release_version)

        global_env = self.__config_release.get('setting', {}).get('global_env', {})
        new_global_env = {}
        for k, v in global_env.items():
            new_global_env[k] = v.format(**self.__config_version.config)
        env.set_global(new_global_env)

        path_usage = self.__config_release.get('setting', {}).get('path_usage', {})
        for pkg in sorted_pkgs:
            pkg_info = self.__pkg_mgr.package_info(pkg)
            env.set_package(path_usage, pkg_info)

        env_change = env.env_change()

        _logger.info('From software root: {0}'.format(software_root))
        _logger.info('Using version: {0}'.format(release_version))
        _logger.info('Current platform: {0}'.format(self.__config_version.config['platform']))

        return env_change
