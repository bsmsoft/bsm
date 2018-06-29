from bsm.cmd.base import Base

class Version(Base):
    def execute(self):
        return self._bsm.version()
