import sys

from paradag import Dag
from paradag import dag_run
from paradag.sequential_processor import SequentialProcessor
from paradag.multi_thread_processor import MultiThreadProcessor

from bsm.install.selector import Selector as InstallSelector
from bsm.install.executor import Executor as InstallExecutor
from bsm.install.step import Step

from bsm.config.config_release import ConfigRelease

from bsm.package_manager import PackageManager

from bsm.check import Check

from bsm.util import ensure_list

from bsm.logger import get_logger
_logger = get_logger()


class Install(object):
    def __init__(self, config_user, config_version, config_release):
        self.__config_user = config_user
        self.__config_version = config_version
        self.__config_release = config_release

        self.__pkg_mgr = PackageManager(self.__config_version, self.__config_release)

    def check(self):
        check = Check(self.__config_release, 'install')
        missing_pkg, pkg_install_name = check.check()
        return missing_pkg, check.install_cmd, pkg_install_name

    def package_list(self):
        pkg_list = []
        for pkg, pkg_info in self.__pkg_mgr.package_all().items():
            if not pkg_info.get('config_category', {}).get('install'):
                continue

            pkg_version = pkg_info['config'].get('version', 'unknown')
            pkg_list.append((pkg, pkg_version, pkg_info['dir']['root']))
        return pkg_list

    def install_packages(self):
        self.__step_info = Step(self.__config_version, self.__config_release)

        self.__build_dag()

        sys.path.insert(0, self.__config_version.handler_dir)
        self.__dag_run()
        sys.path.remove(self.__config_version.handler_dir)

    def __find_dest_action(self, pkg, steps, dest_start, dest_end):
        start_found = False
        for step in steps:
            if not start_found and step == atomic_start:
                start_found = True
            if start_found and (pkg, step) in self.__dag.vertice():
                return step
            if step == dest_end:
                break
        return ''

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

    def __dag_run(self):
        selector = InstallSelector(self.__config_user, self.__config_version, self.__config_release)
        processor = MultiThreadProcessor()
#        processor = SequentialProcessor()
        executor = InstallExecutor(self.__config_user, self.__config_version, self.__config_release, self.__step_info)

        dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
