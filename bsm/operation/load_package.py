from bsm.operation import Base

class LoadPackage(Base):
    def execute(self, package, category, subdir, version):
        pkg_cfg = self._config['package_runtime'].package_config(category, subdir, package, version)['config']

        self._env.unload_package(package)
        self._env.load_package(pkg_cfg)
