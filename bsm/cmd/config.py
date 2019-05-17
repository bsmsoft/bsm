from bsm.cmd import Base

class Config(Base):
    def execute(self, config_type='', item_name=''):
        if not config_type or config_type == 'all':
            return self._bsm.config_all()
        if not item_name:
            return self._bsm.config(config_type)
        return self._bsm.config(config_type)[item_name]
