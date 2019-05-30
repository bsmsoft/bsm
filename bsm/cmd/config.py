import collections

from bsm.cmd import Base
from bsm.cmd import CmdError

class Config(Base):
    def execute(self, config_type='', item_name=''):
        if not config_type or config_type == 'all':
            return self._bsm.config_all()

        if not item_name:
            return self._bsm.config(config_type)

        if not isinstance(self._bsm.config(config_type), collections.MutableMapping):
            raise CmdError('Config "{0}" is not a dict'.format(config_type))
        if item_name not in self._bsm.config(config_type):
            raise CmdError('Item "{0}" not found in config "{1}"'.format(item_name, config_type))

        return self._bsm.config(config_type)[item_name]
