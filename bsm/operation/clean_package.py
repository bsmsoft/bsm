from bsm.operation import Base

class CleanPackage(Base):
    def execute(self, package):
        self._env.unload_package(package)
