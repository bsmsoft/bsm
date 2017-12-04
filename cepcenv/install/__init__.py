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

from cepcenv.util import ensure_list

from cepcenv.logger import get_logger
_logger = get_logger()


class Install(object):
    def __init__(self, config, config_version):
        self.__config = config
        self.__config_version = config_version

    def run(self):
        install_definition(self.__config_version)
        install_handler(self.__config_version)

        self.__config_release = ConfigRelease(self.__config_version)

        self.__build_dag()
        sys.path.insert(0, self.__config_version.handler_dir)
        self.__dag_run()

    def __build_dag(self):
        self.__dag = Dag()

        package_config = self.__config_release.get('package', {})
        attribute_config = self.__config_release.get('attribute', {})

        for pkg, cfg in package_config.items():
            self.__dag.add_vertex((pkg, 'download'))
            self.__dag.add_vertex((pkg, 'extract'))
            self.__dag.add_vertex((pkg, 'pre_compile'))
            self.__dag.add_vertex((pkg, 'compile'))
            self.__dag.add_vertex((pkg, 'post_compile'))

            self.__dag.add_edge((pkg, 'download'), (pkg, 'extract'))
            self.__dag.add_edge((pkg, 'extract'), (pkg, 'pre_compile'))
            self.__dag.add_edge((pkg, 'pre_compile'), (pkg, 'compile'))
            self.__dag.add_edge((pkg, 'compile'), (pkg, 'post_compile'))

        basic_pkgs = []
        for pkg, cfg in attribute_config.items():
            if pkg in package_config:
                if 'basic' in cfg and cfg['basic']:
                    basic_pkgs.append(pkg)

        for pkg, cfg in package_config.items():
#            category = cfg['category']
#            should_install = False
#            if category in self.__config_release.config['main']['category']['categories']:
#                should_install = self.__config_release.config['main']['category']['categories'][category].get('install', False)

            if pkg not in basic_pkgs:
#                if not should_install:
#                    continue
                for bp in basic_pkgs:
                    self.__dag.add_edge((bp, 'post_compile'), (pkg, 'download'))

            if pkg in attribute_config and 'dep' in attribute_config[pkg]:
#                if not should_install:
#                    continue
                pkgs_dep = ensure_list(attribute_config[pkg]['dep'])
                for pkg_dep in pkgs_dep:
                    self.__dag.add_edge((pkg_dep, 'post_compile'), (pkg, 'pre_compile'))

    def __dag_run(self):
        selector = InstallSelector(self.__config, self.__config_release)
        processor = MultiThreadProcessor()
#        processor = SequentialProcessor()
        executor = InstallExecutor(self.__config, self.__config_version, self.__config_release)

        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
