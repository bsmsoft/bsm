from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.util.install.selector import Selector as InstallSelector
from bsm.operation.util.install.executor import Executor as InstallExecutor

from bsm.handler import Handler

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackage(Base):
    def execute(self, package, category, subdir, version):
        dag = self.__build_dag(package, category, subdir, version)
        self.__dag_run(dag)

    def __build_dag(self, package, category, subdir, version):
        dag = Dag()

        steps = self._config['release_install']['steps']
        pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)

        previous_vertex = None
        for step in steps:
            for sub_step in range(len(pkg_cfg['step'][step])):
                vertex_pkg = (category, subdir, package, version, step, sub_step)
                dag.add_vertex(vertex_pkg)
                if previous_vertex is not None:
                    _logger.debug('DAG add edge for single package: %s -> %s',
                                  previous_vertex, vertex_pkg)
                    dag.add_edge(previous_vertex, vertex_pkg)
                previous_vertex = vertex_pkg

        return dag

    def __dag_run(self, dag):
        selector = InstallSelector(self._config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config, self._env.env_final(), 'runtime')

        with Handler(self._config['release_path']['handler_python_dir']):
            dag_run(dag, selector=selector, processor=processor, executor=executor)
