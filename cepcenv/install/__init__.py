from paradag import Dag
from paradag import dag_run
from paradag.multi_thread_processor import MultiThreadProcessor

from cepcenv.install.selector import Selector as InstallSelector
from cepcenv.install.executor import Executor as InstallExecutor

from cepcenv.util import ensure_list


class Install(object):
    def __init__(self, config, release_config):
        self.__config = config
        self.__release_config = release_config

        self.__build_dag()

    def __build_dag(self):
        self.__dag = Dag()

        if 'package' not in self.__release_config:
            return
        package_config = self.__release_config['package']

        for pkg, cfg in package_config.items():
            self.__dag.add_vertex((pkg, 'DOWNLOAD'))
            self.__dag.add_vertex((pkg, 'EXTRACT'))
            self.__dag.add_vertex((pkg, 'PRE_CHECK'))
            self.__dag.add_vertex((pkg, 'INSTALL'))
            self.__dag.add_vertex((pkg, 'POST_CHECK'))

            self.__dag.add_edge((pkg, 'DOWNLOAD'), (pkg, 'EXTRACT'))
            self.__dag.add_edge((pkg, 'EXTRACT'), (pkg, 'PRE_CHECK'))
            self.__dag.add_edge((pkg, 'PRE_CHECK'), (pkg, 'INSTALL'))
            self.__dag.add_edge((pkg, 'INSTALL'), (pkg, 'POST_CHECK'))

        for pkg, cfg in package_config.items():
            if 'dep' in cfg:
                pkgs_dep = ensure_list(cfg['dep'])
                for pkg_dep in pkgs_dep:
                    self.__dag.add_edge((pkg_dep, 'POST_CHECK'), (pkg, 'PRE_CHECK'))

    def run(self):
        selector = InstallSelector(self.__config, self.__release_config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self.__config, self.__release_config)

        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
