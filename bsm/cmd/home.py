from bsm.cmd import Base

class Home(Base):
    def execute(self):
        return self._bsm.home()
