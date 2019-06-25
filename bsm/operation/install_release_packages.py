import datetime

from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.sequential_processor import SequentialProcessor
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.util.install.selector import Selector as InstallSelector
from bsm.operation.util.install.executor import Executor as InstallExecutor

from bsm.handler import Handler

from bsm.env import Env

from bsm.util import ensure_list
from bsm.util import safe_mkdir

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackageError(Exception):
    pass


class InstallReleasePackages(Base):
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
                                _logger.debug('Dependency for package "{0}" not available: {1}'.format(package, pkg_dep))
                                continue
                            for dep in package_steps[pkg_dep]:
                                dep_end_index = len(self._config['package_install'][dep[0]][dep[1]][dep[2]][dep[3]]['step'][atomic_end]) - 1
                                end_vertex = (dep[0], dep[1], dep[2], dep[3], atomic_end, dep_end_index)

                                _logger.debug('DAG add edge for package dependency: {0} -> {1}'.format(end_vertex, start_vertex))
                                self.__dag.add_edge(end_vertex, start_vertex)

    def __dag_run(self):
        # Get clean environment
        env = Env(initial_env=self._env.env_final(), env_prefix=self._config['app']['env_prefix'])
        env.unload_packages()
        env.unload_release()
        env.unload_app()
        env.load_app(self._config['app'])
        env.load_release(self._config['scenario'], self._config['option'], self._config['release'])

        selector = InstallSelector(self._config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config, env.env_final())

        start_time = datetime.datetime.utcnow()

        with Handler(self._config['release_path']['handler_python_dir']):
            dag_run(self.__dag, selector=selector, processor=processor, executor=executor)

        end_time = datetime.datetime.utcnow()

        self._config['release_status']['install'] = {}
        self._config['release_status']['install']['start'] = start_time
        self._config['release_status']['install']['end'] = end_time
        self._config['release_status']['install']['finished'] = True
        self._config['release_status']['option'] = {}
        for opt in self._config['release_install']['options_to_save']:
            if opt in self._config['option']:
                self._config['release_status']['option'][opt] = self._config['option'][opt]

        safe_mkdir(self._config['release_path']['status_dir'])
        self._config['release_status'].save_to_file(self._config['release_path']['status_file'])
