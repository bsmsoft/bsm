import os

from bsm.operation import Base
from bsm.handler import Handler, HandlerNotFoundError

from bsm.logger import get_logger
_logger = get_logger()

class Option(Base):
    def execute(self):
        handler_dir = None
        if 'handler_dir' in self._config['scenario'].version_path:
            handler_dir = self._config['scenario'].version_path['handler_dir']

        try:
            with Handler(handler_dir) as h:
                _logger.debug('hehehe')
                return h.run('option')
        except HandlerNotFoundError as e:
            _logger.debug('No option loaded: {0}'.format(e))
            return ''
