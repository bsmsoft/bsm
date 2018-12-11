from bsm.cmd import Base

class Version(Base):
    def execute(self):
        return self._bsm.version()
