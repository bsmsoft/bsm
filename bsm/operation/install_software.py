import sys

from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.sequential_processor import SequentialProcessor
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.util.install.selector import Selector as InstallSelector
#from bsm.operation.util.install.executor import Executor as InstallExecutor

from bsm.util import ensure_list

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallSoftware(Base):
    def execute(self):
        self.__build_dag()
#        self.__dag_run()

    def __build_dag(self):
        self.__dag = Dag()

        all_steps = {}

        # For a single package
        for category in self._config['package_install']:
            for subdir in self._config['package_install'][category]:
                for package in self._config['package_install'][category][subdir]:
                    for version, value in self._config['package_install'][category][subdir][package].items():
                        previous_vertex = None
                        for step in value['step']['steps']:
                            vertex_pkg = (category, subdir, package, version, step['action'], step['sub_action'])
                            self.__dag.add_vertex(vertex_pkg)
                            if previous_vertex is not None:
                                _logger.debug('DAG add edge for single package: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                                self.__dag.add_edge(previous_vertex, vertex_pkg)
                            previous_vertex = vertex_pkg
                        all_steps.setdefault(package, [])
                        all_steps[package].append((category, subdir, package, version))

        # For the package dependencies
        for category in self._config['package_install']:
            for subdir in self._config['package_install'][category]:
                for package in self._config['package_install'][category][subdir]:
                    for version, value in self._config['package_install'][category][subdir][package].items():
                        start_step = value['step']['steps'][value['step']['atomic_start_index']]
                        start_vertex = (category, subdir, package, version, start_step['action'], start_step['sub_action'])

                        pkg_deps = ensure_list(value['config'].get('dep', []))

                        for pkg_dep in pkg_deps:
                            if pkg_dep not in all_steps:
                                continue
                            for dep in all_steps[pkg_dep]:
                                end_step = self._config['package_install'][dep[0]][dep[1]][dep[2]][dep[3]]\
                                        ['step']['steps'][value['step']['atomic_end_index']]
                                end_vertex = (dep[0], dep[1], dep[2], dep[3], end_step['action'], end_step['sub_action'])

                                _logger.debug('DAG add edge for package dependency: {0} -> {1}'.format(end_vertex, start_vertex))
                                self.__dag.add_edge(end_vertex, start_vertex)

    def __dag_run(self):
        selector = InstallSelector(self._config['scenario'], self._config['release'])
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config['scenario'], self._config['release'], self._config['package_install'])

        sys.path.insert(0, self._config['release_path']['handler_python_dir'])
        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
        sys.path.remove(self._config['release_path']['handler_python_dir'])
