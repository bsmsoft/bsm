from bsm.operation import Base

class PackageConfig(Base):
    def execute(self, package, category, subdir, version):
        return self._config['package_runtime'].package_config(category, subdir, package, version)
