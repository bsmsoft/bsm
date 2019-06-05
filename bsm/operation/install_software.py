import sys

from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.sequential_processor import SequentialProcessor
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.install.selector import Selector as InstallSelector
from bsm.operation.install.executor import Executor as InstallExecutor
from bsm.operation.install.step import Step

from bsm.config.config_release import ConfigRelease

from bsm.package_manager import PackageManager

from bsm.util import ensure_list

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class Install(Base):
    def execute(self):
        self.__build_dag()
        self.__dag_run()

    def __add_single_package(self, category, package, subdir, version, steps):
        previous_vertex = None
        for step in steps:
            vertex_pkg = (category, package, subdir, version, step['action'], step['sub_action'])
            self.__dag.add_vertex(vertex_pkg)
            if previous_vertex is not None:
                _logger.debug('DAG add edge: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                self.__dag.add_edge(previous_vertex, vertex_pkg)
            previous_vertex = vertex_pkg

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
                            vertex_pkg = (category, package, subdir, version, step['action'], step['sub_action'])
                            self.__dag.add_vertex(vertex_pkg)
                            if previous_vertex is not None:
                                _logger.debug('DAG add edge: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                                self.__dag.add_edge(previous_vertex, vertex_pkg)
                            previous_vertex = vertex_pkg
                        all_steps.setdefault(package, [])
                        all_steps[package].append((category, package, subdir, version))

        # For the package dependencies
        for category in self._config['package_install']:
            for subdir in self._config['package_install'][category]:
                for package in self._config['package_install'][category][subdir]:
                    for version, value in self._config['package_install'][category][subdir][package].items():
                        start_step =
                        start_vertex = (category, package, subdir, version, start_step['action'], start_step['sub_action'])

                        pkg_deps = ensure_list(value['config'].get('dep', []))

                        previous_vertex = None
                        for step in steps:
                            vertex_pkg = (category, package, subdir, version, step['action'], step['sub_action'])
                            self.__dag.add_vertex(vertex_pkg)
                            if previous_vertex is not None:
                                _logger.debug('DAG add edge: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                                self.__dag.add_edge(previous_vertex, vertex_pkg)
                            previous_vertex = vertex_pkg
                        all_steps.setdefault(package, [])
                        all_steps[package].append((category, package, subdir, version))

        # For the package dependencies
        for pkg, pkg_steps in self.__step_info.package_steps_all().items():
            start_step = self.__step_info.find_atomic_start(pkg)
            _logger.debug('start_step: {0} {1}'.format(pkg, start_step))
            if not start_step:
                continue
            start_vertex = (pkg, start_step['action'], start_step['sub_action'])

            pkg_deps = ensure_list(self.__pkg_mgr.package_info(pkg).get('config', {}).get('dep', []))
            for pkg_dep in pkg_deps:
                if pkg_dep not in self.__step_info.package_steps_all():
                    continue
                end_step = self.__step_info.find_atomic_end(pkg_dep)
                _logger.debug('end_step: {0} {1}'.format(pkg_dep, end_step))
                if not end_step:
                    continue
                end_vertex = (pkg_dep, end_step['action'], end_step['sub_action'])

                _logger.debug('DAG add edge: {0} -> {1}'.format(end_vertex, start_vertex))
                self.__dag.add_edge(end_vertex, start_vertex)

    def __dag_run(self):
        selector = InstallSelector(self._config['scenario'], self._config['release'])
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config['scenario'], self._config['release'], self._config['package_install'])

        sys.path.insert(0, self._config['release_path']['handler_python_dir'])
        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
        sys.path.remove(self._config['release_path']['handler_python_dir'])

class InstallOld(object):
    def __build_dag(self):
        self.__dag = Dag()

        all_steps = self.__step_info.package_steps_all()

        # For a single package
        for pkg, pkg_steps in self.__step_info.package_steps_all().items():
            previous_vertex = None

            for step in pkg_steps:
                vertex_pkg = (pkg, step['action'], step['sub_action'])
                self.__dag.add_vertex(vertex_pkg)
                if previous_vertex is not None:
                    _logger.debug('DAG add edge: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                    self.__dag.add_edge(previous_vertex, vertex_pkg)
                previous_vertex = vertex_pkg

        # For the package dependencies
        for pkg, pkg_steps in self.__step_info.package_steps_all().items():
            start_step = self.__step_info.find_atomic_start(pkg)
            _logger.debug('start_step: {0} {1}'.format(pkg, start_step))
            if not start_step:
                continue
            start_vertex = (pkg, start_step['action'], start_step['sub_action'])

            pkg_deps = ensure_list(self.__pkg_mgr.package_info(pkg).get('config', {}).get('dep', []))
            for pkg_dep in pkg_deps:
                if pkg_dep not in self.__step_info.package_steps_all():
                    continue
                end_step = self.__step_info.find_atomic_end(pkg_dep)
                _logger.debug('end_step: {0} {1}'.format(pkg_dep, end_step))
                if not end_step:
                    continue
                end_vertex = (pkg_dep, end_step['action'], end_step['sub_action'])

                _logger.debug('DAG add edge: {0} -> {1}'.format(end_vertex, start_vertex))
                self.__dag.add_edge(end_vertex, start_vertex)
