from bsm.cmd import Base

class Option(Base):
    def execute(self):
        return self._bsm.option()
