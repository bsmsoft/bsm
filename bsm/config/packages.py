import os

from bsm.config.common import Common
from bsm.config.package import Package

from bsm.util.config import load_config
from bsm.util.config import dump_config

from bsm.util import safe_mkdir

from bsm.logger import get_logger
_logger = get_logger()


class ConfigPackagesError(Exception):
    pass


class Packages(Common):
    def load_packages(self, config_app, config_release, config_category):
        self.__load_packages(config_release, config_category, config_app['package_work_dir'])
        self.__load_dir_list(config_release)

    def __load_packages(self, config_release, config_category, pkg_work_dir):
        for pkg, pkg_config in config_release.get('package', {}).items():
            category = pkg_config.get('category')
            if category not in config_category:
                _logger.error('Category "{0}" does not exist for package "{1}"'.format(category, pkg))
                continue

            self[pkg] = Package()
            self[pkg].load_package(pkg, pkg_config, config_category[category], pkg_work_dir)

    def __load_dir_list(self, config_release):
        self.__dir_list = {}
        install_path_name = config_release.get('setting', {}).get('path_def', {}).get('install', {})
        for pkg in self:
            if not self[pkg]['category'].get('install'):
                continue
            for k, v in self[pkg]['config'].get('path', {}).items():
                if k not in install_path_name:
                    continue
                path_key = install_path_name[k].format(package=pkg)
                self.__dir_list[path_key] = v.format(**self[pkg]['dir']['location'])


    @property
    def dir_list(self):
        return self.__dir_list
