from bsm.cmd import Base

class Run(Base):
    def execute(self, command):
        return self._bsm.run_release_command(list(command))
