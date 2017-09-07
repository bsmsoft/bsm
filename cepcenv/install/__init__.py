import os
import sys

from paradag import Dag
from paradag import dag_run
from paradag.multi_thread_processor import MultiThreadProcessor

from cepcenv.install.selector import Selector as InstallSelector
from cepcenv.install.executor import Executor as InstallExecutor

from cepcenv.config.util import dump_config
from cepcenv.config.release import copy_release_handler

from cepcenv.util import safe_mkdir
from cepcenv.util import ensure_list


class Install(object):
    def __init__(self, config, version_config, release_config):
        self.__config = config
        self.__version_config = version_config
        self.__release_config = release_config

        self.__build_dag()

    def __build_dag(self):
        self.__dag = Dag()

        if 'package' not in self.__release_config:
            return
        package_config = self.__release_config['package']

        for pkg, cfg in package_config.items():
            if cfg['category'] != 'system':
                self.__dag.add_vertex((pkg, 'download'))
                self.__dag.add_vertex((pkg, 'extract'))
                self.__dag.add_vertex((pkg, 'pre_check'))
                self.__dag.add_vertex((pkg, 'install'))
            self.__dag.add_vertex((pkg, 'post_check'))

            if cfg['category'] != 'system':
                self.__dag.add_edge((pkg, 'download'), (pkg, 'extract'))
                self.__dag.add_edge((pkg, 'extract'), (pkg, 'pre_check'))
                self.__dag.add_edge((pkg, 'pre_check'), (pkg, 'install'))
                self.__dag.add_edge((pkg, 'install'), (pkg, 'post_check'))

        for pkg, cfg in package_config.items():
            if 'dep' in cfg:
                pkgs_dep = ensure_list(cfg['dep'])
                for pkg_dep in pkgs_dep:
                    if cfg['category'] != 'system':
                        self.__dag.add_edge((pkg_dep, 'post_check'), (pkg, 'pre_check'))
                    else:
                        self.__dag.add_edge((pkg_dep, 'post_check'), (pkg, 'post_check'))

    def run(self):
        self.__save_release_config()

        sys.path.insert(0, os.path.join(self.__version_config['release_status_root'], 'handler'))
        self.__dag_run()

    def __dag_run(self):
        selector = InstallSelector(self.__config, self.__release_config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self.__config, self.__version_config, self.__release_config)

        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)

    def __save_release_config(self):
        if 'release_status_root' not in self.__version_config:
            raise Exception('release_status_root not found in version_config')

        release_status_root = self.__version_config['release_status_root']
        safe_mkdir(release_status_root)

        dump_config(self.__release_config, os.path.join(release_status_root, 'release.yml'))

        copy_release_handler(self.__version_config, release_status_root)
