from bsm.cmd.base import Base

class Home(Base):
    def execute(self):
        return self._bsm.home()
