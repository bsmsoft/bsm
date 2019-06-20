from bsm.cmd import Base

from bsm.logger import get_logger
_logger = get_logger()

class Default(Base):
    def execute(self):
        return self._bsm.default()
