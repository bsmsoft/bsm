import sys

from paradag import Dag
from paradag import dag_run
from paradag.sequential_processor import SequentialProcessor
from paradag.multi_thread_processor import MultiThreadProcessor

from cepcenv.install.release import install_definition
from cepcenv.install.release import install_handler

from cepcenv.install.selector import Selector as InstallSelector
from cepcenv.install.executor import Executor as InstallExecutor

from cepcenv.config.config_release import ConfigRelease

from cepcenv.package_manager import PackageManager

from cepcenv.check import Check

from cepcenv.util import ensure_list

from cepcenv.logger import get_logger
_logger = get_logger()


class Install(object):
    def __init__(self, config, config_version, config_release=None, transformers=[]):
        self.__config = config
        self.__config_version = config_version
        self.__config_release = config_release

        if self.__config_release is None:
            install_definition(self.__config_version)
            install_handler(self.__config_version)

            # Must initialize ConfigRelease after install_definition
            self.__config_release = ConfigRelease(self.__config_version)

        for transformer in transformers:
            self.__config_release.transform(transformer)

        self.__pkg_mgr = PackageManager(self.__config_version, self.__config_release)

    def config_release(self):
        return self.__config_release

    def check(self):
        check = Check(self.__config_release, 'install')
        missing_pkg, pkg_install_name = check.check()
        return missing_pkg, check.install_cmd, pkg_install_name

    def package_list(self):
        pkg_list = []
        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('install'):
                continue

            pkg_version = pkg_info['package'].get('version', 'unknown')
            pkg_list.append((pkg, pkg_version, pkg_info['dir']['root']))
        return pkg_list

    def install_packages(self):
        self.__build_dag()

        sys.path.insert(0, self.__config_version.handler_dir)
        self.__dag_run()
        sys.path.remove(self.__config_version.handler_dir)

    def __build_dag(self):
        self.__dag = Dag()

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('install'):
                continue

            self.__dag.add_vertex((pkg, 'download'))
            self.__dag.add_vertex((pkg, 'extract'))
            self.__dag.add_vertex((pkg, 'pre_compile'))
            self.__dag.add_vertex((pkg, 'compile'))
            self.__dag.add_vertex((pkg, 'post_compile'))
            self.__dag.add_vertex((pkg, 'clean'))

            self.__dag.add_edge((pkg, 'download'), (pkg, 'extract'))
            self.__dag.add_edge((pkg, 'extract'), (pkg, 'pre_compile'))
            self.__dag.add_edge((pkg, 'pre_compile'), (pkg, 'compile'))
            self.__dag.add_edge((pkg, 'compile'), (pkg, 'post_compile'))
            self.__dag.add_edge((pkg, 'post_compile'), (pkg, 'clean'))

        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('category', {}).get('install'):
                continue

            pkgs_dep = ensure_list(pkg_info.get('attribute', {}).get('dep', []))
            for pkg_dep in pkgs_dep:
                if not self.__pkg_mgr.package_info(pkg_dep).get('category', {}).get('install'):
                    continue
                self.__dag.add_edge((pkg_dep, 'post_compile'), (pkg, 'pre_compile'))

    def __dag_run(self):
        selector = InstallSelector(self.__config, self.__config_release)
        processor = MultiThreadProcessor()
#        processor = SequentialProcessor()
        executor = InstallExecutor(self.__config, self.__config_version, self.__config_release)

        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
