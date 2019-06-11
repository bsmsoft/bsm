from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Use(Base):
    def execute(self, default=False, without_package=False):
        self._bsm.use(without_package)
        return self._bsm.config('scenario')['version']
