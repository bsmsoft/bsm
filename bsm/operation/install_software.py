import sys

from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.sequential_processor import SequentialProcessor
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.util.install.selector import Selector as InstallSelector
from bsm.operation.util.install.executor import Executor as InstallExecutor

from bsm.util import ensure_list

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallSoftware(Base):
    def execute(self):
        self.__build_dag()
        self.__dag_run()

    def __build_dag(self):
        self.__dag = Dag()

        steps = self._config['release_install']['steps']
        atomic_start = self._config['release_install']['atomic_start']
        atomic_end = self._config['release_install']['atomic_end']

        package_steps = {}

        # For a single package
        for category in self._config['package_install']:
            for subdir in self._config['package_install'][category]:
                for package in self._config['package_install'][category][subdir]:
                    for version, value in self._config['package_install'][category][subdir][package].items():
                        previous_vertex = None
                        for step in steps:
                            for sub_step in range(len(value['step'][step])):
                                vertex_pkg = (category, subdir, package, version, step, sub_step)
                                self.__dag.add_vertex(vertex_pkg)
                                if previous_vertex is not None:
                                    _logger.debug('DAG add edge for single package: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                                    self.__dag.add_edge(previous_vertex, vertex_pkg)
                                previous_vertex = vertex_pkg
                        package_steps.setdefault(package, [])
                        package_steps[package].append((category, subdir, package, version))

        # For the package dependencies
        for category in self._config['package_install']:
            for subdir in self._config['package_install'][category]:
                for package in self._config['package_install'][category][subdir]:
                    for version, value in self._config['package_install'][category][subdir][package].items():
                        start_vertex = (category, subdir, package, version, atomic_start, 0)

                        pkg_deps = ensure_list(value['config'].get('dep', []))
                        for pkg_dep in pkg_deps:
                            if pkg_dep not in package_steps:
                                _logger.warn('Dependency for package "{0}" not found: {1}'.format(package, pkg_dep))
                                continue
                            for dep in package_steps[pkg_dep]:
                                dep_end_index = len(self._config['package_install'][dep[0]][dep[1]][dep[2]][dep[3]]['step'][atomic_end]) - 1
                                end_vertex = (dep[0], dep[1], dep[2], dep[3], atomic_end, dep_end_index)

                                _logger.debug('DAG add edge for package dependency: {0} -> {1}'.format(end_vertex, start_vertex))
                                self.__dag.add_edge(end_vertex, start_vertex)

    def __dag_run(self):
        selector = InstallSelector(self._config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config)

        sys.path.insert(0, self._config['release_path']['handler_python_dir'])
        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
        sys.path.remove(self._config['release_path']['handler_python_dir'])
