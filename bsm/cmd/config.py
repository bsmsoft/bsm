try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from bsm.cmd import Base
from bsm.cmd import CmdError

class Config(Base):
    def execute(self, config_type='', item_list=[]):
        if not config_type or config_type == 'all':
            return self._bsm.config_all()

        if not item_list:
            return self._bsm.config(config_type)

        current_config = self._bsm.config(config_type)
        current_item = [config_type]
        for item in item_list:
            if not isinstance(current_config, Mapping):
                raise CmdError('Config "{0}" is not a map: {1}'.format(':'.join(current_item), type(current_config)))
            current_item.append(item)
            if item not in current_config:
                raise CmdError('Config "{0}" not found'.format(':'.join(current_item)))
            current_config = current_config[item]

        return current_config
