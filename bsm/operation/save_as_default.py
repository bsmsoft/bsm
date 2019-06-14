from bsm.util import expand_path

from bsm.operation import Base

class SaveAsDefault(Base):
    def execute(self):
        self._config['info']['default'] = {}
        self._config['info']['default']['scenario'] = self._config['entry'].get('scenario')
        self._config['info']['default']['software_root'] = self._config['entry'].get('software_root')
        self._config['info']['default']['option'] = self._config['entry'].get('option', {})

        self._config['info'].save_to_file(expand_path(self._config['app']['config_info_file']))
