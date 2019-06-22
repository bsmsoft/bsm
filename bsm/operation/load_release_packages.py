from bsm.config.util import load_packages

from bsm.handler import Handler

from bsm.operation import Base

class LoadReleasePackages(Base):
    def execute(self):
        self._env.unload_packages()

        category_auto_env = [ctg for ctg in self._config['category_priority'] if self._config['category'].get(ctg, {}).get('auto_env')]

        with Handler(self._config['release_path']['handler_python_dir']) as h:
            for package, value in load_packages(h, category_auto_env, self._config['package_runtime']).items():
                category, subdir, version = value
                pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)
                self._env.load_package(pkg_cfg['config'])
