from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class InstallPackage(Base):
    def execute(self, category, subdir, version):
        pass
