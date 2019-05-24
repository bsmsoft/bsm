import os

from bsm.operation import Base

from bsm.logger import get_logger
_logger = get_logger()

class Option(Base):
    def execute(self):
        try:
            return run_handler(self._config['scenario'].version_path['handler_dir'], 'option')
        except Exception as e:
            return ''
