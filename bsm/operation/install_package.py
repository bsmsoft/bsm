from bsm.paradag import Dag
from bsm.paradag import dag_run
from bsm.paradag.sequential_processor import SequentialProcessor
from bsm.paradag.multi_thread_processor import MultiThreadProcessor

from bsm.operation.util.install.selector import Selector as InstallSelector
from bsm.operation.util.install.executor import Executor as InstallExecutor

from bsm.operation import Base

from bsm.config.util import find_package
from bsm.config.util import package_path

from bsm.util import safe_mkdir
from bsm.util.config import dump_config

from bsm.handler import Handler

from bsm.logger import get_logger
_logger = get_logger()


class InstallPackageError(Exception):
    pass


class InstallPackage(Base):
    def execute(self, package, category=None, subdir=None, version=None, category_origin=None, subdir_origin=None, version_origin=None):
        ctg, sd, ver = self.__find_package(package, category, subdir, version, category_origin, subdir_origin, version_origin)

        self.__build_dag(package, ctg, sd, ver)
        self.__dag_run()

        return ctg, sd, ver

    def __find_package(self, package, category, subdir, version, category_origin, subdir_origin, version_origin):
        category_priority = self._config['category']['priority']
        with Handler(self._config['release_path']['handler_python_dir']) as h:
            ctg, sd, ver = find_package(h, category_priority, self._config['package_runtime'], package, category, subdir, version)
            if ctg and sd and ver:
                _logger.debug('Package config already available for {0}.{1}.{2}.{3}'.format(ctg, sd, package, ver))
                return ctg, sd, ver

            ctg_org, sd_org, ver_org = find_package(h, category_priority, self._config['package_runtime'], package, category_origin, subdir_origin, version_origin)
            if ctg_org and sd_org and ver_org:
                _logger.debug('Package reference found in config_package_runtime: {0}.{1}.{2}.{3}'.format(ctg_org, sd_org, package, ver_org))
                pkg_cfg_origin = self._config['package_runtime'].package_config(ctg_org, sd_org, package, ver_org)['config_origin']
            else:
                _logger.debug('Try to find reference in config_package_install')
                ctg_org, sd_org, ver_org = find_package(h, category_priority, self._config['package_install'], package, category_origin, subdir_origin, version_origin)
                if not ctg_org:
                    raise InstallPackageError('Could not find package reference to install {0}'.format(package))
                _logger.debug('Package reference found in config_package_install: {0}.{1}.{2}.{3}'.format(ctg_org, sd_org, package, ver_org))
                pkg_cfg_origin = self._config['package_install'].package_config(ctg_org, sd_org, package, ver_org)['config_origin']

        ctg = category if category is not None else ctg_org
        sd = subdir if subdir is not None else sd_org
        ver = version if version is not None else ver_org

        pkg_cfg = {}
        pkg_cfg['name'] = package
        pkg_cfg['category'] = ctg
        pkg_cfg['subdir'] = sd
        pkg_cfg['version'] = ver
        pkg_path = package_path(self._config['app'], self._config['category'], pkg_cfg)
        safe_mkdir(pkg_path['config_dir'])
        dump_config(pkg_cfg_origin, pkg_path['config_file'])

        self._config.reset()

        return ctg, sd, ver


    def __build_dag(self, package, category, subdir, version):
        self.__dag = Dag()

        steps = self._config['release_install']['steps']
        pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)

        previous_vertex = None
        for step in steps:
            for sub_step in range(len(pkg_cfg['step'][step])):
                vertex_pkg = (category, subdir, package, version, step, sub_step)
                self.__dag.add_vertex(vertex_pkg)
                if previous_vertex is not None:
                    _logger.debug('DAG add edge for single package: {0} -> {1}'.format(previous_vertex, vertex_pkg))
                    self.__dag.add_edge(previous_vertex, vertex_pkg)
                previous_vertex = vertex_pkg

    def __dag_run(self):
        selector = InstallSelector(self._config)
        processor = MultiThreadProcessor()
        executor = InstallExecutor(self._config, self._env.env_final(), 'runtime')

        with Handler(self._config['release_path']['handler_python_dir']):
            dag_run(self.__dag, selector=selector, processor=processor, executor=executor)
