from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class Clean(Base):
    def execute(self):
        self._env.unload_packages()
        self._env.unload_release()
