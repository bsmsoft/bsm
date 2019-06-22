from bsm.cmd import Base

class Clean(Base):
    def execute(self):
        self._bsm.clean()
