from bsm.cmd import Base

class Version(Base):
    def execute(self):
        bsm_version = self._bsm.version()
        app_id = self._bsm.app()
        return '{0} (BSM) version {1}'.format(app_id, bsm_version)
