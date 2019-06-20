from bsm.config.util import check_conflict_package

from bsm.operation import Base

class CheckConflictPackage(Base):
    def execute(self, directory):
        return check_conflict_package(directory, self._config['package_runtime'])
