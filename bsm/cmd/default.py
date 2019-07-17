from bsm.cmd import Base

class Default(Base):
    def execute(self):
        return self._bsm.default()
