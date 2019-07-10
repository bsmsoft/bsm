from bsm.cmd import Base

class Bsmcli(Base):
    def execute(self):
        return self._bsm.cli()
