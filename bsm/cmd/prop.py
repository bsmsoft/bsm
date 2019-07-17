try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

from bsm.cmd import Base
from bsm.cmd import CmdError

class Prop(Base):
    def execute(self, prop_type, item_list):
        if not prop_type or prop_type == 'all':
            return self._bsm.prop_all()

        if not item_list:
            return self._bsm.prop(prop_type)

        current_prop = self._bsm.prop(prop_type)
        current_item = [prop_type]
        for item in item_list:
            if not isinstance(current_prop, Mapping):
                raise CmdError('Prop "{0}" is not a map: {1}'
                               .format(':'.join(current_item), type(current_prop)))
            current_item.append(item)
            if item not in current_prop:
                raise CmdError('Prop "{0}" not found'
                               .format(':'.join(current_item)))
            current_prop = current_prop[item]

        return current_prop
