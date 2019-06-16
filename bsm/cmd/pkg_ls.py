from bsm.cmd import Base

class PkgLs(Base):
    def execute(self, list_all):
        if list_all:
            return self._bsm.ls_all_package()
        return self._bsm.ls_active_package()
