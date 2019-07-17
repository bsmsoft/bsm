from bsm.operation import Base

class LoadPackage(Base):
    def execute(self, package, category, subdir, version):
        pkg_prop = self._prop['packages_runtime'].package_props(
            category, subdir, package, version)['prop']

        self._env.unload_package(package)
        self._env.load_package(pkg_prop)
