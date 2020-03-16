from bsm.util import expand_path

from bsm.operation import Base

class SaveAsDefault(Base):
    def execute(self):
        self._prop['info']['default'] = {}
        self._prop['info']['default']['scenario'] = self._prop['entry'].get('scenario')
        self._prop['info']['default']['software_root'] = self._prop['entry'].get('software_root')
        self._prop['info']['default']['option'] = self._prop['entry'].get('option', {})

        self._prop['info'].save_to_file(expand_path(self._prop['app']['bsm_info_file']))
