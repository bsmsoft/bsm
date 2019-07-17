from bsm.prop.util import load_packages

from bsm.handler import Handler

from bsm.operation import Base

class LoadReleasePackages(Base):
    def execute(self):
        self._env.unload_packages()

        category_auto_env = [
            ctg for ctg in self._prop['category_priority']
            if self._prop['category'].get(ctg, {}).get('auto_env')]

        with Handler(self._prop['release_path']['handler_python_dir']) as h:
            for package, value in load_packages(
                    h, category_auto_env, self._prop['packages_runtime']).items():
                category, subdir, version = value
                pkg_props = self._prop['packages_runtime'].package_props(
                    category, subdir, package, version)
                self._env.load_package(pkg_props['prop'])
