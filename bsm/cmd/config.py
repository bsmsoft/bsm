from bsm.cmd import Base

class Config(Base):
    def execute(self, config_type=''):
        if not config_type or config_type == 'all':
            return self._bsm.config_all()
        if config_type == 'example':
            return self._bsm.config_user_example()
        return self._bsm.config(config_type)
