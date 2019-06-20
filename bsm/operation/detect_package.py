from bsm.config.util import detect_package

from bsm.operation import Base

class DetectPackage(Base):
    def execute(self, directory):
        return detect_package(directory, self._config['package_runtime'])
