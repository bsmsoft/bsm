from bsm.cmd import Base

class ConfigExample(Base):
    def execute(self, save=False):
        content = self._bsm.config_user_example()
        if not save:
            return content

        config_user_file = self.bsm.config('app')['config_user_file']
        if 'config_user_file' in self['entry']:
            config_user_file = self['entry']['config_user_file']
        return self._bsm.config(config_type)
